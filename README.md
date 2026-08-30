# eval-framework

**Verifiable RL environments for agentic AI — the gym and the grader, not the model.**

We build the environment half of the reinforcement learning loop: the world an agent acts
in, and the program that decides, objectively, whether it succeeded. We do not train models
and we do not write RL algorithms.

## Why this exists

Frontier labs spend substantial compute per RL environment and **cannot tell whether the
reward signal is sound** before spending it. A verifier that can be gamed produces a model
that learned to cheat — at full cost.

Nobody sells verified verifiers. So every environment built with this framework ships with a
**Gameability Report**: five adversarial reward-hacking policies run against its own
verifier, across multiple seeds, with the exploits found and patched.

```
$ uv run ef redteam demo/ledger-balance --seeds 1,2,3

Gameability Report — demo/ledger-balance
seeds=[1, 2, 3] threshold=0.05

  [     ok] null           max_score=0.000
  [     ok] test-tamper    max_score=0.000
  [     ok] oracle-search  max_score=0.000
  [     ok] output-mimic   max_score=0.000
  [     ok] overfit        max_score=0.000

VERDICT: PASS — safe to ship
```

A policy scoring above zero is never an interesting result about the model. It is a defect
report about the verifier.

## Quickstart

```bash
uv sync --extra demo
uv run ef list
uv run ef run     demo/ledger-balance --seed 42 --agent claude
uv run ef redteam demo/ledger-balance --seeds 1,2,3
uv run ef export  demo/ledger-balance --fmt inspect
```

## The tier ladder

Domains differ far less than they appear to. What actually differs is how hard the verifier
is — so we sequence by tier, not by industry.

| Tier | Mechanism | Where it shows up |
|---|---|---|
| **0** Deterministic | Exact match, unit tests, balance checks, trace equality | Accounting, tax, insurance adjudication, security, software |
| **1** Structural | Resolves against an authority: citation exists, filing validates, code is legal for the diagnosis | Legal, compliance, medical coding |
| **2** Reference-chain | Gold document decomposed into scored dimensions | Contract redlining, clinical notes |
| **3** Calibrated judge | Model judge with measured human agreement | Never ships alone |

**A pack may not use tier N until it has exhausted tier N−1.**

Legal docket-deadline computation is tier 0. Contract redlining is tier 2. The domain is the
same; only the verifier difficulty differs — and that, not the industry, is what determines
what ships first.

## Architecture

Adding a domain means implementing three things. Everything else is shared.

| Varies per pack | Shared by every pack |
|---|---|
| `TaskGenerator` — seed data + private ground truth | Sandbox runtime |
| `Toolset` — SQL? PDF? bash? | Rollout engine, trace capture |
| `Verifier` — tier 0–3 | Scoring, red-team, packaging, exporters |

```
packages/ef-core      TaskSpec, GroundTruth, Trace, Reward, protocols, registry
packages/ef-sandbox   Docker (default, network denied) and Local (test-only)
packages/ef-verify    BaseVerifier, Checklist, leak guard
packages/ef-runner    rollout(), ClaudeAgent, ScriptedAgent
packages/ef-redteam   five reward-hack policies, GameabilityReport
packages/ef-export    Inspect AI exporter
packages/ef-cli       the `ef` command
packs/ef-pack-demo    public tier-0 reference implementation
```

Packs register through the `ef.packs` entry point group, so domain packs install
independently of the core.

## The invariant

**Ground truth never enters the sandbox.** If the agent can read the answer, a perfect score
means nothing.

This is enforced structurally, not by convention: `TaskInstance.ground_truth` is excluded
from serialization, `public_manifest()` is the only sanctioned path into a sandbox, and every
ground truth carries a random canary that the `oracle-search` policy hunts for. A canary
sighting is reported as a verifier defect — our bug, not the model's.

Generators must construct ground truth **first** and derive the agent-visible material from
it. Deriving truth the other way makes the verifier only as trustworthy as the solver.

## Docs

| | |
|---|---|
| [STRATEGY.md](docs/STRATEGY.md) | What we build and why, with claim provenance |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Interfaces, plug points, data flow |
| [**VERIFIERS.md**](docs/VERIFIERS.md) | The tier ladder and the ship gate — **start here** |
| [NICHES.md](docs/NICHES.md) | Domains, ordered by tier |
| [FLAGSHIPS.md](docs/FLAGSHIPS.md) | The GBA Eval analogues for law and medicine |
| [GTM.md](docs/GTM.md) | Open-core rationale, pricing posture, risks |
| [ROADMAP.md](docs/ROADMAP.md) | Milestones and gates |
| [STATUS.md](docs/STATUS.md) | Living log: progress, decisions, open questions |

Working prompts for building with Claude Code live in [`prompts/`](prompts/).

## Development

```bash
uv sync --extra demo
uv run pytest -q          # contract tests + the ship gate
uv run ruff check .
uv run pyright
```

Contract tests in `tests/test_contracts.py` apply to any pack: protocol conformance, seed
determinism, leak guarding, dimensional credit, and verifier crash containment. New packs
inherit real coverage the moment they register.

## License

Apache-2.0. Domain packs, gold references, and holdout sets are maintained separately.
