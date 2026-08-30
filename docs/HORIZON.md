# Horizon

The gap between what we have built and what frontier labs actually buy.

**Recorded 2026-08-30, after M2.** Our verification is ahead of the market. Our task horizon
is behind it. This document says why that matters and how to close it.

---

## The finding

| | Mechanize | Us (after M2) |
|---|---|---|
| Verifiable rewards, no human preference | ✅ | ✅ |
| Sandbox + task + programmatic grader | ✅ | ✅ |
| Ungameable verifier as the moat | ✅ | ✅ **— and we ship adversarial proof, which they do not publish** |
| Oracle source | Existing third-party reference (Mesen2) | We author ground truth via generators |
| **Task horizon** | **24 hours — write a whole GBA emulator** | **~30 minutes — parse a CSV** |
| Domain strategy | Deep in one (software) | Broad across four |

The first three rows are solid, and row three is where we are genuinely ahead of anything
published.

**Row five is the problem.**

## Why horizon is the thing

Mechanize's central bet is long-horizon work, because that is where frontier models actually
fail. Not on single reasoning steps — on sustaining a plan across hours, recovering from
their own earlier mistakes, and holding state that no longer fits in context.

A task that takes a competent human 30 minutes and produces one artifact tests *knowledge*.
A task that takes weeks and produces a system tests *agency*. Labs are buying the second one.

Our six tasks are roughly SWE-bench scale: single-shot, 20–40 minutes of human work, one file
written at the end. That is a real category, but it is the commoditized end of it —
closer to an eval than to a training environment.

## What this means for positioning

**We have a verification methodology, demonstrated on six small tasks.** The methodology is
the differentiated asset. The tasks are evidence that it works, not the product.

This sharpens the pitch rather than weakening it. Do not lead with "six environments" — a lab
will compare six 6KB CSV tasks against what they bought from Mechanize, and the comparison is
unflattering. Lead with verification, and use the tasks as evidence.

## What transfers unchanged

Everything except the tasks:

- `TaskSpec` / `TaskInstance` / `GroundTruth` with canary leak detection
- The five baseline adversaries and the whole red-team harness
- `Checklist` dimensional scoring, and the two hard-won rules below
- Sandbox, rollout engine, exporters, CLI

**Horizon is the missing dimension, not rigor.** Nothing in the framework needs rebuilding.

## How to add it, per domain

### Accounting — the cheapest, since the generator exists

Not "find 5 errors in one month." **Twelve consecutive months**, where:

- Errors compound: an unfixed March accrual is still wrong in December
- Prior-period adjustments are required once a closed month is found to be wrong
- The agent carries state across closes — opening balances come from its own prior output
- Some errors are only *detectable* later, when a subsequent-month document contradicts an
  earlier assumption

That is hours of work, and a mistake in March poisons everything after it. The verifier
extends naturally: score each month's trial balance, plus whether prior-period adjustments
were correctly recognized and applied.

### Legal — a whole docket

Not one deadline. Thirty deadlines across a case lifecycle, with intervening events that
reset or toll clocks: an amended complaint, a stay, a granted extension, a substituted party.
The agent maintains a live calendar and must revise it as events arrive.

### Medical — the flagship

Implement the grouper. See [FLAGSHIP-DRG.md](FLAGSHIP-DRG.md). This is already the right
instinct and it is the closest thing we have to a true GBA Eval analogue.

### Software — a whole utility

Not one function against a generated spec. A complete tool with subcommands, config parsing,
error handling, and streaming behaviour, diffed against a reference implementation across
thousands of invocations.

## The two rules that carry forward

Both were found by running our own gate, and both generalize to any environment:

1. **A dimension must not be satisfiable by a degenerate extreme.** Flagging nothing must not
   earn precision; flagging everything must not earn recall.
2. **An all-zero red-team report is indistinguishable from a broken harness** unless a real
   solver also scores 1.0 on the same backend.

Long-horizon environments make both *more* dangerous, not less: with more dimensions and more
steps, there are more places for a degenerate strategy to hide.

## Sequencing

1. **Calibrate the six existing tasks first.** If a frontier model already scores 90%+, that
   confirms the horizon diagnosis empirically and is worth knowing before building anything.
2. **Talk to a buyer** before committing months to a long-form environment.
3. **Then one long-form task** — the 12-month close, since the generator already exists —
   or DRG Phase 0.

**Do not build more short tasks in new domains.** M3/M4/M5 as originally scoped would move
us further in the wrong direction: more of the thing we already have too much of.
