# Pack: medical / dosing  (wave 1, small)

**Status:** not started. **Tier:** 0–1. **Expert:** MDs. **Repo:** private.

## The task

Given a patient (weight, age, renal function, relevant labs) and a drug, compute the correct
dose, frequency, and any required adjustment.

## Why it is here

Renal and weight-based dosing is arithmetic against structured references. It is a small,
cheap, genuinely tier-0 task that gives the medical pack a deterministic anchor while
`medical/coding` handles the tier-1 work.

## The generator

Sample patient parameters, compute the correct dose from an encoded dosing rule. Include
cases requiring renal adjustment, cases contraindicated outright, and cases where the naive
weight-based calculation is wrong because a cap applies.

## The verifier (tier 0)

- `dose_correct` — numeric, within the clinically defined tolerance (not a float equality)
- `frequency_correct`
- `adjustment_applied` — renal/hepatic adjustment when indicated
- `contraindication_flagged` — refusing to dose when contraindicated must score **full
  credit**, not zero. A verifier that punishes appropriate refusal trains a model to dose
  patients it should not.

## Expert loop

MDs define tolerances and the contraindication set. Encode both; do not leave either to a
judge model.
