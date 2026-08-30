"""Conformance tests for the core protocols.

These are contract tests, not example tests: anything implementing a protocol must satisfy
them, so a new pack inherits real coverage the moment it registers.
"""

from __future__ import annotations

import json

import pytest
from ef.core.protocols import Sandbox, TaskGenerator, Verifier
from ef.core.registry import Registry
from ef.core.types import Reward, TaskInstance, Trace, VerifierTier
from ef.sandbox.local import LocalSandbox
from ef.verify.leak import find_leak
from ef_pack_demo import PACK, LedgerGenerator, LedgerVerifier
from pydantic import ValidationError

GEN = LedgerGenerator()
VER = LedgerVerifier()


def _solved_trace(instance: TaskInstance) -> Trace:
    """A trace representing a perfect solution, built from ground truth."""
    return Trace(
        instance_id=instance.instance_id,
        seed=instance.seed,
        agent="oracle",
        final_files={"corrections.json": json.dumps(instance.ground_truth.payload)},
    )


def test_protocols_are_satisfied():
    assert isinstance(GEN, TaskGenerator)
    assert isinstance(VER, Verifier)
    assert isinstance(LocalSandbox(), Sandbox)


def test_generation_is_deterministic_in_seed():
    a, b = GEN.generate(7), GEN.generate(7)
    assert a.files == b.files
    assert a.ground_truth.payload == b.ground_truth.payload


def test_different_seeds_differ():
    """A task whose answer is constant across seeds is a memorisable constant, not an env."""
    payloads = [json.dumps(GEN.generate(s).ground_truth.payload) for s in range(6)]
    assert len(set(payloads)) > 1


def test_ground_truth_never_serializes():
    instance = GEN.generate(3)
    dumped = instance.model_dump()
    assert "ground_truth" not in dumped
    assert instance.ground_truth.canary not in instance.model_dump_json()


def test_ground_truth_absent_from_sandbox_files():
    instance = GEN.generate(3)
    blob = "\n".join(instance.files.values())
    assert instance.ground_truth.canary not in blob
    for entry_id in instance.ground_truth.payload["unbalanced_entries"]:
        assert f"unbalanced,{entry_id}" not in blob


def test_correct_solution_scores_one():
    instance = GEN.generate(11)
    reward = VER.verify(instance, _solved_trace(instance))
    assert reward.passed
    assert reward.score == pytest.approx(1.0)


def test_empty_trace_scores_zero():
    """The null policy must not be credited for the starting state."""
    instance = GEN.generate(11)
    reward = VER.verify(instance, Trace(instance_id=instance.instance_id, seed=11, agent="null"))
    assert reward.score == 0.0
    assert not reward.passed


def test_plausible_but_wrong_output_scores_low():
    """Right shape, fabricated values — the output-mimic failure mode."""
    instance = GEN.generate(11)
    trace = Trace(
        instance_id=instance.instance_id,
        seed=11,
        agent="mimic",
        final_files={
            "corrections.json": json.dumps(
                {"unbalanced_entries": [], "total_debits": "0.00", "total_credits": "0.00"}
            )
        },
    )
    reward = VER.verify(instance, trace)
    assert not reward.passed
    assert reward.score < 0.5


def test_partial_credit_is_dimensional():
    """Entries right, totals wrong must score strictly between 0 and 1."""
    instance = GEN.generate(11)
    payload = dict(instance.ground_truth.payload) | {"total_debits": "1.00"}
    trace = Trace(
        instance_id=instance.instance_id, seed=11, agent="partial",
        final_files={"corrections.json": json.dumps(payload)},
    )
    reward = VER.verify(instance, trace)
    assert 0.0 < reward.score < 1.0
    assert set(reward.dimensions) == {"submitted", "entries_correct", "totals_correct"}


def test_leak_guard_detects_canary():
    instance = GEN.generate(5)
    trace = Trace(
        instance_id=instance.instance_id, seed=5, agent="oracle-search",
        final_files={"dump.txt": f"found {instance.ground_truth.canary}"},
    )
    assert find_leak(instance, trace) is not None
    reward = VER.verify(instance, trace)
    assert reward.verifier_error is not None
    assert "LEAK" in reward.verifier_error


def test_verifier_crash_is_reported_not_scored_as_failure():
    """A broken verifier must never masquerade as an agent failure."""

    class Boom(LedgerVerifier):
        def check(self, instance, trace, checklist):
            raise ValueError("kaboom")

    instance = GEN.generate(2)
    reward = Boom().verify(instance, _solved_trace(instance))
    assert reward.verifier_error is not None
    assert "kaboom" in reward.verifier_error


def test_registry_resolves_pack():
    registry = Registry()
    registry.register(PACK)
    generator, verifier = registry.resolve("demo/ledger-balance")
    assert generator.spec.id == "demo/ledger-balance"
    assert verifier.tier == VerifierTier.DETERMINISTIC
    assert registry.all_task_ids() == ["demo/ledger-balance"]


def test_registry_rejects_bad_ids():
    registry = Registry()
    registry.register(PACK)
    with pytest.raises(ValueError):
        registry.resolve("no-slash")
    with pytest.raises(KeyError):
        registry.resolve("nope/task")


def test_reward_score_is_bounded():
    """Scores outside [0,1] break downstream aggregation, so the type rejects them."""
    with pytest.raises(ValidationError):
        Reward(score=1.5, passed=True)
    with pytest.raises(ValidationError):
        Reward(score=-0.1, passed=False)


# --- sandbox backend parity -----------------------------------------------------


def _docker_available() -> bool:
    import shutil
    import subprocess

    if shutil.which("docker") is None:
        return False
    return subprocess.run(["docker", "info"], capture_output=True).returncode == 0


requires_docker = pytest.mark.skipif(
    not _docker_available(), reason="docker daemon not available"
)


@requires_docker
@pytest.mark.asyncio
async def test_docker_and_local_agree_on_file_names():
    """Backends must name files identically, or verifiers silently miss under Docker.

    `find .` emits "./x" while LocalSandbox emits "x". That mismatch made every
    `trace.final_files[...]` lookup fail under Docker, so rollouts scored zero and the
    red-team gate passed vacuously — a defeated-looking result from a broken harness.
    """
    from ef.sandbox.docker import DockerSandbox

    instance = GEN.generate(3)
    names = {}
    for label, sandbox in (("local", LocalSandbox()), ("docker", DockerSandbox())):
        try:
            await sandbox.start(instance)
            await sandbox.write_file("corrections.json", "{}")
            names[label] = set(await sandbox.list_files())
        finally:
            await sandbox.stop()

    assert "corrections.json" in names["local"]
    assert "corrections.json" in names["docker"], (
        f"docker returned {sorted(names['docker'])} — path prefix not normalized"
    )
    assert names["local"] == names["docker"]


@requires_docker
@pytest.mark.asyncio
async def test_solver_scores_one_on_docker():
    """A genuine solution must score 1.0 on the REAL backend, not just locally.

    Without this, an all-zero red-team report is indistinguishable from a harness that
    never collected any output.
    """
    from ef.runner.engine import rollout
    from ef.sandbox.docker import DockerSandbox

    from test_redteam import Solver

    result = await rollout(GEN, VER, Solver(), seed=4, sandbox=DockerSandbox())
    assert result.reward.passed, result.reward.evidence
    assert result.reward.score == 1.0
