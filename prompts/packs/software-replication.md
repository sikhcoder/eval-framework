# Pack: software / replication  (wave 1)

**Status:** not started. **Tier:** 0. **Repo:** private.

## The task

Implement a specified piece of software from scratch so that its behavior matches a
reference implementation.

## Why it is cheap

The reference's own test suite and I/O pairs are the verifier. Verifier cost is near zero,
which is the entire argument for including software despite it being the most contested
domain. This is a credibility play, not the revenue play.

## The generator

Pick a reference (a CLI utility, an encryption routine, a parser, a small protocol
implementation), write a rigorous behavioral spec, and generate I/O pairs by running the
reference. Ground truth is the reference's behavior.

Prefer references with **no entropy** — no wall clock, no RNG, no network — or the
comparison is not deterministic. This is the same insight behind GBA Eval: the console has
no entropy source, so identical inputs give identical frames.

## The verifier (tier 0)

- `io_matches` — per-case credit across the generated pairs
- `edge_cases` — separately weighted, because these are where implementations actually differ
- `no_reference_import` — the candidate must not shell out to or import the reference

## Red-team, beyond the baselines

`test-tamper` matters most here. The verifier must score from I/O pairs held **outside** the
sandbox, never from a test file the agent can edit. Add a **special-case policy** that
hardcodes the visible cases: if it scores, the held-out set is too small.

## Licensing

Only reference implementations whose licenses permit this use. Record provenance per
reference.
