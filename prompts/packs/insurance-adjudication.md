# Pack: insurance / adjudication  (wave 2)

**Status:** queued. **Tier:** 0. **Repo:** private.

## Why it is a strong candidate to jump the queue

Policy terms, coverage rules, and exclusions are effectively code, and the payout is a
number. Near-deterministic, well-funded buyers, badly served by existing evaluations.

## The task

Given a policy document and a claim, decide coverage and compute the payout: deductible,
co-insurance, limits, sub-limits, exclusions.

## The generator

Encode the policy as executable rules, then generate claims by sampling scenarios. The
correct adjudication is computed, never solved. Sample near exclusion boundaries and limit
thresholds — that is where models fail and where the money is.

## The verifier (tier 0)

- `coverage_decision` — covered / denied
- `payout_correct` — to the penny via `money_equal`
- `exclusions_cited` — the controlling clause identified
- `no_spurious_denial` — denying everything must score near zero

## Red-team

Add a **deny-all** and a **pay-limit** policy. Either scoring means the decision dimension is
underweighted relative to the arithmetic.
