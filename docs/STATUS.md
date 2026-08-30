# Status

Living log of progress, decisions, and open questions. **Update this at the end of every
working session** — it is the handoff artifact between sessions and between people.

Last updated: **2026-08-30** (M2 landed)

---

## Where we are

**M0 complete.** Core framework runs, demo pack passes its own ship gate against real
Docker, CI green.

| Milestone | State |
|---|---|
| M0 — core, docs, prompts, CI | ✅ Complete |
| M1 — accounting month-end close | ✅ Complete. Passes baseline + 2 domain adversaries on Docker |
| M2 — wave 1 packs (legal ×2, medical ×2, software) | ✅ Complete. Six tasks ship-ready |
| M3 — insurance, security | ❌ **Descoped.** More short tasks move us the wrong way — see `HORIZON.md` |
| Horizon — one long-form task | ✅ `accounting/year-close`. 12 linked months, delayed errors, 12 checkpoints |
| Flagship — DRG grouper | Phase 0 kill-test can run any time, ~$100. See `FLAGSHIP-DRG.md` |

### Six tasks, all gated on real Docker

| Task | Tier | Oracle | Baseline gate | Domain adversaries |
|---|---|---|---|---|
| `accounting/month-end-close` | 0 | 1.000 | pass | suspense-plug 0.048, flag-everything 0.143 |
| `software/replication` | 0 | 1.000 | pass | all three ≤ 0.200 |
| `legal/docket-deadlines` | 0 | 1.000 | pass | naive-calendar 0.278, no-roll 0.278 |
| `legal/citation-verify` | 1 | 1.000 | pass | flag-all 0.059, flag-none 0.059 |
| `medical/dosing` | 0 | 1.000 | pass | no-renal 0.263, refuse-all 0.158 |
| `medical/coding` | 1 | 1.000 | pass | max-reimbursement 0.143, ignore-exclusions 0.143 |
| `accounting/year-close` | 0 | 1.000 | pass | **isolated-month 0.214** (long-horizon) |

The oracle column is the one that matters: it proves each gate is real rather than an
artifact of output never reaching the verifier.

### What actually works today

```bash
uv run ef list                                      # demo/ledger-balance, T0, accounting
uv run ef run     demo/ledger-balance --seed 42
uv run ef redteam demo/ledger-balance --seeds 1,2,3 # all five policies score 0.000
uv run ef export  demo/ledger-balance --fmt inspect
```

17 tests, ruff clean, pyright 0 errors, CI green on first push.

---

## Decisions made

| Date | Decision | Rationale |
|---|---|---|
| 2026-08-29 | Monorepo with pluggable packs, not a branch per niche | Long-lived per-domain branches diverge; core fixes never merge back |
| 2026-08-29 | Thin core + exporters, don't rebuild a harness | Inspect AI / `verifiers` / METR already exist; rebuilding is months of zero differentiation |
| 2026-08-29 | Sequence by **verifier tier**, not by domain | Every domain has tier 0/1 sub-tasks that ship fast; legal deadlines are tier 0, contract redlining is tier 2 |
| 2026-08-29 | Open-core: public Apache-2.0 core + private packs | Core becomes the interchange format; packs are the acquirable asset |
| 2026-08-29 | Gameability Report as the differentiator | Labs can't currently tell a sound verifier from a gameable one |
| 2026-08-29 | Legal + medical move **up** into wave 1 | In-house lawyer, MDs, and accountant remove the usual expertise blocker |
| 2026-08-30 | **Docker/Local backends must agree on file naming** | A `./` prefix from `find .` made every `trace.final_files` lookup miss under Docker. Gates passed *vacuously*. Now covered by a parity test and a solver-scores-1.0-on-Docker test. |
| 2026-08-30 | **Abstaining earns no precision credit** | `no_false_positives` gave full marks for flagging nothing, so the suspense-plug policy scored 0.27. Precision is now conditional on having found a genuine error. |
| 2026-08-30 | **Fable 5 for red-team and verifier design; Opus 5 for everything else** | Fable is 2× Opus cost ($10/$50 vs $5/$25) and *more* capable, not cheaper. Worth it where we need frontier-grade adversarial reasoning — a weak adversary won't find the exploits a real training run does. Not worth it for generators and plumbing. |

### Model note

Fable 5 requires 30-day data retention and is **unavailable under zero-data-retention.**
Irrelevant on synthetic data, but it forecloses that path if a customer ever demands ZDR for
PHI-adjacent work. Revisit before any such commitment.

