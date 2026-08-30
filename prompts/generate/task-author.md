# Task author

**Goal:** design a task and its generator, before any verifier code exists.

## The order that matters

**Ground truth first. Agent-visible material derived from it.**

Never the reverse. A generator that produces a problem and then solves it to get ground
truth makes the verifier only as trustworthy as the solver — and that is exactly how
gameable environments get built. Construct the answer, then construct the question around it.

## Design checklist

**Is it long-horizon?** A one-shot question is a benchmark, not an RL environment. The agent
should need multiple tools, multiple steps, and intermediate state.

**Does the answer vary with the seed?** If not, it is a memorizable constant. The `overfit`
policy exists to catch this and it will.

**Is there a degenerate strategy?** Ask what a lazy agent does. "Flag everything." "Deny
everything." "Delete the failing service." If a degenerate strategy scores well, add the
dimension that punishes it *now* — `no_false_positives`, `no_spurious_denial`,
`service_still_works` — not after the red-team catches it.

**Where is the entropy?** For replication-style tasks, references with a wall clock, RNG, or
network are not deterministically comparable. This is the insight behind GBA Eval: the
console has no entropy source, so identical inputs yield identical frames.

**Is the difficulty band useful?** A task nothing solves is broken, not hard. A task
everything solves is spent. Target a real model pass rate roughly in the 20–70% band.

## Sampling

Sample **near the edges** deliberately. Uniform sampling produces mostly easy instances and a
task that looks solved when it is not. Boundaries, thresholds, holidays, phase-outs — those
are where models fail and where the environment earns its price.

## Deliverables

- [ ] `TaskSpec` with an unambiguous output format in the instruction
- [ ] `TaskGenerator.generate(seed)`, deterministic in seed
- [ ] `GroundTruth.payload` — everything the verifier needs, nothing the agent may see
- [ ] Tests: determinism, seed variation, canary absence from generated files
