# Strategy

## What we build

**We build the environment half of the RL loop: the world an agent acts in, and the program
that grades what it did.** We do not train models and we do not write RL algorithms. Labs
bring the model, the GPUs, and the optimizer.

The full research memo this derives from is preserved at
[`research/mechanize-memo-original.md`](research/mechanize-memo-original.md).

## Claim provenance

The memo is a market-research narrative, not a build spec, and several of its load-bearing
figures postdate our ability to check them. Tagged honestly:

| Claim | Status |
|---|---|
| RL environments are a real, funded procurement category at frontier labs | **[verified]** — Inspect AI, SWE-Gym, Terminal-Bench, METR's task standard all exist publicly |
| Verifiable-reward training (RLVR) is the active frontier for agentic capability | **[verified]** |
| Deterministic graders resist reward hacking better than model judges | **[verified]** — this is the technical bedrock and it does not depend on any deal |
| Google acquired/licensed Mechanize for >$1.5B on the stated dates | **[unverified]** — postdates knowledge cutoff; not independently confirmed |
| $9.1M seed at $500M valuation, 103 days to acquisition | **[unverified]** |
| ~$2,400 lifetime compute per RL task | **[unverified]** — sourced to a Mechanize essay; directionally plausible, not audited |
| Mechanize salary bands ($300–400K) | **[unverified]** |

**Nothing in our build plan depends on the unverified figures.** They affect how large the
prize looks, not whether the technical approach is sound. The strategy stands if the deal
numbers are wrong by an order of magnitude.

## What the acquired asset actually was

Not a model, not a product, not infrastructure. Three things:

1. **A corpus of environments** — containers holding a codebase, a task, and a tool surface.
2. **The verifiers** — programs deciding objectively whether the agent succeeded. GBA Eval
   has models write a Game Boy Advance emulator in Rust→WASM in 24 hours, then grades it
   frame-by-frame and audio-sample-by-sample against a modified Mesen2 reference. Binary,
   deterministic, impossible to bluff.
3. **The people** who know how to build graders a frontier model cannot cheat.

## Three corrections to the memo

### 1. Monorepo with pluggable packs, not a branch per niche

The memo proposes a base framework "branching off into niches." Long-lived per-domain
branches diverge immediately and core fixes never merge back. Domains are **packs**
discovered through entry points — see [ARCHITECTURE.md](ARCHITECTURE.md).

### 2. The harness is not the moat

Inspect AI, prime-intellect's `verifiers`, METR's task standard, Terminal-Bench and SWE-Gym
already exist. Rebuilding a harness is months of zero differentiation.

Our core is deliberately thin, and we **export to those harnesses** rather than compete
with them. An environment a lab can drop into its existing pipeline is worth more than one
requiring them to adopt our runner.

The effort goes where nobody else is: the verifier compiler and the adversarial red-team.

### 3. Sequence by verifier tier, not by domain

The memo leads with law and medicine because they are hard. High value — but sequencing by
domain difficulty is backwards. **Sequence by tier.** Every domain has tier-0/1 sub-tasks
that ship fast, and tier-2/3 sub-tasks that should wait.

Accounting month-end close and legal docket-deadline computation are both tier 0. Contract
redlining and clinical differential diagnosis are both tier 2. The first pair ships this
quarter; the second pair waits — and *domain* has nothing to do with it.

## The wedge the memo misses

Labs spend real compute per environment and **cannot tell whether the reward signal is
sound** before spending it. Nobody sells verified verifiers.

Every environment we ship carries a **Gameability Report**: five adversarial reward-hacking
policies run against our own verifier across multiple seeds, with the exploits found and
patched. It is a machine-checkable artifact, it is the product differentiator, and it is
the reason a buyer should trust our tasks over a cheaper supplier's.

See [VERIFIERS.md](VERIFIERS.md).

## Our structural advantage

The memo's own thesis (§3.2, §6.2) is that **extracting deep domain expertise is the
bottleneck** — encoding tacit practitioner knowledge into reward functions — and that
Mechanize pays $300–400K/yr to buy it.

This team already has a practicing lawyer and medical doctors. That is the scarce input,
and it is in-house.

**Critical: experts are verifier authors, not task authors.** Having a lawyer write hard
legal questions produces a static Q&A dataset — commoditized, and not an RL environment at
all. Having a lawyer decompose *what makes a redline correct* into a checkable reward chain
is the thing competitors cannot replicate by hiring engineers. See
[`prompts/expert/`](../prompts/expert/).

## Honest risks

- **Open-source commoditization.** The lower tiers of this market will commoditize. Our
  answer is to be the standard interchange format at the bottom (Apache-2.0 core) and sell
  the part that does not commoditize.
- **Obsolescence through success.** If these environments train genuinely general agents,
  bespoke simulation loses value. This is a real long-run risk and we do not have an answer
  to it; it argues for moving fast rather than building a decade-long moat.
- **Engineering capacity, not expertise, is our binding constraint.** Experts author gold
  data; someone still builds generators. Parallel domains are only safe because tier-0/1
  packs reuse identical machinery.
- **Concentrated buyers.** A handful of labs constitute the entire market. They can build
  in-house at any time, and one of them just bought our closest analogue's whole team.
