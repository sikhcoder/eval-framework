"""Public demo pack: a tier-0 ledger-balancing task.

This exists to prove the plugin API end to end and to serve as the reference pattern every
proprietary pack copies. It is deliberately small, but it is not a toy in the ways that
matter: ground truth is constructed first and never enters the sandbox, scoring is exact,
and it survives the full red-team suite.
"""

from __future__ import annotations

import json
import random
from decimal import Decimal

from ef.core.registry import Pack
from ef.core.types import (
    GroundTruth,
    SandboxSpec,
    TaskInstance,
    TaskSpec,
    Toolset,
    Trace,
    VerifierTier,
)
from ef.verify.base import BaseVerifier
from ef.verify.scoring import Checklist, money_equal

ACCOUNTS = ["cash", "accounts_receivable", "inventory", "accounts_payable", "revenue", "expenses"]

INSTRUCTION = """\
`ledger.csv` contains journal entries with columns: entry_id, account, debit, credit.

Every entry must balance: its debits must equal its credits. Some entries do not.

Find every unbalanced entry and write `corrections.json` in the working directory:

{
  "unbalanced_entries": [<entry_id>, ...],
  "total_debits": "<sum of all debit values, 2dp>",
  "total_credits": "<sum of all credit values, 2dp>"
}

Report entry ids as integers, sorted ascending. Report totals as strings with two decimals.
"""

SPEC = TaskSpec(
    id="demo/ledger-balance",
    domain="accounting",
    instruction=INSTRUCTION,
    sandbox=SandboxSpec(backend="docker", image="python:3.12-slim", network=False),
    tools=Toolset(bash=True, read=True, write=True),
    verifier_tier=VerifierTier.DETERMINISTIC,
    difficulty=0.2,
    tags=("tier0", "demo", "accounting"),
)


class LedgerGenerator:
    """Builds a ledger from known-correct books, then injects specific imbalances.

    Ground truth is constructed *first* and the agent-visible CSV derived from it. Deriving
    truth the other way — by solving our own puzzle — would make the verifier only as
    trustworthy as the solver, which is the mistake that produces gameable environments.
    """

    spec = SPEC

    def __init__(self, n_entries: int = 24, n_broken: int = 4) -> None:
        self.n_entries = n_entries
        self.n_broken = n_broken

    def generate(self, seed: int) -> TaskInstance:
        rng = random.Random(seed)
        rows: list[tuple[int, str, Decimal, Decimal]] = []
        broken: list[int] = []

        broken_ids = sorted(rng.sample(range(1, self.n_entries + 1), self.n_broken))
        for entry_id in range(1, self.n_entries + 1):
            amount = Decimal(rng.randrange(10_00, 500_00)) / 100
            debit_account = rng.choice(ACCOUNTS)
            credit_account = rng.choice([a for a in ACCOUNTS if a != debit_account])
            credit_amount = amount
            if entry_id in broken_ids:
                # A transposition-style error: the credit leg is off by a real amount.
                skew = Decimal(rng.randrange(1_00, 50_00)) / 100
                credit_amount = amount + (skew if rng.random() < 0.5 else -skew)
                if credit_amount <= 0:
                    credit_amount = amount + skew
                broken.append(entry_id)
            rows.append((entry_id, debit_account, amount, Decimal("0.00")))
            rows.append((entry_id, credit_account, Decimal("0.00"), credit_amount))

        total_debits = sum((r[2] for r in rows), Decimal("0.00"))
        total_credits = sum((r[3] for r in rows), Decimal("0.00"))

        lines = ["entry_id,account,debit,credit"]
        lines += [f"{r[0]},{r[1]},{r[2]:.2f},{r[3]:.2f}" for r in rows]

        return TaskInstance(
            spec=self.spec,
            seed=seed,
            files={"ledger.csv": "\n".join(lines) + "\n"},
            ground_truth=GroundTruth(
                payload={
                    "unbalanced_entries": sorted(broken),
                    "total_debits": f"{total_debits:.2f}",
                    "total_credits": f"{total_credits:.2f}",
                }
            ),
        )


class LedgerVerifier(BaseVerifier):
    """Scores `corrections.json` against ground truth held outside the sandbox.

    Three independent dimensions rather than one boolean: a run that finds every broken
    entry but fluffs a total is genuinely more correct than one that finds nothing, and the
    gradient should say so.
    """

    tier = VerifierTier.DETERMINISTIC

    def check(self, instance: TaskInstance, trace: Trace, checklist: Checklist) -> None:
        truth = instance.ground_truth.payload
        raw = trace.final_files.get("corrections.json")
        if raw is None:
            checklist.add("submitted", False, weight=1.0, detail="corrections.json not written")
            checklist.add("entries_correct", False)
            checklist.add("totals_correct", False)
            return
        checklist.add("submitted", True)

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            checklist.add("entries_correct", False, detail=f"invalid JSON: {exc}")
            checklist.add("totals_correct", False)
            return

        claimed = parsed.get("unbalanced_entries")
        expected = truth["unbalanced_entries"]
        entries_ok = isinstance(claimed, list) and sorted(claimed) == expected
        checklist.add(
            "entries_correct",
            entries_ok,
            weight=2.0,
            detail=f"expected {expected}, got {claimed}",
        )

        try:
            totals_ok = money_equal(
                parsed.get("total_debits", "nan"), truth["total_debits"]
            ) and money_equal(parsed.get("total_credits", "nan"), truth["total_credits"])
        except Exception:
            totals_ok = False
        checklist.add("totals_correct", totals_ok, detail="totals must match to the penny")


PACK = Pack(
    name="demo",
    generators={"ledger-balance": LedgerGenerator()},
    verifiers={"ledger-balance": LedgerVerifier()},
)
