# Architecture

## The shape of the thing

Every domain reduces to the same five pieces. Only three vary.

| Varies per pack | Shared by every pack |
|---|---|
| `TaskGenerator` — seed data + private ground truth | Sandbox runtime |
| `Toolset` — SQL? PDF? EHR API? bash? | Rollout engine, trace capture |
| `Verifier` — tier 0–3 | Scoring, red-team, packaging, exporters |

**Adding a domain is implementing three classes.** That is the entire reason a single team
can credibly ship accounting, legal, medical, and software packs — the marginal engineering
cost per pack is low, and the real cost is gold data and expert time.

## Packages

```
packages/
  ef-core/      TaskSpec, TaskInstance, GroundTruth, Trace, Reward, protocols, registry
  ef-sandbox/   Sandbox protocol; Docker (default) and Local (test-only) backends
  ef-verify/    BaseVerifier, Checklist, leak guard, tier primitives
  ef-runner/    rollout(), ClaudeAgent, ScriptedAgent
  ef-redteam/   five reward-hack policies, GameabilityReport
  ef-export/    Inspect AI exporter and trace bridge
  ef-cli/       the `ef` command
packs/
  ef-pack-demo/ public tier-0 reference implementation
```

`ef` is a PEP 420 namespace package, so each distribution installs independently. That is
what lets the proprietary packs live in a separate private repository from the Apache-2.0
core.

## Pack discovery

Packs register through the `ef.packs` entry point group:

```toml
[project.entry-points."ef.packs"]
demo = "ef_pack_demo:PACK"
```

`Registry.resolve("demo/ledger-balance")` returns the `(generator, verifier)` pair. Installing
a private pack alongside the public core makes its tasks appear in `ef list` with no core
changes.

## Data flow

```
generator.generate(seed)
        │
        ├─ GroundTruth ──────────────────────┐  never enters the sandbox
        │                                    │
        └─ TaskInstance.files                │
                 │                           │
                 ▼                           │
           sandbox.start()                   │
                 │                           │
                 ▼                           │
        agent.run(instance, sandbox)         │
                 │                           │
                 ▼                           │
              Trace ────────────────────────▶├─▶ verifier.verify() ─▶ Reward
                                             │        │
                                       leak guard ────┘
```

The single most important line in that diagram is the one that does not exist: there is no
path from `GroundTruth` into the sandbox.

## Key design decisions

### Ground truth is structurally excluded, not excluded by convention

`TaskInstance.ground_truth` is a pydantic field with `exclude=True`, so serialization omits
it by default. Leaking it requires reaching for it deliberately. Every `GroundTruth` also
carries a random **canary** that the `oracle-search` policy hunts for inside the sandbox.

### Network denied by default

`SandboxSpec.network` defaults to `False`. An agent that can reach the internet can
exfiltrate a task, fetch a solution, or contaminate a future benchmark. Packs opt in
explicitly and justify it.

### Adversarial policies are ordinary agents

`NullPolicy`, `TestTamperPolicy` and friends implement the same `Agent` protocol as
`ClaudeAgent` and run through the same `rollout()` path. Whatever they score is exactly what
a real model would score by doing the same thing. Sharing one path is what makes the
Gameability Report trustworthy rather than a separate, divergent code path that proves
nothing.

### Determinism in the seed

`generate(seed)` must be byte-identical for the same seed — enforced by
`test_generation_is_deterministic_in_seed`. This is what makes a run reproducible and a leak
attributable to a specific buyer.

Equally, the answer must *differ* across seeds
(`test_different_seeds_differ`). A task whose answer is constant is a memorizable constant,
not an environment, and the `overfit` policy exists to prove it.

### Interop over lock-in

`ef-export` renders tasks for Inspect AI, delegating scoring back to our verifier so the
score is identical across harnesses. Adding `verifiers` and METR-standard exporters is
deliberately cheap — the core stays thin so this stays easy.

## Adding a pack

1. New package with an `ef.packs` entry point.
2. Implement `TaskGenerator.generate(seed)`. **Build ground truth first**, derive the
   agent-visible files from it.
3. Subclass `BaseVerifier`, implement `check()` with a `Checklist`.
4. Inherit the contract tests in `tests/test_contracts.py`.
5. Pass the gate: `ef redteam <pack>/<task> --seeds 1,2,3` against the real backend.

Full walkthrough: [`prompts/build/08-pack-plugin-system.md`](../prompts/build/08-pack-plugin-system.md).

## Testing strategy

- **Contract tests** (`tests/test_contracts.py`) — protocol conformance, determinism, leak
  guarding, dimensional credit, verifier crash containment. Any pack inherits these.
- **Red-team tests** (`tests/test_redteam.py`) — the ship gate, plus a deliberately broken
  verifier proving the gate actually *catches* gameability rather than rubber-stamping.
- Both run against `LocalSandbox`, so CI needs no Docker daemon. Release gating uses Docker.
