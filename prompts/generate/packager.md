# Packager

**Goal:** assemble a customer-ready environment bundle.

## Contents

1. **Container spec and generator** — seeded, reproducible, pinned
2. **Verifier** — with dimensional scoring
3. **Gameability Report** — the differentiator (see below)
4. **Exporters** — Inspect AI today
5. **Holdout split** — private, canary-stamped, per-buyer variants
6. **Difficulty stats** — pass rate for a real model
7. **Provenance manifest** — source and license for every reference file

## Pre-flight — all must hold

- [ ] Red-team passes on the **real** backend, ≥3 seeds (`--sandbox local` is not acceptable
      for release; isolation differences change what a policy can reach)
- [ ] **A genuine solver scores 1.0 on the real backend.** Non-negotiable: an all-zero
      red-team report is indistinguishable from a harness that never collected any output
- [ ] Domain-specific adversaries defeated, not just the five baselines
- [ ] Difficulty in the useful band
- [ ] Tier 1+: expert agreement rate measured and published
- [ ] Provenance clean, lawyer signed off
- [ ] Holdout tasks excluded from everything shipped
- [ ] Per-buyer seed range allocated and recorded privately

## The Gameability Report is the point

Everyone else sells tasks. We sell tasks with evidence the reward signal survives
adversarial pressure.

Include the exploits that were found **and fixed**, with patches referenced. A report with
no history of caught exploits does not read as a clean environment — it reads as a harness
that was never run. The credibility comes from the catches.

## Contamination control

Per-buyer seed ranges make any leak attributable. Canaries are embedded in ground truth.
Holdout tasks are never published, never exported, never in a demo.

A benchmark that leaks into a training set is worthless to every future buyer. This protects
the asset, not just the relationship.
