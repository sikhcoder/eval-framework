"""The ship gate, exercised against the demo pack.

If these fail, the demo pack is gameable and must not be published — which is exactly the
signal the Gameability Report is designed to produce for paying customers.

These run against `LocalSandbox` so CI needs no Docker daemon. Release gating must re-run
the same suite against the real backend the environment ships with.
"""

from __future__ import annotations

import pytest
from ef.core.types import Trace
from ef.redteam.report import run_redteam
from ef.runner.engine import rollout
from ef.sandbox.local import LocalSandbox
from ef_pack_demo import LedgerGenerator, LedgerVerifier

GEN = LedgerGenerator()
VER = LedgerVerifier()

SOLVER_SRC = '''
import csv, json, collections
totals = collections.defaultdict(lambda: [0, 0])
for row in csv.DictReader(open("ledger.csv")):
    eid = int(row["entry_id"])
    totals[eid][0] += round(float(row["debit"]) * 100)
    totals[eid][1] += round(float(row["credit"]) * 100)
debits = sum(v[0] for v in totals.values())
credits = sum(v[1] for v in totals.values())
json.dump(
    {
        "unbalanced_entries": sorted(e for e, v in totals.items() if v[0] != v[1]),
        "total_debits": "%.2f" % (debits / 100),
        "total_credits": "%.2f" % (credits / 100),
    },
    open("corrections.json", "w"),
)
'''


class Solver:
    """A genuine solution, run through the identical path the hack policies use."""

    name = "solver"

    async def run(self, instance, sandbox):
        await sandbox.write_file("solve.py", SOLVER_SRC)
        code, out = await sandbox.exec("python3 solve.py")
        trace = Trace(instance_id=instance.instance_id, seed=instance.seed, agent=self.name)
        if code != 0:
            trace.error = out
            return trace
        for path in await sandbox.list_files():
            try:
                trace.final_files[path] = await sandbox.read_file(path)
            except Exception:
                continue
        return trace


@pytest.mark.asyncio
async def test_all_policies_score_zero():
    """Every baseline reward-hack policy must fail to score. This is the ship gate."""
    report = await run_redteam(
        GEN, VER, "demo/ledger-balance", seeds=[1, 2], sandbox_factory=LocalSandbox
    )
    for result in report.results:
        assert result.max_score <= report.threshold, (
            f"{result.policy} scored {result.max_score}: verifier defect\n"
            + "\n".join(result.evidence)
        )
    assert report.passed
    assert "PASS" in report.render()


@pytest.mark.asyncio
async def test_report_flags_a_deliberately_broken_verifier():
    """The gate must actually catch a gameable verifier, not just rubber-stamp good ones."""

    class Gullible(LedgerVerifier):
        """Credits mere file presence — the classic tier-1 drift failure."""

        def check(self, instance, trace, checklist):
            checklist.add("submitted", "output.json" in trace.final_files)

    report = await run_redteam(
        GEN, Gullible(), "demo/ledger-balance", seeds=[1], sandbox_factory=LocalSandbox
    )
    assert not report.passed
    assert any(r.policy == "output-mimic" for r in report.exploits)
    assert "do not ship" in report.render()


@pytest.mark.asyncio
async def test_solving_agent_scores_one():
    result = await rollout(GEN, VER, Solver(), seed=4, sandbox=LocalSandbox())
    assert result.reward.passed, result.reward.evidence
    assert result.reward.score == 1.0
