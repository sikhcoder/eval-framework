# Pack: medical / coding  (wave 1)

**Status:** not started. **Tier:** 1 — structural. **Expert:** MDs. **Repo:** private.

## The task

Given a clinical note, assign ICD-10 diagnosis codes, CPT procedure codes, and the resulting
DRG.

## Why it is verifiable

The CMS DRG grouper is a **published deterministic algorithm**. NCCI edits and LCD/NCD
policies are explicit rules. Given a correct code set, the DRG follows mechanically — which
puts most of this task at tier 1 rather than tier 3, where "medical AI evaluation" usually
lands.

## The generator

Synthetic notes (Synthea as the base) generated **from** a chosen code set, not labeled
afterwards. Choose the diagnoses and procedures first, render a plausible note, and the code
set is ground truth by construction.

Vary difficulty via comorbidities affecting DRG assignment, documentation ambiguity, and
codes that NCCI edits forbid bundling.

## The verifier (tier 1)

- `icd10_correct` — set comparison with partial credit; specificity matters (a 3-character
  code where a 5-character one is documented is wrong, not partially right)
- `cpt_correct` — same
- `ncci_compliant` — no forbidden bundles
- `drg_correct` — run the grouper; deterministic
- `no_upcoding` — **penalize codes not supported by the note**

That last dimension is not optional. Upcoding is the exact behavior RL will discover if
reward tracks reimbursement, and a verifier that rewards it is worse than useless — it would
be training a model to commit billing fraud.

## Red-team, beyond the baselines

Add a **max-reimbursement policy** that always emits the highest-paying code set consistent
with the note's surface features. If it scores, `no_upcoding` is underweighted.

## Compliance — gating, non-negotiable

- No real PHI. Synthetic first; MIMIC **only** under its DUA.
- **Our MDs must not use identifiable patient material from their own practices.** This is
  the single easiest way to turn a clean synthetic dataset into a HIPAA problem.
- Evals are not medical devices, but efficacy claims can be regulated. No clinical-outcome
  marketing.

## Expert loop

MDs validate coding correctness on a held-out sample. Disagreements become regression tests.
Publish the agreement rate.
