# Pack: accounting / month-end-close  (M1 — the reference implementation)

**Status:** not started. This is the next piece of work.
**Tier:** 0 — deterministic. **Repo:** private (`eval-framework-packs`).

## The task

An agent gets a container with a synthetic company's messy books and one instruction:
reconcile the accounts, post adjusting journal entries, produce a trial balance and
financial statements.

## The generator

Start from a **known-correct set of books**, then inject specific, catalogued errors. Ground
truth is therefore exact and free — we never solve our own puzzle.

Seed data: a Postgres ledger (chart of accounts, journal entries across a period), bank
statements, an invoice register, an FX rate table.

Inject a seeded selection of:

| Error | Shape |
|---|---|
| Duplicated invoice | Same invoice posted twice with different entry ids |
| Transposition | Digits swapped in one leg (e.g. 5,481 → 5,841) |
| Missed accrual | Expense incurred in period, invoice dated after close |
| Misapplied FX rate | Closing rate used where average rate is correct |
| Period cutoff | Revenue recognized one day past period end |
| Unreconciled bank item | Bank line with no matching ledger entry |

Record, in `GroundTruth.payload`, exactly which errors were injected, their entry ids, and
the corrected trial balance.

## The verifier (tier 0)

Dimensions, each independently scored:

- `debits_balance_credits` — the arithmetic identity
- `errors_found` — per-error credit, weighted; found/missed against the injected list
- `no_false_positives` — penalize flagging clean entries. Without this, "flag everything"
  scores well, and that is exactly the kind of degenerate strategy RL will discover.
- `trial_balance_ties` — to the penny, via `money_equal`
- `adjusting_entries_valid` — each posted correction is itself balanced

**No model judge anywhere in the loop.**

## Red-team, beyond the five baselines

Add a **suspense-account policy**: plug the imbalance with one fabricated adjusting entry so
the trial balance ties while none of the actual errors are found. If that scores, the
verifier is weighting arithmetic over diagnosis — which is precisely the mistake that makes
an accounting environment worthless.

## Done when

```bash
uv run ef generate accounting/month-end-close --seed 42
uv run ef run      accounting/month-end-close --seed 42 --agent claude
uv run ef redteam  accounting/month-end-close --seeds 1,2,3    # the gate, on Docker
uv run ef export   accounting/month-end-close --fmt inspect
```

Plus a manual check, once: confirm the injected-error list appears nowhere in the container
filesystem, environment, or git history.

## Constraint

Fully synthetic ledgers. **Never a customer's real books.**