---

## Open questions

### Engineering

- [ ] **Rollout checkpointing** — an 8-hour run that dies at hour 7 loses everything. Blocks
      running `year-close` against a real model. Framework change, now the top engineering gap.
- [ ] **Trace store** (`prompts/build/05-trace-store.md`) — not started. Needed before we can
      answer aggregate questions: which dimension fails most, does score correlate with seed.
- [ ] E2B or Modal backend — do we need one, or is Docker sufficient through M2?
- [ ] `verifiers` and METR exporters — worth building before we have a buyer asking?

### Product / business

- [ ] **Who is the first conversation with?** The technical work is ahead of the commercial
      work. Worth starting outreach before M1 ships rather than after.
- [ ] Pricing: per-task, per-bundle, or per-domain licence? `docs/GTM.md` argues for bundles.
- [ ] Do we publish the demo pack's Gameability Report publicly as a credibility artifact?

### Domain — awaiting expert input

Worksheets are in the **private repo** at `worksheets/`. Each fills a real gap:

- [ ] **Accounting** — is the injected-error catalogue realistic? Is the suspense-account plug
      the true cheat?
- [ ] **Legal, deadlines — highest priority.** Is our order of operations right? We compute the
      base period, roll forward, *then* add the mail extension, then roll again. Reversing
      those steps changes a meaningful fraction of answers. Everything in that pack rests on
      this.
- [ ] **Legal, deadlines** — how often is naive calendar-day counting accidentally correct?
      That number determines how hard we must over-sample edge cases.
- [ ] **Legal, citations** — is "still good law" decidable from the citation alone, or does it
      need the proposition it's cited for? If the latter, this task is harder than planned.
- [ ] **Medical, coding** — where is the bright line between aggressive-but-defensible and
      upcoding? Is CPT's AMA licensing a problem for shipping bundles?
- [ ] **Medical, dosing** — tolerances per drug; how to express "do not dose" checkably.

### Known risks we haven't resolved

- **Buyer concentration.** A handful of labs are the whole market and can build in-house.
- **Obsolescence through success.** Genuinely general agents reduce the value of bespoke
  simulation. No answer; argues for speed over moat-building.
- **Expert bandwidth.** Practicing professionals have day jobs. The worksheets exist to make
  their hours convert to verifier code at the highest rate, but this is the real constraint.

---

## What M2 taught us

**Recall must be an exact set match, not a superset.** `flag-all-citations` scored 0.41
because flagging every citation earned full recall credit — perfect recall is trivial when
you accuse everything. This is the mirror image of the M1 abstention bug, and the same latent
hole existed in the accounting pack. Both are fixed.

The general rule now covering both: **a dimension must not be satisfiable by a degenerate
extreme.** Flagging nothing must not earn precision; flagging everything must not earn
recall.

## What M1 taught us

Two defects the gate caught, both worth carrying into every future pack:

1. **The gate was passing vacuously.** `DockerSandbox.list_files` returned `./name` while
   `LocalSandbox` returned `name`, so no agent output ever reached a verifier under Docker.
   Everything scored zero and looked defeated. **An all-zero red-team report is
   indistinguishable from a broken harness unless a real solver also scores 1.0 on the same
   backend.** That check is now a test, and it belongs in every pack's definition of done.
2. **Abstaining was being rewarded.** Reporting nothing earned full `no_false_positives`
   credit, so the suspense plug scored 0.27. Precision now requires having found something.
   Generalizes: any "did not do the bad thing" dimension must be conditional on having
   attempted the good thing.

Both are now baked into `prompts/generate/verifier-author.md` and the packager checklist.

## Next session

1. **Send an email to a lab.** The technical work is now well ahead of the commercial work,
   and six gated environments plus a published methodology is a real thing to open with. This
   is the highest-value hour available.
2. **DRG flagship Phase 0** — ~$100 and two weeks tells us whether the flagship is viable at
   all. See `FLAGSHIP-DRG.md`.
3. Collect worksheets, especially the deadline order-of-operations question.
4. **Fable 5 pass on the six verifiers** — is there a cheat none of our adversaries catch?
5. Difficulty calibration: real model, ≥20 seeds per task, target the 20–70% band. Right now
   we know the tasks are *ungameable*; we do not yet know they are *appropriately hard*.

**Rule that still gates everything:** a pack ships only when the baseline gate, its domain
adversaries, *and* a real solver at 1.0 all hold on the real backend.
