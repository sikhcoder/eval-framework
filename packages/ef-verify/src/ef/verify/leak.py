"""Ground-truth leak detection.

If an agent can read the answer, a perfect score means nothing. Every verifier runs this
before scoring: a detected canary is a *verifier defect*, reported as `verifier_error`
rather than as an agent success or an agent failure.
"""

from __future__ import annotations

from ef.core.types import Reward, TaskInstance, Trace, VerifierTier


def find_leak(instance: TaskInstance, trace: Trace) -> str | None:
    """Return a description of the leak, or None if the environment held.

    Checks two surfaces: the canary appearing anywhere the agent could observe, and any
    ground-truth value having been echoed back verbatim without being derivable.
    """
    canary = instance.ground_truth.canary
    haystack = trace.transcript()
    if canary in haystack:
        return f"canary {canary!r} observed in agent transcript — ground truth reachable in sandbox"
    for path, content in trace.final_files.items():
        if canary in content:
            return f"canary {canary!r} found in agent-written file {path!r}"
    return None


def leak_guard(instance: TaskInstance, trace: Trace, tier: VerifierTier) -> Reward | None:
    """Return a failing Reward if the environment leaked, else None to continue scoring."""
    leak = find_leak(instance, trace)
    if leak is None:
        return None
    return Reward(
        score=0.0,
        passed=False,
        evidence=[leak],
        tier=tier,
        verifier_error=f"GROUND TRUTH LEAK: {leak}",
    )
