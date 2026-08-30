# Pack: tax / computation  (wave 3)

**Status:** queued. **Tier:** 0. **Repo:** private.

## The task

Given a synthetic taxpayer situation, compute the liability: income categorization,
deductions, credits, phase-outs, and the final number.

## Why tier 0

The tax code produces a number. Given the facts, the answer is arithmetic over an encoded
rule set — no judgment required.

## The generator

Encode the rule set for a specific year and filing status, then sample situations. Compute
the liability from the encoding. Sample near phase-out thresholds and AMT boundaries, where
models reliably fail.

Pin the tax year explicitly. A verifier that silently changes answers when rules update is
not reproducible.

## The verifier (tier 0)

- `liability_correct` — to the dollar
- `line_items_correct` — intermediate values, dimensionally scored (a model right on the
  final number by compensating errors should not score the same as one right throughout)
- `credits_applied` — eligible credits claimed, ineligible ones not

## Constraint

Synthetic taxpayers only. Nothing we ship is tax advice.
