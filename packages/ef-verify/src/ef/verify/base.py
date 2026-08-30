"""Base class packs subclass to get leak-guarding and error containment for free."""

from __future__ import annotations

import traceback
from abc import ABC, abstractmethod

from ef.core.types import Reward, TaskInstance, Trace, VerifierTier
from ef.verify.leak import leak_guard
from ef.verify.scoring import Checklist


class BaseVerifier(ABC):
    """Implement `check()`; the template handles leaks and verifier crashes.

    A crashing verifier must never be silently scored as an agent failure — that would
    quietly poison a training run with false negatives. It is reported as `verifier_error`.
    """

    tier: VerifierTier = VerifierTier.DETERMINISTIC

    @abstractmethod
    def check(self, instance: TaskInstance, trace: Trace, checklist: Checklist) -> None:
        """Populate `checklist` with named checks. Raise nothing you can help."""

    def verify(self, instance: TaskInstance, trace: Trace) -> Reward:
        if (leaked := leak_guard(instance, trace, self.tier)) is not None:
            return leaked
        if trace.error:
            return Reward.zero(f"rollout failed: {trace.error}", self.tier)
        checklist = Checklist(tier=self.tier)
        try:
            self.check(instance, trace, checklist)
        except Exception:
            return Reward(
                score=0.0,
                passed=False,
                evidence=["verifier raised"],
                tier=self.tier,
                verifier_error=traceback.format_exc(limit=5),
            )
        return checklist.to_reward()
