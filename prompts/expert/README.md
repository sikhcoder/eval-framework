# Expert elicitation

The highest-leverage prompts in this repository.

Our structural advantage is that the domain expertise the memo identifies as *the*
bottleneck — and which Mechanize pays $300–400K/yr to buy — is already in-house.

**Experts are verifier authors, not task authors.** Having a lawyer write hard legal
questions produces a static Q&A dataset: commoditized, and not an RL environment at all.
Having a lawyer decompose *what makes an answer correct* into a checkable rule is the thing
competitors cannot replicate by hiring engineers.

Every session here ends in a **machine-checkable artifact** — a decision table, a rule
encoding, a test case — never in prose. Prose is the failure mode. If a session produces a
memo, it produced nothing.

## Running a session

Pair an engineer with the expert. The engineer drives the prompt and writes code live; the
expert corrects. Expect 60–90 minutes to yield one encoded rule with its edge cases.

| Prompt | Produces |
|---|---|
| `elicit-rule-encoding.md` | An executable decision table + adversarial edge cases |
| `elicit-reward-chain.md` | A weighted, scored decomposition of a gold document |
| `expert-review-verifier.md` | Regression tests from verifier/expert disagreements |
| `gold-set-provenance.md` | Source, license, and DUA status for every reference file |
