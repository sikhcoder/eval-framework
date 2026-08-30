# Pack: legal / citation-verify  (wave 1)

**Status:** not started. **Tier:** 1 — structural. **Expert:** lawyer. **Repo:** private.

## Why this task

Hallucinated citations are a famous, measurable failure mode with actual sanctions cases
behind it — and the ground truth is free via CourtListener.

## The task

Given a brief containing citations, identify which do not resolve, which are mis-cited
(wrong reporter, wrong year, wrong court), and which no longer state good law.

## The generator

Start from real, resolvable citations, then inject corruptions: nonexistent reporter volumes,
transposed page numbers, right case with the wrong year, a case whose holding was later
abrogated.

Ground truth is the injected corruption list. As always: corrupt from truth, never solve.

## The verifier (tier 1)

Resolution against a **vendored offline snapshot** of CourtListener/RECAP metadata —
verifiers must never make network calls, or they are neither reproducible nor auditable.

- `nonexistent_flagged` — cites that do not resolve
- `miscited_flagged` — resolves, but metadata disagrees
- `no_false_positives` — valid cites left alone. Essential: "flag everything" must score
  near zero.
- `still_good_law` — subsequent history correct (the tier-1 ceiling here; deeper treatment
  analysis is tier 2 and out of scope)

## Data and provenance

CourtListener and RECAP only. Record source and license for every corpus file. Snapshot and
pin the version — a verifier whose answers change when an upstream database updates is not
reproducible.

## Expert loop

The lawyer defines "still good law" operationally — which subsequent-history flags count,
and how a partial abrogation is treated. That definition is the asset; encode it, do not
leave it to a judge model.
