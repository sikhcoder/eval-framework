# Flagship environments

The showcase artifacts — the legal and medical equivalents of Mechanize's GBA Eval.

These are **not** M1 work. Each is months of effort. They are the thing that makes a lab
take a meeting, built once the tier-0/1 packs have proven the machinery.

## What made GBA Eval work

Mechanize's flagship has models write a Game Boy Advance emulator in Rust→WASM in 24 hours,
graded frame-by-frame and audio-sample-by-sample against a modified Mesen2 reference.

Strip away the Game Boy and the recipe is four properties:

1. **A pre-existing authoritative reference implementation** (Mesen2) they did not write or
   validate — it was already the oracle.
2. **Zero entropy in the system.** The GBA has no wall clock, no RNG, no analog input.
   Identical inputs give bit-identical outputs. (Mechanize explicitly excludes the cartridges
   with solar sensors and gyroscopes.)
3. **Enormous scope**, so the task cannot be one-shot or luck-guessed.
4. **Bit-exact comparison.** Nothing to argue about.

**They did not invent a grading rubric. They found a domain that already had an oracle and
exploited it.**

So the question is never "what's a hard legal or medical task?" It is: **where does the
domain already have a published, deterministic reference implementation we can diff against?**

## Candidates, ranked by whether the oracle already exists

| Candidate | External oracle exists? | Entropy | Verdict |
|---|---|---|---|
| **CMS MS-DRG grouper** | **Yes — CMS publishes the logic** | None | **Medical flagship** |
| **State child support calculators** | **Yes — official state calculators** | None | **Legal flagship** |
| Medicare fee schedule (RVU → payment, GPCI) | Yes — CMS files | None | Strong |
| NCCI bundling edits | Yes — published tables | None | Strong |
| Federal sentencing guidelines | Partly — manual published | None | Strong |
| EDGAR XBRL validation | Yes — Arelle + published rules | None | Strong (compliance) |
| Tax computation | Yes — IRS published test scenarios | None | Strong |
| Docket deadline computation | **No — we author it** | None | Good task, weaker oracle |

That last row is the important distinction. Docket deadlines remain a solid wave-1 task, but
they are **not** the GBA Eval analogue: we would be writing the oracle ourselves, which
reintroduces the "verifier is only as good as your solver" problem that
[VERIFIERS.md](VERIFIERS.md) warns about. The top two rows do not have that weakness.

## Medical flagship — reimplement the DRG grouper

> **Given the published CMS specification, write a Medicare MS-DRG grouper from scratch.**

Near-perfect structural match to GBA Eval:

- **Oracle exists.** CMS publishes the definitions manual and grouper logic. We do not have
  to establish correctness — it is already authoritative. *[verify current licensing]*
- **Scope is real.** MDC assignment, surgical hierarchies, CC/MCC tiers, thousands of
  cross-referenced rules. Months of human work.
- **Zero entropy.** No clock, no RNG, no network. Same claim, same DRG, always.
- **Bit-exact grading.** Push millions of synthetic claims through candidate and reference,
  compare assignment claim-by-claim. A DRG is an integer — you cannot bluff an integer.

**What the MDs do** — not grading outputs. They make the **claim generator clinically
coherent**, because the grouper's edge cases only fire on realistic claims. A generator
emitting a hysterectomy on a male patient, or an MCC that cannot co-occur with its principal
diagnosis, never exercises the paths where implementations actually diverge. The MDs are why
the corpus hits the interesting 5% instead of the boring 95%.

Commercial bonus: this is directly valuable to revenue-cycle management, so the flagship
doubles as a product.

## Legal flagship — reimplement a support-guideline engine

> **Given a state's published child support guidelines, write the calculation engine.**

- **Oracle exists.** Several states publish official calculators — a genuine third-party
  reference, the Mesen2 equivalent, rather than one we author. *[verify licensing and
  scraping terms]*
- **Deterministic.** Income shares, custody-time adjustments, healthcare and childcare
  add-ons, low-income adjustments, self-support reserve. Facts in, dollar amount out.
- **Bit-exact grading.** Generate scenarios, diff the number.

Federal sentencing guidelines are the same shape (facts → offense level → guideline range)
with a slightly weaker oracle, since the manual is published but reference implementations
are less canonical.

**What the lawyer does:** pick the jurisdiction with the cleanest published rules and a live
official calculator, validate the rule encoding against the statute, and **clear licensing on
the reference materials**. That last item is a real gate, and answering it in-house in a week
rather than a quarter is a genuine structural advantage.

## Gates before starting either

- [ ] **Licensing cleared.** CMS materials are generally US government works, but **the AMA
      licenses CPT** — already flagged in the medical coding worksheet. Confirm before any
      bundle ships.
- [ ] **Oracle is legitimately usable** as a reference — check terms for the official
      calculators, and never scrape where terms forbid it.
- [ ] **Tier-0/1 packs shipped first.** These are months each. They are the showcase, not the
      first deliverable.
- [ ] **The generator is expert-validated**, or the corpus never reaches the paths that
      distinguish a correct implementation from a plausible one.

## Why this shape is worth the months

A flagship does something no bundle of small tasks does: it proves we can build an
**ungameable, long-horizon environment in a domain everyone else thinks is unverifiable.**
That is the exact claim a lab cannot currently buy, and it is what a $1.5B precedent was
reportedly built on.
