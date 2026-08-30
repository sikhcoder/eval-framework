# Flagship: MS-DRG grouper replication

> **Given the published CMS specification, write a Medicare MS-DRG grouper from scratch.**

The medical equivalent of GBA Eval. See [FLAGSHIPS.md](FLAGSHIPS.md) for why this shape
matters; this document is the execution plan.

**Status:** not started. Gated on M2 shipping. Phase 0 can run at any time and costs ~$100.

---

## The buyer

**A frontier lab's post-training team.** Not a hospital, not a coding vendor.

This is a *training asset*, not a product — it exists to make a model better at implementing
a large specification faithfully. The domain is almost incidental to why they want it.

That carries an uncomfortable implication: **roughly 20–40 people on Earth can write this
check.** Anthropic, OpenAI, Google DeepMind, Meta, xAI, and the Chinese labs; within each, a
small RL-data or environments team. It is a relationship sale, not a product sale.

**Secondary market:** RCM vendors and healthcare-AI companies would buy this as an *eval*
rather than as training data. Smaller check, much faster sale, and it validates demand.
Worth pursuing in parallel because it de-risks the primary thesis.

---

## Worked example — one claim, one integer

**Input:** 67-year-old male admitted with pneumonia.

| Field | Value |
|---|---|
| Principal diagnosis | `J18.9` — pneumonia, unspecified organism |
| Secondary diagnosis | `J44.1` — COPD with acute exacerbation |
| OR procedure | none |
| Discharge status | home |

**What the grouper does:**

1. Check pre-MDC conditions (transplant, ECMO, tracheostomy) → none
2. Map principal diagnosis to a Major Diagnostic Category → **MDC 04, Respiratory**
3. OR procedure present? No → **medical partition**
4. Base DRG family for simple pneumonia → a three-way split: with MCC / with CC / neither
5. Scan secondary diagnoses for a qualifying complication → `J44.1` counts as a CC
6. **Output: the "with CC" DRG.** One integer.

That integer is worth roughly a thousand dollars of reimbursement difference against the tier
below it. The candidate either produces it or does not.

*(Exact DRG numbers shift annually with the IPPS final rule. The structure is the point.)*

## Why it cannot be bluffed

Step 5 is the whole game.

**A secondary diagnosis does not count as a complication if it is too closely related to the
principal diagnosis.** CMS publishes an exclusion table — thousands of pairwise
relationships. If the principal diagnosis is already respiratory failure, certain respiratory
comorbidities stop counting, because they say nothing new about severity.

You cannot reason your way to that table. You implemented it or you did not.

The **surgical hierarchy** is the same shape: with multiple OR procedures you take the
highest-ranked in a published ordering — not the first, not the most expensive. A model that
"understands DRGs" but skipped the hierarchy produces a plausible integer that is wrong.

This is the GBA Eval property: not "write good code" but **reproduce a specification exactly,
and we will diff you against the reference a million times.**

## What the MDs do

Not grading. **Making the claim generator clinically coherent** — random ICD-10 codes produce
garbage claims that all group to a handful of boring DRGs, and the interesting rules never
fire.

1. **Realistic comorbidity clusters.** Pneumonia with a COPD exacerbation in a 67-year-old is
   a real patient. Pneumonia plus obstetric complications in a 67-year-old male is noise — and
   the grouper's own sex/procedure edits will reject it, so nothing is learned.
2. **Push claims toward the CC/MCC boundary.** The exclusion table is only exercised when a
   secondary diagnosis sits *near* the line. An MD knows which pairs are common enough to
   matter and close enough to be contested.
3. **Name the high-stakes confusions.** Which DRG pairs get audited, appealed, and fought
   over? Those are where a divergence is worth catching.

Without this, you generate a million claims that exercise the same five code paths.

## Licensing — check this first

**MS-DRG grouping uses ICD-10-CM and ICD-10-PCS, not CPT.** CPT is AMA-licensed and would be
a genuine problem; it applies to *outpatient* coding. ICD-10-CM/PCS are published by CDC/CMS
as US government work. So this flagship likely sidesteps the exact licensing gate flagged in
`worksheets/medical-coding.md`. *[verify]*

Still to confirm: distribution terms on the CMS grouper software itself, and whether a
derived corpus can ship inside a customer bundle. That is a week of the lawyer's time and it
gates everything downstream.

---

## Phases

Assume 1–2 engineers plus a few hours a week from an MD.

| Phase | Weeks | Work | Kill condition |
|---|---|---|---|
| **0. Kill-test** | 1–2 | Give a frontier model the spec for **one MDC** and see if it one-shots a working grouper. ~$100 of API. | **Model succeeds → the environment is worthless. Stop.** |
| **1. Oracle** | 2–5 | Get the CMS grouper executing. Produce (claim → DRG) pairs at scale. Lawyer clears licensing in parallel. | Licensing blocks distribution → pivot to the support-guideline flagship |
| **2. Generator** | 5–9 | Claim generator with MD-defined comorbidity clusters, targeting the CC/MCC boundary and surgical hierarchy | Claims cannot reach the interesting paths → corpus is worthless |
| **3. Environment** | 9–13 | Task, verifier, red-team policies, gameability report | Standard ship gate |
| **4. Calibrate & package** | 13–17 | Difficulty band, scale the corpus, bundle | Real-model pass rate must land in 20–70% |

**~4 months to a sellable artifact.** Phase 0 matters most and costs almost nothing — run it
before committing anything else.

### Phase 0 in detail

The cheapest, highest-information step in the whole plan.

1. Pick one MDC with meaningful structure (Respiratory is a reasonable start).
2. Assemble the published spec for that MDC only.
3. Prompt a frontier model at high effort: implement a grouper for this MDC.
4. Diff its output against the reference on a few thousand claims.

**If it scores near 100%, stop and pick another flagship.** An environment a model already
solves teaches nothing and sells for nothing. Better to learn that in week 1 for $100 than
in month 4.

If it scores well on common claims but collapses on the CC/MCC exclusions — the expected
outcome — that gap *is* the environment, and Phase 1 starts.

---

## Odds, stated honestly

| Outcome | Estimate | Reasoning |
|---|---|---|
| Build a technically sound, ungameable environment | **~75%** | Main risks are licensing and one-shotting; both testable cheaply in weeks 1–2 |
| First paid sale within 12 months | **~20–25%** | The technical work is the easy part. ~20–40 possible buyers, all relationship-gated |
| Acquisition outcome in 2–3 years | **~5%** | Honest base rate for a startup built on a specific acquisition thesis |

**The downside is bounded.** Even where no lab buys, the artifact is a working DRG grouper
validation harness — which RCM vendors have real use for. A smaller business, but a business.

## The thing that most changes the odds

**Talk to a buyer before building this, not after.**

The likeliest failure is not technical. It is spending four months on a beautiful environment
and then learning the labs wanted something adjacent — different format, different domain,
already built in-house, or not buying non-coding environments yet at all.

There is something specific to open with right now: a working tier-0 environment, a published
gameability methodology, and in-house MDs and a lawyer. That is a real email. Sending it costs
a day and could redirect four months.
