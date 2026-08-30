"""Scoring primitives shared by every pack.

Packs express a verifier as a list of named checks. The framework turns those into a
`Reward` with per-check dimensions, because dimensional credit is what makes a task
trainable rather than merely gradeable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from ef.core.types import Reward, VerifierTier

PENNY = Decimal("0.01")


def money_equal(actual: Decimal | str | float, expected: Decimal | str | float) -> bool:
    """Exact to the penny. Never use float equality on money."""
    return (Decimal(str(actual)) - Decimal(str(expected))).copy_abs() <= PENNY


def within_tolerance(actual: float, expected: float, tolerance: float) -> bool:
    return abs(actual - expected) <= tolerance


@dataclass
class Check:
    """One named, independently scored assertion."""

    name: str
    passed: bool
    weight: float = 1.0
    detail: str = ""

    @property
    def score(self) -> float:
        return 1.0 if self.passed else 0.0


@dataclass
class Checklist:
    """Accumulates checks and folds them into a Reward.

    `pass_threshold` is the score at or above which `Reward.passed` is True. It defaults to
    1.0 because for tier 0 tasks partial credit should shape the gradient without ever being
    reported as success — an almost-balanced ledger is still a wrong ledger.
    """

    tier: VerifierTier = VerifierTier.DETERMINISTIC
    pass_threshold: float = 1.0
    checks: list[Check] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add(self, name: str, passed: bool, weight: float = 1.0, detail: str = "") -> Check:
        check = Check(name=name, passed=passed, weight=weight, detail=detail)
        self.checks.append(check)
        return check

    def note(self, message: str) -> None:
        self.notes.append(message)

    def score(self) -> float:
        total = sum(c.weight for c in self.checks)
        if total == 0:
            return 0.0
        return sum(c.score * c.weight for c in self.checks) / total

    def to_reward(self) -> Reward:
        score = self.score()
        evidence = [
            f"{'PASS' if c.passed else 'FAIL'} {c.name}" + (f" — {c.detail}" if c.detail else "")
            for c in self.checks
        ]
        evidence.extend(self.notes)
        return Reward(
            score=score,
            passed=score >= self.pass_threshold,
            dimensions={c.name: c.score for c in self.checks},
            evidence=evidence,
            tier=self.tier,
        )
