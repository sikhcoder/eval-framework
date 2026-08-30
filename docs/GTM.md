# Go to market

## Open core

| | Public — `eval-framework` (Apache-2.0) | Private — `eval-framework-packs` |
|---|---|---|
| **Contents** | Task schema, sandbox, runner, verifier interfaces, red-team harness, exporters, demo pack | Domain generators, gold references, holdout sets, red-team results |
| **Purpose** | Become the standard interchange format. Distribution and credibility. | The asset. This is what gets acquired. |

The core is given away deliberately. A lab that already runs our schema has near-zero
switching cost to buying our packs, and an environment format others adopt is worth more to
an acquirer than a private one nobody has heard of.

Note what is *public*: the red-team harness itself. Publishing the adversarial policies
proves the methodology and invites others to attack our claims. What stays private is the
gold data and the domain rule encodings — the parts that took expert time.

## What a customer actually buys

A packaged environment bundle:

1. The container spec and task generator (seeded, reproducible)
2. The verifier, with dimensional scoring
3. **The Gameability Report** — five adversarial policies × N seeds, with exploits found and patched
4. Exporters for their existing harness (Inspect AI today)
5. A private holdout split, canary-stamped and variant-generated per buyer

Item 3 is the differentiator. Everyone else sells tasks; we sell tasks with a proof that the
reward signal survives adversarial pressure.

## Pricing posture

Price against the buyer's compute exposure, not against our labor. If a lab spends
meaningful compute per task over its lifetime ([unverified] — the memo cites ~$2,400), then
a cheap task with a weak signal is not a saving, it is a way to waste the compute. That is
the entire pitch, and it means we should never compete on being the cheapest supplier.

Sell in bundles per domain rather than per task: a curriculum with graded difficulty is
worth more than the sum of its tasks, and it is much harder for a buyer to replicate
piecemeal.

## Sequence

1. **Credibility** — public core runs, demo pack passes its own gate, red-team methodology
   is published and reproducible.
2. **First bundle** — accounting month-end close, a few hundred seeded variants with
   graded difficulty and a clean report.
3. **Expert-authored bundles** — legal docket deadlines and medical coding. These are the
   proof that we solved verification *outside* software engineering, which is the thing
   labs cannot currently buy.
4. **Breadth** — insurance and security reuse the same machinery at low marginal cost.

## Why an acquirer would care

The precedent ([unverified], but structurally instructive) is that Google bought a corpus,
a set of graders, and the people who make graders uncheatable — not a product.

What makes us acquirable is therefore: a domain corpus that cannot be regenerated cheaply, a
verification methodology with published evidence it works, in-house expertise in domains
where verification is unsolved, and a format the buyer already uses.

Note the incentive this creates: we are more valuable having proven the method across four
domains than having perfected one. That is an argument for breadth — but only across
domains whose tier-0/1 sub-tasks reuse the same machinery, which is exactly the roadmap.

## Honest risks

- **Buyer concentration.** A handful of labs are the whole market, they can build in-house
  at any time, and one just absorbed our closest analogue's entire team.
- **Commoditization from below.** Open-source environment collections improve fast. Our
  answer is to *be* the open layer at the bottom and sell above it.
- **Obsolescence through success.** Genuinely general agents reduce the value of bespoke
  simulation. No good answer; it argues for speed over moat-building.
- **Expert bandwidth.** Practicing lawyers and doctors have day jobs. The
  [`prompts/expert/`](../prompts/expert/) elicitation flow exists to make their hours
  convert to verifier code at the highest possible rate.
