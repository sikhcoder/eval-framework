# Expert review of a verifier

**Goal:** measure verifier-vs-expert agreement, and convert every disagreement into a test.
**Output:** regression tests and a published agreement rate.
**Run before** any tier-1+ pack ships.

## Why it is a gate

The red-team harness proves a verifier cannot be *cheated*. It cannot prove the verifier is
*right*. For tier 0 that gap is small — arithmetic is arithmetic. For tier 1 and above it is
the whole risk, and only a practitioner can close it.

## Procedure

1. **Sample a held-out set.** 30–50 instances the verifier has not been tuned against.
   Tuning against the review set makes the resulting agreement rate meaningless.
2. **Expert scores blind.** They see the task and the agent's output, never the verifier's
   score. Blindness is not optional; anchoring destroys the measurement.
3. **Compare.** Compute agreement, and for graded dimensions report κ, not raw agreement —
   raw agreement is inflated when one outcome dominates.
4. **Triage every disagreement into exactly one bucket:**

| Bucket | Meaning | Action |
|---|---|---|
| Verifier wrong | The encoding is incorrect or incomplete | Fix the verifier. Add a regression test. |
| Expert wrong | Practitioner slip | Add a test asserting the verifier's behavior, with the reasoning recorded |
| Task ambiguous | The instruction admits both readings | **Fix the task**, not the verifier |
| Genuinely contested | Practitioners legitimately disagree | The task is not tier ≤2. Cut it or drop the dimension. |

The last bucket is the one teams talk themselves out of. A task real practitioners disagree
about does not have a verifiable answer, and shipping it means shipping noise as gradient.

5. **Publish the rate.** It goes in the bundle alongside the Gameability Report.

## On what a low rate means

A low agreement rate is a defect signal, not a number to improve by relabeling. Do not
adjust the review set until the number looks better — that is how a verifier ends up
measuring its own assumptions.

## Deliverables

- [ ] Agreement rate and κ per dimension
- [ ] One regression test per disagreement, attributed
- [ ] Buckets tallied — a high "task ambiguous" count means the instruction needs rewriting,
      not the verifier
- [ ] Cut list: dimensions or tasks that fell into "genuinely contested"
