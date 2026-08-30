# Pack: legal / docket-deadlines  (wave 1)

**Status:** not started. Expert authoring can begin immediately.
**Tier:** 0 — deterministic. **Expert:** lawyer. **Repo:** private.

## Why this task

The sleeper of the whole roadmap. Deadline computation is genuinely deterministic, genuinely
hard for models, commercially real, and nobody has built it as an RL environment.

Models fail it in characteristic ways: conflating calendar days with court days, missing
holiday rules, misapplying the mailbox rule, forgetting that a deadline landing on a weekend
rolls forward.

## The task

Given a jurisdiction, a trigger event, a service method, and a filing type, compute the
deadline. One date. One correct answer.

## The generator

Ground truth comes from an **executable rule encoding**, not from a solver: FRCP Rule 6 plus
local rules, court holiday calendars, service-method extensions, weekend/holiday roll-forward.

Build the encoding first (see `prompts/expert/elicit-rule-encoding.md`), then generate
scenarios by sampling jurisdiction × trigger × service method × date. The date is computed
by the encoding; the scenario text is rendered from it.

Sample deliberately near edges — deadlines landing on holidays, service by mail crossing a
weekend, periods short enough for the sub-11-day rules to matter. Uniform sampling produces
mostly easy cases and a task that looks solved when it is not.

## The verifier (tier 0)

- `deadline_correct` — exact date match, the dominant weight
- `rule_cited` — the controlling rule identified (structural, not judged)
- `reasoning_steps` — intermediate dates (trigger, raw period, extensions) correct

Intermediate credit matters here: a model off by one holiday is closer to correct than one
that used calendar days, and the gradient should distinguish them.

## Red-team, beyond the baselines

Add a **naive-calendar policy** that always answers `trigger + N calendar days`. If the seed
distribution is lazy this scores well, which reveals that the sampler is not hitting the
edges that make the task meaningful.

## Data

Court rule text is generally public. Holiday calendars are published. **Never scrape Westlaw
or Lexis** — hard line. Headnotes and editorial content are not public even where the
underlying rule is; the lawyer reviews before ingestion.

## Expert loop

The lawyer validates the rule encoding, not individual answers. Every disagreement between
encoding and expert becomes a regression test. Publish the agreement rate.
