# Initializer agent

**Runs once per pack.** Your job is scaffolding and planning — **not** implementation.

The most common failure here is trying to build the pack. Do not. A half-built pack with no
plan is worse than an empty one with a good plan, because the next session cannot tell what
is deliberate and what is unfinished.

## Read first

- `docs/ARCHITECTURE.md` — the three plug points
- `docs/VERIFIERS.md` — the tier ladder and the ship gate
- `packs/ef-pack-demo/` — the reference implementation
- The pack prompt in `prompts/packs/`

## Do

1. **Create the package** with an `ef.packs` entry point, mirroring `ef-pack-demo`.
2. **Write `TaskSpec`** — id, domain, instruction, sandbox spec, toolset, tier. The
   instruction must be precise about output format; ambiguity there shows up later as
   verifier/expert disagreement that is actually a task defect.
3. **Write `PROGRESS.md`** — the artifact that matters most. See below.
4. **Stub the generator and verifier** so imports resolve and `ef list` shows the task.
5. **Commit.** Clean baseline, nothing half-done.

## `PROGRESS.md` format

```markdown
# <pack>/<task>

## Status
Scaffolded. Generator and verifier are stubs.

## Design decisions
- Tier: 0 — ground truth from <source>, because <reason>
- Ground truth strategy: <how truth is constructed BEFORE agent-visible material>

## Features (atomic — one per session)
- [ ] 1. Seed data generator: <specific scope>
- [ ] 2. Error injection: <the catalogue>
- [ ] 3. Ground truth payload
- [ ] 4. Verifier dimension: <name>
- [ ] 5. Contract tests
- [ ] 6. Domain red-team policy: <the cheat this pack invites>
- [ ] 7. Gameability gate on Docker

## Verification
uv run pytest packs/ef-pack-<name> -q
uv run ef redteam <pack>/<task> --seeds 1,2,3

## Open questions
- <anything needing an expert>
```

Each feature must be completable in one session and leave the tests green. "Build the
generator" is not atomic. "Generate the chart of accounts and journal entries" is.

## Do not

- Implement features. That is the iterative agent's job.
- Write a generator that solves its own puzzle. Ground truth is constructed first, always.
- Leave the repo with failing tests.
