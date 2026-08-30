"""The rollout engine: generate an instance, run an agent in a sandbox, score the trace.

Every consumer goes through `rollout()` — real evaluations, red-team probes, and
difficulty calibration alike. Sharing one path is what guarantees an adversarial policy is
scored by exactly the same verifier a real model faces.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from ef.core.protocols import Agent, Sandbox, TaskGenerator, Verifier
from ef.core.types import Reward, TaskInstance, Trace
from ef.sandbox import build_sandbox


@dataclass(frozen=True)
class RolloutResult:
    instance: TaskInstance
    trace: Trace
    reward: Reward

    @property
    def summary(self) -> str:
        status = "PASS" if self.reward.passed else "FAIL"
        return f"{status} {self.instance.instance_id} score={self.reward.score:.3f}"


async def rollout(
    generator: TaskGenerator,
    verifier: Verifier,
    agent: Agent,
    seed: int,
    sandbox: Sandbox | None = None,
) -> RolloutResult:
    """Run one full attempt end to end.

    The sandbox is always torn down, including when the agent raises: a leaked container
    holds the generated task material, which is a contamination risk as much as a resource
    leak.
    """
    instance = generator.generate(seed)
    sb = sandbox or build_sandbox(instance.spec.sandbox)
    trace = Trace(instance_id=instance.instance_id, seed=seed, agent=agent.name)
    try:
        await sb.start(instance)
        trace = await agent.run(instance, sb)
    except Exception as exc:
        trace.error = f"{type(exc).__name__}: {exc}"
    finally:
        trace.ended_at = datetime.now(UTC)
        await sb.stop()
    reward = verifier.verify(instance, trace)
    return RolloutResult(instance=instance, trace=trace, reward=reward)
