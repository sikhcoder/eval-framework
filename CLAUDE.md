# eval-framework

We build the environment half of the RL loop: the world an agent acts in, and the program
that grades what it did. We do not train models and we do not write RL algorithms.

## The two rules

**1. Ground truth never enters the sandbox.**
Generators construct ground truth *first* and derive agent-visible material from it — never
the reverse. A generator that solves its own puzzle makes the verifier only as trustworthy
as the solver. `TaskInstance.ground_truth` is `exclude=True`; `public_manifest()` is the only
sanctioned path into a sandbox.

**2. Nothing ships until `ef redteam` passes on the real backend.**
A reward-hack policy scoring above zero is a defect report about us, not a result about the
model. Fix the verifier. Never raise the threshold.

## The tier ladder

0 deterministic · 1 structural · 2 reference-chain · 3 calibrated judge.
**A pack may not use tier N until it has exhausted tier N−1.** Tier 3 never ships alone.

Read `docs/VERIFIERS.md` before writing or changing any verifier.

## Layout

- `packages/ef-{core,sandbox,verify,runner,redteam,export,cli}` — the Apache-2.0 core
- `packs/ef-pack-demo` — public tier-0 reference implementation
- `docs/` — STRATEGY, ARCHITECTURE, VERIFIERS, NICHES, GTM, ROADMAP
- `prompts/{build,packs,expert,generate}` — working prompts

Domain packs live in the **private** `eval-framework-packs` repo and register through the
`ef.packs` entry point group.

## Commands

```bash
uv sync --extra demo
uv run ef list
uv run ef redteam demo/ledger-balance --seeds 1,2,3
uv run pytest -q && uv run ruff check . && uv run pyright
```

## Conventions

- Python 3.12+, pydantic v2, 100-char lines, ruff + pyright clean before commit
- `ef` is a PEP 420 namespace package — **never** add `__init__.py` to `src/ef/`
- Verifiers make no network calls; they are otherwise not reproducible or auditable
- Money is `Decimal` compared with `money_equal`, never float equality
- `Reward.dimensions` is plural. A single boolean is a sparse gradient.
- Heavy imports (docker, the Claude SDK) go inside functions so `ef --help` stays fast

## What not to do

- Do not add a rollout path that bypasses `rollout()`. Adversarial policies and real models
  share it deliberately — that is what makes the Gameability Report mean anything.
- Do not persist `GroundTruth` to any analysis artifact.
- Do not commit anything under `references/QUARANTINE/` or holdout material.
