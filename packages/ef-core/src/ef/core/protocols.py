"""Structural protocols every domain pack implements.

Adding a domain is implementing three of these: a TaskGenerator, a Verifier, and
(usually) reusing an existing Sandbox backend. Everything else in the framework is shared.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ef.core.types import Reward, TaskInstance, TaskSpec, Trace, VerifierTier


@runtime_checkable
class TaskGenerator(Protocol):
    """Procedurally builds task instances from a seed.

    Implementations must be deterministic in `seed`: the same seed yields byte-identical
    files and ground truth. This is what makes a run reproducible and a leak attributable.

    Implementations must construct ground truth *first* and derive the agent-visible
    material from it — never the reverse. Deriving truth by solving your own puzzle means
    your verifier is only as good as your solver.
    """

    spec: TaskSpec

    def generate(self, seed: int) -> TaskInstance: ...


@runtime_checkable
class Verifier(Protocol):
    """Scores a trace against an instance's ground truth.

    Must never mutate the instance, and must never require network access. A verifier that
    reaches the network is not reproducible and cannot be audited.
    """

    tier: VerifierTier
    """Declared tier. Typed as the enum rather than int so the ladder is enforced statically."""

    def verify(self, instance: TaskInstance, trace: Trace) -> Reward: ...


@runtime_checkable
class Sandbox(Protocol):
    """An isolated world the agent acts in."""

    async def start(self, instance: TaskInstance) -> None: ...

    async def exec(self, command: str, timeout: int = 120) -> tuple[int, str]: ...

    async def read_file(self, path: str) -> str: ...

    async def write_file(self, path: str, content: str) -> None: ...

    async def list_files(self, path: str = ".") -> list[str]: ...

    async def stop(self) -> None: ...


@runtime_checkable
class Agent(Protocol):
    """Anything that can attempt a task inside a sandbox.

    Real models and adversarial reward-hack policies implement the same interface, which is
    what lets the red-team harness reuse the entire rollout path unchanged.
    """

    name: str

    async def run(self, instance: TaskInstance, sandbox: Sandbox) -> Trace: ...
