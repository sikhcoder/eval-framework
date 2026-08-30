# Pack: medical / prior-auth  (wave 3)

**Status:** queued. **Tier:** 1. **Expert:** MDs. **Repo:** private.

## The task

Given a clinical scenario and a published payer policy, decide whether the requested service
meets medical-necessity criteria, and cite the controlling criterion.

## Why tier 1

Published payer policies are explicit criteria lists. The decision is a structured walk
through them, not a clinical judgment call — which is what keeps this out of tier 3.

## The verifier (tier 1)

- `decision_correct` — approve / deny / pend
- `criteria_cited` — the controlling criterion identified
- `missing_documentation_flagged` — correctly identifies what the request lacks
- `no_blanket_denial` — denying everything scores near zero

## Constraint

Published payer policies and synthetic scenarios only. Same PHI rules as `medical/coding`.
