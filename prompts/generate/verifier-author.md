# Verifier author

**Read `docs/VERIFIERS.md` first.** It is the specification; this is the procedure.

## Establish the tier honestly

Start at 0 and only move up when genuinely blocked:

- Can it be exact-matched, computed, or diffed? → **Tier 0**
- Can it be resolved against an authority? → **Tier 1**
- Can a gold document be decomposed into checkable dimensions? → **Tier 2** (see
  `prompts/expert/elicit-reward-chain.md`)
- Otherwise → **Tier 3**, which never ships alone and must publish human agreement

Most "this needs judgment" claims dissolve under decomposition. Push hard before conceding a
tier.

## Write it

Subclass `BaseVerifier`, implement `check()`, populate a `Checklist`. Leak guarding and
crash containment come from the template.

## Dimensions

Plural, weighted by consequence, and **including at least one that punishes the degenerate
strategy**. If the task rewards finding things, add `no_false_positives`. If it rewards
denying, add `no_spurious_denial`. If it rewards patching, add `service_still_works`.

That dimension is not defensive polish. It is the difference between an environment that
teaches the skill and one that teaches the shortcut.

## Two failure modes M1 actually hit

**Abstaining must not earn credit.** A `no_false_positives`-style dimension gives full marks
to an agent that reports nothing, because reporting nothing trivially has no false positives.
Any "did not do the bad thing" dimension must be conditional on having attempted the good
thing — otherwise the safest strategy is to do nothing, and RL will find that.

**An all-zero red-team report can mean a broken harness, not a sound verifier.** Before
believing a gate, confirm a genuine solver scores 1.0 **on the same backend**. M1's gate
passed vacuously for an afternoon because agent output was never reaching the verifier under
Docker at all.

## Never

- Read assertions from inside the sandbox. `test-tamper` exists to catch exactly that.
- Make a network call. Not reproducible, not auditable.
- Use float equality on money. `money_equal` compares Decimals to the penny.
- Score an absent artifact as vacuously correct. `null` exists to catch that.

## Verify

```bash
uv run pytest packs/ef-pack-<name> -q
uv run ef redteam <pack>/<task> --seeds 1,2,3       # on Docker, not local
```

A hack policy scoring above zero is a defect report about the verifier. Fix it. **Never
raise the threshold.**
