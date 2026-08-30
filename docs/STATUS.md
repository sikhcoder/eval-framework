# Status

Living log of progress, decisions, and open questions. **Update this at the end of every
working session** — it is the handoff artifact between sessions and between people.

Last updated: **2026-08-30**

---

## Where we are

**M0 complete.** Core framework runs, demo pack passes its own ship gate against real
Docker, CI green.

| Milestone | State |
|---|---|
| M0 — core, docs, prompts, CI | ✅ Complete |
| M1 — accounting month-end close | 🔜 Next. Blocked on nothing; expert input improves it |
| M2 — wave 1 packs (legal ×2, medical ×2, software) | ⏸ Gated on M1's red-team gate holding |
| M3+ — insurance, security, tier 2 | Not started |

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
| 2026-08-30 | **Fable 5 for red-team and verifier design; Opus 5 for everything else** | Fable is 2× Opus cost ($10/$50 vs $5/$25) and *more* capable, not cheaper. Worth it where we need frontier-grade adversarial reasoning — a weak adversary won't find the exploits a real training run does. Not worth it for generators and plumbing. |

### Model note

Fable 5 requires 30-day data retention and is **unavailable under zero-data-retention.**
Irrelevant on synthetic data, but it forecloses that path if a customer ever demands ZDR for
PHI-adjacent work. Revisit before any such commitment.

---

## Open questions

### Engineering

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
      the true cheat? *(gates M1 quality)*
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

## Next session

1. Collect worksheets from accounting/legal/medical colleagues (async — doesn't block).
2. Build M1: `prompts/packs/accounting-month-end-close.md`. Use the env-initializer agent
   to scaffold and write `PROGRESS.md`, then iterate one feature per session.
3. Add the accounting-specific red-team policy (suspense-account plug) **before** declaring
   M1 done — the five baselines won't catch it.

**Rule that gates everything:** if M1's red-team gate doesn't hold on Docker, M2 does not
start. Four packs on a broken pattern is four times the rework.
