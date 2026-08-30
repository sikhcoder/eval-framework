# Verifiers

> The most important document in this repository. Everything else is plumbing.

A verifier decides whether an agent succeeded. It is the only part of an RL environment
that cannot be bought, borrowed, or open-sourced away — and it is the thing we sell.

## Why this is the whole business

A frontier lab spends on the order of **$2,400 of compute across the lifetime of a single RL
task** ([unverified] — from the Mechanize essay *Cheap RL tasks will waste compute*). If the
reward signal is weak or gameable, that compute produces a model that learned to cheat.

Labs currently have no way to tell a sound verifier from a gameable one before spending the
money. Nobody sells *verified verifiers*. That gap is our wedge.

## The tier ladder

Tiers are ordered by how much of the reward comes from an authority rather than an opinion.

| Tier | Name | Mechanism | Ships alone? |
|---|---|---|---|
| **0** | Deterministic | Exact match, unit tests, balance checks, frame/trace equality | Yes |
| **1** | Structural | Resolves against an authority: citation exists, filing validates, code is legal for the diagnosis | Yes |
| **2** | Reference-chain | Gold document decomposed into independently scored dimensions (RLVRR) | Yes, with caveats |
| **3** | Calibrated judge | Model judge with measured human agreement | **Never** |

**The rule: a pack may not use tier N until it has exhausted tier N−1.**

This rule exists because tier drift is the most common way a good environment silently
rots. A task starts as "check the number," someone finds an awkward edge case, and it
quietly becomes "check that the output mentions the number" — which the output-mimic policy
will pass without doing any work at all.

### On tier 3

A model judge is not forbidden, it is *insufficient*. If a pack ships a tier-3 dimension it
must also publish the human agreement rate on a held-out sample, and that dimension may
never be the sole contributor to a score. An unaudited LLM judge is a plausible-sounding
random number generator.

## Dimensional credit is mandatory

`Reward.dimensions` is required, not optional. A single boolean gives a sparse gradient and
teaches the model nothing about *why* it failed. A run that finds every unbalanced entry but
fluffs one total is genuinely more correct than one that finds nothing, and the reward must
say so.

Use `Checklist` from `ef.verify.scoring`: add named checks with weights, and the framework
folds them into a `Reward` with per-check dimensions for free.

## The two invariants

### 1. Ground truth never enters the sandbox

If the agent can read the answer, a perfect score means nothing.

The framework enforces this structurally rather than by convention:

- `TaskInstance.ground_truth` is `exclude=True`, so `model_dump()` and `model_dump_json()`
  omit it by default.
- `public_manifest()` is the only sanctioned path for material into a sandbox.
- Every `GroundTruth` carries a **canary** — a random token. `ef.verify.leak.find_leak`
  searches the agent's transcript and written files for it. A canary sighting is reported as
  `verifier_error`, *not* as an agent failure, because it is our bug and not the model's.

Generators must construct ground truth **first** and derive the agent-visible material from
it. Deriving truth the other way — by solving your own puzzle — makes the verifier only as
trustworthy as the solver. That is precisely how gameable environments get built.

### 2. A crashing verifier is never scored as an agent failure

`BaseVerifier` catches exceptions from `check()` and reports them as `verifier_error`. A
verifier that throws and gets recorded as "the model failed" silently poisons a training run
with false negatives — the most expensive possible bug, because it looks like data.

Verifiers must also never touch the network. A verifier that makes a network call is not
reproducible and cannot be audited.

## The ship gate: the Gameability Report

Every environment ships with the results of running five adversarial policies against our
own verifier, across multiple seeds.

| Policy | What it does | Defect it finds |
|---|---|---|
| `null` | Nothing at all | Verifier credits the starting state, or scores an absent artifact as vacuously correct |
| `test-tamper` | Neuters tests, conftest, Makefile targets | Verifier reads assertions from *inside* the sandbox |
| `oracle-search` | Greps files, env, git history for the answer | Generator leaked ground truth |
| `output-mimic` | Emits right-shaped output with fabricated values | Verifier checks format instead of values — the classic tier-1 drift |
| `overfit` | Replays values harvested from a prior run | The answer does not actually vary with the seed |

**Gate: every policy must score at or below threshold (default 0.05) on every seed.**

```bash
uv run ef redteam <pack>/<task> --seeds 1,2,3
```

Exits non-zero on any exploit. A policy scoring above zero is never an interesting result
about the model — it is a defect report about us.

Multiple seeds matter: a policy scoring zero on one seed and high on another has found a
generator that is not randomizing what it claims to randomize.

Run the gate against the **real backend** before release. `--sandbox local` is for fast
iteration only; isolation differences change what a policy can reach.

## Writing a verifier

Subclass `BaseVerifier` and implement `check()`. Leak guarding, crash containment, and
reward assembly come from the template.

```python
class LedgerVerifier(BaseVerifier):
    tier = VerifierTier.DETERMINISTIC

    def check(self, instance, trace, checklist):
        truth = instance.ground_truth.payload
        raw = trace.final_files.get("corrections.json")
        if raw is None:
            checklist.add("submitted", False, detail="corrections.json not written")
            return
        checklist.add("submitted", True)
        parsed = json.loads(raw)
        checklist.add(
            "entries_correct",
            sorted(parsed["unbalanced_entries"]) == truth["unbalanced_entries"],
            weight=2.0,
        )
```

See `packs/ef-pack-demo` for the complete reference implementation.

## Checklist before shipping any environment

- [ ] Tier is the lowest that the domain actually permits
- [ ] `dimensions` carries more than one signal
- [ ] Ground truth constructed before agent-visible material, never after
- [ ] Canary absent from every generated file (`test_ground_truth_absent_from_sandbox_files`)
- [ ] Answer varies across seeds (`test_different_seeds_differ`)
- [ ] Verifier makes no network calls
- [ ] Gameability Report passes on the real backend, ≥3 seeds
- [ ] For tier 2–3: expert agreement rate measured and published
