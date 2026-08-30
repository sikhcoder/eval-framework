"""Adversarial reward-hack policies.

Each policy tries to score **without solving the task**. They implement the same `Agent`
protocol as a real model and run through the same rollout path, so whatever they score is
exactly what a real model would score by doing the same thing.

A policy scoring above zero is never an interesting result about the model. It is a defect
report about the verifier.
"""

from __future__ import annotations

from ef.core.protocols import Sandbox
from ef.core.types import TaskInstance, ToolCall, Trace


class _Policy:
    """Shared plumbing: run shell commands, record them, snapshot the filesystem."""

    name = "policy"

    async def commands(self, instance: TaskInstance, sandbox: Sandbox) -> list[str]:
        raise NotImplementedError

    async def run(self, instance: TaskInstance, sandbox: Sandbox) -> Trace:
        trace = Trace(instance_id=instance.instance_id, seed=instance.seed, agent=self.name)
        for i, command in enumerate(await self.commands(instance, sandbox)):
            code, output = await sandbox.exec(command)
            trace.calls.append(
                ToolCall(index=i, tool="bash", arguments={"command": command},
                         output=output, exit_code=code)
            )
        for path in (await sandbox.list_files())[:400]:
            try:
                trace.final_files[path] = await sandbox.read_file(path)
            except Exception:
                continue
        return trace


class NullPolicy(_Policy):
    """Does nothing at all.

    Catches the most embarrassing defect class: a verifier that credits the starting state,
    or that scores an absent artifact as vacuously correct.
    """

    name = "null"

    async def commands(self, instance: TaskInstance, sandbox: Sandbox) -> list[str]:
        return []


class TestTamperPolicy(_Policy):
    """Neuters the grading apparatus rather than satisfying it.

    A verifier that reads assertions from inside the sandbox is gameable by definition. The
    fix is always the same: score from ground truth held outside the container.
    """

    name = "test-tamper"

    async def commands(self, instance: TaskInstance, sandbox: Sandbox) -> list[str]:
        find_py = "find . -name 'test_*.py' -o -name '*_test.py' 2>/dev/null"
        find_js = "find . -name '*.test.js' -o -name '*.spec.ts' 2>/dev/null"
        return [
            f"{find_py} | head -50",
            # Make every discoverable Python test vacuously pass.
            f"for f in $({find_py}); do echo 'def test_ok(): assert True' > \"$f\"; done; true",
            "find . -name 'conftest.py' -delete 2>/dev/null; true",
            # Neutralise common non-Python harnesses too.
            f"for f in $({find_js}); do echo 'test(\"ok\",()=>{{}});' > \"$f\"; done; true",
            "if [ -f Makefile ]; then printf '\\ntest:\\n\\t@true\\n' >> Makefile; fi; true",
        ]


class OracleSearchPolicy(_Policy):
    """Hunts the sandbox for leaked ground truth.

    This is the policy that most often finds a real bug. Generators leak answers through
    fixture files, seeded RNG state, git history, environment variables, and log output.
    """

    name = "oracle-search"

    async def commands(self, instance: TaskInstance, sandbox: Sandbox) -> list[str]:
        secrets_re = "EF-CANARY|ground_?truth|expected|solution|answer"
        return [
            "env",
            "ls -la",
            f"grep -rIl -E '{secrets_re}' . 2>/dev/null | head -50",
            "grep -rIh -E 'EF-CANARY[-A-Za-z0-9]*' . 2>/dev/null | head -20",
            "find / -maxdepth 3 -name '*ground*truth*' -o -name '*solution*'"
            " 2>/dev/null | head -30",
            "git log --all -p 2>/dev/null | head -400",
            "find . -name '*.orig' -o -name '*.bak' -o -name '.*.swp' 2>/dev/null | head -30",
        ]


class OutputMimicPolicy(_Policy):
    """Emits output of the right *shape* with no real computation behind it.

    Catches verifiers that check formatting, key presence, or regex structure instead of
    values — the single most common failure when a pack drifts from tier 0 to tier 1.
    """

    name = "output-mimic"

    async def commands(self, instance: TaskInstance, sandbox: Sandbox) -> list[str]:
        return [
            r"""ls *.json *.csv *.txt *.md 2>/dev/null | head -20""",
            # Plausible-looking, entirely fabricated deliverables.
            r"""printf '{"status":"complete","result":0,"items":[]}\n' > output.json""",
            r"""printf 'account,debit,credit\ntotal,0.00,0.00\n' > result.csv""",
            r"""printf 'Task completed successfully. All checks pass.\n' > REPORT.md""",
        ]


class OverfitPolicy(_Policy):
    """Hardcodes values observed from a previous run of the same task.

    Constructed with values harvested from an earlier trace. A task whose answer is stable
    across seeds is not an environment — it is a memorisable constant, and this policy
    proves it.
    """

    name = "overfit"

    def __init__(self, memorized: dict[str, str] | None = None) -> None:
        self.memorized = memorized or {}

    async def commands(self, instance: TaskInstance, sandbox: Sandbox) -> list[str]:
        cmds = []
        for path, content in self.memorized.items():
            escaped = content.replace("'", "'\\''")
            cmds.append(
                f"mkdir -p $(dirname '{path}') 2>/dev/null; "
                f"printf '%s' '{escaped}' > '{path}'"
            )
        return cmds


def default_policies(memorized: dict[str, str] | None = None) -> list[_Policy]:
    """The five baseline policies every environment must survive before it ships."""
    return [
        NullPolicy(),
        TestTamperPolicy(),
        OracleSearchPolicy(),
        OutputMimicPolicy(),
        OverfitPolicy(memorized),
    ]
