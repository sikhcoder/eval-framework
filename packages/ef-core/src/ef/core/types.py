"""Core data types for eval-framework.

The single most important invariant in this module: **ground truth never reaches the
sandbox**. A verifier can only be trusted if the agent cannot read the answer. Every
type here is designed so that leaking ground truth requires deliberate effort rather
than being the accidental default.
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime
from enum import IntEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class VerifierTier(IntEnum):
    """How a verifier establishes truth. Lower is stronger.

    A pack may not use tier N until it has exhausted tier N-1. Tier 3 never ships alone.
    """

    DETERMINISTIC = 0
    """Exact match, unit tests, balance checks, binary/trace equality."""

    STRUCTURAL = 1
    """Resolves against an authority: a citation exists, a filing validates, a code is legal."""

    REFERENCE_CHAIN = 2
    """A gold document decomposed into independently scored dimensions (RLVRR)."""

    CALIBRATED_JUDGE = 3
    """Model judge. Requires measured human agreement; never the sole signal."""


def new_canary() -> str:
    """Mint a canary string.

    Embedded in ground truth and searched for inside the sandbox by the oracle-search
    red-team policy. If this string is findable by the agent, the environment leaks.
    """
    return f"EF-CANARY-{secrets.token_hex(16)}"


class SandboxSpec(BaseModel):
    """How to build the world the agent acts in."""

    model_config = ConfigDict(frozen=True)

    backend: Literal["docker", "local", "e2b", "modal"] = "docker"
    image: str | None = None
    dockerfile: str | None = None
    setup_script: str | None = None
    workdir: str = "/workspace"
    network: bool = False
    """Default deny. Network access is an exfiltration and contamination vector."""
    cpu_limit: float = 2.0
    memory_mb: int = 4096
    timeout_seconds: int = 3600


class Toolset(BaseModel):
    """What the agent is permitted to do. A narrow action space yields a narrow policy."""

    model_config = ConfigDict(frozen=True)

    bash: bool = True
    read: bool = True
    write: bool = True
    sql: str | None = None
    """DSN of a database the agent may query, if the domain needs one."""
    http_allowlist: tuple[str, ...] = ()
    extra: tuple[str, ...] = ()


class TaskSpec(BaseModel):
    """The static definition of a task, independent of any particular seed."""

    model_config = ConfigDict(frozen=True)

    id: str
    """Stable identifier, `<pack>/<task>` — e.g. `accounting/month-end-close`."""
    domain: str
    instruction: str
    sandbox: SandboxSpec
    tools: Toolset = Field(default_factory=Toolset)
    verifier_tier: VerifierTier
    difficulty: float = Field(default=0.5, ge=0.0, le=1.0)
    holdout: bool = False
    """Holdout tasks are never published and never exported to third parties."""
    tags: tuple[str, ...] = ()


class GroundTruth(BaseModel):
    """The answer. Never serialized into the sandbox; never written to a public artifact.

    `payload` is opaque to the core and interpreted only by the pack's own verifier.
    """

    model_config = ConfigDict(frozen=True)

    canary: str = Field(default_factory=new_canary)
    payload: dict[str, Any]


class TaskInstance(BaseModel):
    """A concrete, seeded instantiation of a TaskSpec.

    `ground_truth` is `exclude=True`, so `model_dump()` and `model_dump_json()` omit it by
    default. Anything written into the sandbox must go through `public_manifest()`.
    """

    model_config = ConfigDict(frozen=True)

    spec: TaskSpec
    seed: int
    files: dict[str, str] = Field(default_factory=dict)
    """Relative path -> contents, materialized into the sandbox workdir."""
    ground_truth: GroundTruth = Field(exclude=True, repr=False)

    @property
    def instance_id(self) -> str:
        return f"{self.spec.id}@{self.seed}"

    def public_manifest(self) -> dict[str, Any]:
        """Exactly what the agent is allowed to see. The only sanctioned path into a sandbox."""
        return {
            "instance_id": self.instance_id,
            "instruction": self.spec.instruction,
            "files": sorted(self.files),
            "tools": self.tools_summary(),
        }

    def tools_summary(self) -> list[str]:
        t = self.spec.tools
        names = [n for n, on in (("bash", t.bash), ("read", t.read), ("write", t.write)) if on]
        if t.sql:
            names.append("sql")
        names.extend(t.extra)
        return names


class ToolCall(BaseModel):
    """One action the agent took, and what came back."""

    model_config = ConfigDict(frozen=True)

    index: int
    tool: str
    arguments: dict[str, Any]
    output: str
    exit_code: int | None = None
    duration_ms: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Trace(BaseModel):
    """The complete record of one rollout. The verifier's only view of what happened."""

    instance_id: str
    seed: int
    agent: str
    calls: list[ToolCall] = Field(default_factory=list)
    final_message: str = ""
    final_files: dict[str, str] = Field(default_factory=dict)
    """Post-rollout filesystem state the verifier cares about."""
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ended_at: datetime | None = None
    error: str | None = None

    @property
    def total_tool_calls(self) -> int:
        return len(self.calls)

    def transcript(self) -> str:
        """Flattened text of everything the agent did. Used by leak scanning."""
        parts = [f"{c.tool} {c.arguments}\n{c.output}" for c in self.calls]
        parts.append(self.final_message)
        return "\n".join(parts)


class Reward(BaseModel):
    """The output of a verifier.

    `dimensions` is required rather than optional: partial, granular credit is what makes
    a task trainable rather than merely gradeable. A single binary scalar gives a sparse
    gradient and teaches the model almost nothing about *why* it failed.
    """

    model_config = ConfigDict(frozen=True)

    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    dimensions: dict[str, float] = Field(default_factory=dict)
    evidence: list[str] = Field(default_factory=list)
    """Human-readable justification. Required for expert adjudication of disagreements."""
    tier: VerifierTier = VerifierTier.DETERMINISTIC
    verifier_error: str | None = None
    """Set when the verifier itself failed. Distinct from the agent scoring zero."""

    @classmethod
    def zero(cls, reason: str, tier: VerifierTier = VerifierTier.DETERMINISTIC) -> Reward:
        return cls(score=0.0, passed=False, evidence=[reason], tier=tier)
