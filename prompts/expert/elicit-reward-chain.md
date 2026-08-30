# Elicit a reward chain (tier 2)

**Goal:** decompose a gold document into independently scored, checkable dimensions.
**Output:** a weighted rubric where each dimension is programmatically evaluable.
**Use only** when tiers 0 and 1 are genuinely exhausted — see `docs/VERIFIERS.md`.

## The idea

Rather than grading a document holistically (which requires a judge model, and is tier 3),
extract from a **gold reference** the specific, checkable properties that make it correct.
Score each independently.

This is the RLVRR approach: partial, granular reward across measurable dimensions instead of
one subjective verdict.

## Session structure

### 1. Get a gold document
A real, high-quality example of the output. One the expert would sign.

### 2. Ask what makes it correct
Not "is it good" — *what specifically would be wrong if it were absent or different?*

Push until each answer is a property, not an impression. "Well-reasoned" is an impression.
"Addresses the statute of limitations defense" is a property.

### 3. Classify each property by checkability

| Class | Example | Verdict |
|---|---|---|
| Deterministic | Required section present; date correct; party names consistent | Keep — this is tier 0 hiding inside tier 2 |
| Structural | Every cited case resolves; every claim traces to a record fact | Keep — tier 1 |
| Semantic | The counterargument is actually addressed | Keep only if reducible to a checkable proxy |
| Stylistic | Reads persuasively | **Drop.** Not verifiable, not worth the gradient. |

Most of what an expert first calls "judgment" turns out to be tier 0 or 1 once decomposed.
That reclassification is the main value of the session.

### 4. Weight the dimensions
Ask: *"If a draft got this one thing wrong but everything else right, how bad is it?"*
Weights come from consequence, not from how hard the property was to check.

### 5. Find the degenerate strategy
Ask: *"What would a document look like that satisfies every one of these and is still bad?"*

If the expert can describe one easily, the chain is incomplete. Iterate. This question is the
tier-2 equivalent of the red-team gate, and skipping it is how reward chains rot.

## Deliverables

- [ ] `chains/<task>.py` — dimensions, weights, and per-dimension checkers
- [ ] The gold document, with provenance recorded
- [ ] At least one worked negative example from step 5
- [ ] Any dimension needing a judge model flagged explicitly as tier 3, with a plan to
      measure human agreement

## Hard rule

No tier-3 dimension may be the sole contributor to a score, and any tier-3 dimension must
publish its human agreement rate. An unaudited judge model is a plausible-sounding random
number generator.
