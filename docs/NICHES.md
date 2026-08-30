# Domains

Ordered by **verifier tier**, not by market size. Tier is what determines whether a task can
ship, and it is nearly independent of which industry it belongs to.

## Wave 1 — tier 0/1, in flight

### Accounting / tax

| | |
|---|---|
| **Flagship** | Month-end close: reconcile a messy ledger, post adjusting entries, produce a trial balance |
| **Tier** | 0 — deterministic |
| **Ground truth** | Generator starts from known-correct books and injects specific errors (duplicated invoice, transposition, missed accrual, misapplied FX rate, period cutoff). Truth is exact and free. |
| **Data** | Fully synthetic. **Never a customer's real books.** |
| **Buyer** | Labs; downstream, Intuit / Big Four / enterprise finance |
| **Why first** | A tier-0 verifier lets us debug the machinery without also debating what a correct answer is |

Also here: tax computation (the code yields a number), reconciliations, consolidation, FX
translation, and lease/revenue-recognition schedules.

### Legal

| | |
|---|---|
| **Flagship** | Docket deadline computation — given jurisdiction, trigger event, and service method, compute the date |
| **Tier** | **0.** FRCP Rule 6 plus local rules, court holidays, and service-method extensions produce exactly one date |
| **Secondary** | Citation verification (tier 1): does the cite resolve, and is it still good law? |
| **Ground truth** | Rule encodings validated by our lawyer; CourtListener / RECAP for citations |
| **Data** | CourtListener, RECAP, public dockets, EDGAR. **Never scrape Westlaw or Lexis — hard line.** Rule text is generally public; headnotes and editorial content are not. |
| **Constraint** | Nothing we ship is framed as legal advice. Lawyer reviews every corpus before ingestion. |

Deadline computation is the sleeper: it is genuinely deterministic, genuinely hard for
models (they conflate calendar and court days, miss holiday rules, misapply the mailbox
rule), commercially real, and nobody has built it as an RL environment.

Hallucinated citations are the other standout — a famous, measurable failure mode with
actual sanctions cases behind it, and free ground truth via CourtListener.

### Medical

| | |
|---|---|
| **Flagship** | ICD-10 / CPT / DRG coding from a clinical note |
| **Tier** | 1 — structural. The CMS DRG grouper is a published deterministic algorithm; NCCI edits and LCD/NCD policies are explicit rules. |
| **Secondary** | Renal and weight-based dosing (tier 0–1): arithmetic against structured references |
| **Ground truth** | Official code sets and grouper logic; MDs validate |
| **Data** | Synthetic first (Synthea). MIMIC **only** under its DUA. |
| **Buyer** | Labs; downstream, revenue-cycle management — a large and badly served market |

**Compliance, gating and non-negotiable:** no real PHI. Our MDs must not use identifiable
patient material from their own practices — the single easiest way to turn a clean synthetic
dataset into a HIPAA problem. Evals are not medical devices, but efficacy claims can be
regulated: no clinical-outcome marketing.

### Software engineering

| | |
|---|---|
| **Flagship** | Replication training — implement to spec, diff behavior against a reference implementation |
| **Tier** | 0 — the reference's own test suite and I/O pairs are the verifier |
| **Why included** | Verifier cost is near zero, and it is the category buyers already understand |
| **Caveat** | The most contested domain. This is a credibility play, not the revenue play. |

## Wave 2 — tier 0, queued

**Insurance claims adjudication.** Policy terms, coverage rules, and exclusions are
effectively code; the payout is a number. Near-deterministic, well-funded buyers, badly
served. Strong candidate to jump the queue.

**Security / SOC.** CTF-shaped tasks with binary success: the flag is captured or it is not,
the vulnerability is patched or it is not. Deterministic by construction.

## Wave 3 — tier 2, deliberately deferred

**Contract review against a playbook.** Decompose a gold redline into a scored reward chain.
Real revenue, but it spends scarce expert time on subjectivity.

**Clinical reasoning / differential diagnosis.** Same shape, same reason to wait.

**Deferring these is a discipline, not a capability gap.** Tier-2 work is where verifier
quality quietly collapses, and it should start only once the tier-0/1 wins are banked and
the red-team gate has proven itself.

## Cross-cutting constraints

**Contamination control.** Holdout tasks are never published. Canary strings are embedded in
ground truth. Per-buyer task variants make any leak attributable. A benchmark that leaks
into a training set is worthless to every future buyer, so this is an asset-protection
measure, not a formality.

**Corpus provenance.** Every file under `references/` records its source, license, and DUA
status. Having a lawyer in-house means this is a same-week review rather than a quarter-long
blocker — use it early. It gates wave 1, not wave 3.
