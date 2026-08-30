"""The `ef` command line.

Commands map one-to-one onto the lifecycle of an environment:
generate -> run -> verify -> redteam -> export. `redteam` is the gate: an environment that
does not pass it does not ship, regardless of how good it looks.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer
from ef.core.registry import REGISTRY
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    add_completion=False,
    help="eval-framework — build and verify RL environments for agentic AI.",
)
console = Console()

RUNS_DIR = Path("runs")


@app.command("list")
def list_tasks() -> None:
    """List every task exposed by installed packs."""
    ids = REGISTRY.all_task_ids()
    if not ids:
        console.print("[yellow]No packs installed.[/] Install a pack, e.g. `uv sync --extra demo`.")
        raise typer.Exit(0)
    table = Table("task", "tier", "domain", title="Installed tasks")
    for task_id in ids:
        generator, _ = REGISTRY.resolve(task_id)
        spec = generator.spec
        table.add_row(task_id, f"T{int(spec.verifier_tier)}", spec.domain)
    console.print(table)


@app.command()
def generate(task_id: str, seed: int = 42, out: Path | None = None) -> None:
    """Materialize a task instance. Ground truth is never written to disk here."""
    generator, _ = REGISTRY.resolve(task_id)
    instance = generator.generate(seed)
    manifest = instance.public_manifest()
    if out:
        out.mkdir(parents=True, exist_ok=True)
        for rel, content in instance.files.items():
            target = out / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
        console.print(f"[green]Wrote[/] {len(instance.files)} files to {out}")
    console.print_json(json.dumps(manifest))


@app.command()
def run(task_id: str, seed: int = 42, agent: str = "claude", model: str = "claude-opus-5",
        sandbox: str = "spec") -> None:
    """Run one rollout and score it."""
    from ef.runner.agents import ClaudeAgent, ScriptedAgent
    from ef.runner.engine import rollout
    from ef.sandbox.local import LocalSandbox

    generator, verifier = REGISTRY.resolve(task_id)
    runner = ClaudeAgent(model=model) if agent == "claude" else ScriptedAgent([], name=agent)
    result = asyncio.run(
        rollout(generator, verifier, runner, seed,
                sandbox=LocalSandbox() if sandbox == "local" else None)
    )

    RUNS_DIR.mkdir(exist_ok=True)
    slug = task_id.replace("/", "_")
    (RUNS_DIR / f"{slug}_{seed}.json").write_text(
        json.dumps(
            {"trace": result.trace.model_dump(mode="json"),
             "reward": result.reward.model_dump(mode="json")},
            indent=2,
        )
    )
    console.print(result.summary)
    for line in result.reward.evidence:
        console.print(f"  {line}")
    if result.reward.verifier_error:
        console.print(f"[red]VERIFIER ERROR[/] {result.reward.verifier_error}")
        raise typer.Exit(2)


@app.command()
def redteam(task_id: str, seeds: str = "1,2,3", threshold: float = 0.05,
            out: Path | None = None, sandbox: str = "spec") -> None:
    """Run every reward-hack policy. THIS IS THE SHIP GATE.

    Exits non-zero if any policy scored above threshold — that is a verifier defect, and
    finding it is the thing we sell.

    `--sandbox local` runs without a Docker daemon for fast iteration. Release gating must
    use the real backend, since isolation differences change what a policy can reach.
    """
    from ef.redteam.report import run_redteam
    from ef.sandbox.local import LocalSandbox

    generator, verifier = REGISTRY.resolve(task_id)
    seed_list = [int(s) for s in seeds.split(",")]
    factory = LocalSandbox if sandbox == "local" else None
    if factory is not None:
        console.print("[yellow]Running against LocalSandbox — not valid for release gating.[/]")
    report = asyncio.run(
        run_redteam(generator, verifier, task_id, seed_list, threshold, sandbox_factory=factory)
    )
    console.print(report.render())
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report.to_json())
    if not report.passed:
        raise typer.Exit(1)


@app.command("export")
def export_task(task_id: str, fmt: str = "inspect", seed: int = 42,
                out: Path | None = None) -> None:
    """Export a task to a third-party harness format."""
    from ef.export import FORMATS
    from ef.export.inspect_ai import export_inspect

    if fmt not in FORMATS:
        console.print(f"[red]Unknown format[/] {fmt!r}; known: {', '.join(FORMATS)}")
        raise typer.Exit(2)
    generator, _ = REGISTRY.resolve(task_id)
    rendered = export_inspect(generator.generate(seed))
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered)
        console.print(f"[green]Wrote[/] {out}")
    else:
        console.print(rendered)


if __name__ == "__main__":
    app()
