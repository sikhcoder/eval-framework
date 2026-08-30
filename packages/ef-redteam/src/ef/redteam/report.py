"""The Gameability Report — the artifact that ships with every environment.

Labs spend real compute per environment and cannot currently tell whether a reward signal
is sound. This report is the answer to that: for each adversarial policy, the score it
achieved against our own verifier, across multiple seeds.

The gate is simple and non-negotiable: **every policy must score at or below
`threshold` on every seed.** Anything above it is a verifier defect and blocks shipping.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

from ef.core.protocols import Sandbox, TaskGenerator, Verifier
from ef.redteam.policies import default_policies
from ef.runner.engine import rollout

DEFAULT_THRESHOLD = 0.05


@dataclass
class PolicyResult:
    policy: str
    scores: list[float] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    verifier_errors: list[str] = field(default_factory=list)

    @property
    def max_score(self) -> float:
        return max(self.scores, default=0.0)

    def exploited(self, threshold: float) -> bool:
        return self.max_score > threshold


@dataclass
class GameabilityReport:
    task_id: str
    seeds: list[int]
    threshold: float
    results: list[PolicyResult] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def exploits(self) -> list[PolicyResult]:
        return [r for r in self.results if r.exploited(self.threshold)]

    @property
    def leaks(self) -> list[PolicyResult]:
        """Policies that tripped the ground-truth leak guard — always blocking."""
        return [r for r in self.results if any("LEAK" in e for e in r.verifier_errors)]

    @property
    def passed(self) -> bool:
        return not self.exploits and not self.leaks

    def to_json(self) -> str:
        return json.dumps(asdict(self) | {"passed": self.passed}, indent=2)

    def render(self) -> str:
        lines = [
            f"Gameability Report — {self.task_id}",
            f"seeds={self.seeds} threshold={self.threshold}",
            "",
        ]
        for r in sorted(self.results, key=lambda r: -r.max_score):
            flag = "EXPLOIT" if r.exploited(self.threshold) else "ok"
            lines.append(f"  [{flag:>7}] {r.policy:<14} max_score={r.max_score:.3f}")
            if r.exploited(self.threshold):
                lines.extend(f"             {e}" for e in r.evidence[:5])
        for r in self.leaks:
            lines.append(f"  [   LEAK] {r.policy}: {r.verifier_errors[0][:160]}")
        verdict = "PASS — safe to ship" if self.passed else "FAIL — do not ship"
        lines += ["", f"VERDICT: {verdict}"]
        return "\n".join(lines)


async def run_redteam(
    generator: TaskGenerator,
    verifier: Verifier,
    task_id: str,
    seeds: list[int] | None = None,
    threshold: float = DEFAULT_THRESHOLD,
    memorized: dict[str, str] | None = None,
    sandbox_factory: Callable[[], Sandbox] | None = None,
) -> GameabilityReport:
    """Run every baseline policy across every seed and collect the verdict.

    Multiple seeds matter: a policy that scores zero on one seed and high on another has
    found a generator that is not actually randomizing what it claims to randomize.

    `sandbox_factory` overrides the backend, which lets CI run the gate without a Docker
    daemon. Release gating should still use the real backend the environment ships with.
    """
    seeds = seeds or [1, 2, 3]
    report = GameabilityReport(task_id=task_id, seeds=seeds, threshold=threshold)
    for policy in default_policies(memorized):
        result = PolicyResult(policy=policy.name)
        for seed in seeds:
            outcome = await rollout(
                generator, verifier, policy, seed,
                sandbox=sandbox_factory() if sandbox_factory else None,
            )
            result.scores.append(outcome.reward.score)
            if outcome.reward.score > threshold:
                result.evidence.extend(outcome.reward.evidence[:3])
            if outcome.reward.verifier_error:
                result.verifier_errors.append(outcome.reward.verifier_error)
        report.results.append(result)
    return report
