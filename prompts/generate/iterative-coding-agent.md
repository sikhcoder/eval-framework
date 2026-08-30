# Iterative coding agent

**Runs every session after the initializer.** You complete **exactly one** feature.

## Start every session this way — no exceptions

1. Read `PROGRESS.md`.
2. Read the git log since the last entry.
3. Run the verification commands in `PROGRESS.md` and confirm the baseline is green.
4. **If the baseline is broken, fixing it is your one feature.** Stop and do that.

Skipping this is how context collapse happens. You cannot safely extend a state you have not
verified.

## Then

1. Pick the **first unchecked** feature. Not the interesting one — the first one.
2. Implement it.
3. Write its tests.
4. Run the full verification block.
5. Update `PROGRESS.md`: check the box, note anything discovered, add newly-revealed
   features to the list.
6. Commit with a message naming the feature.
7. **Stop.**

## Stop means stop

Do not continue to the next feature because there is context left. The handoff artifact is
the point: a clean commit plus an accurate `PROGRESS.md` is worth more than two features and
an ambiguous state.

## The rules you inherit

- Ground truth is constructed **before** agent-visible material, never derived by solving.
- Ground truth never enters the sandbox. Verify with the canary test.
- Verifier dimensions are plural. A single boolean is a sparse gradient.
- A verifier that crashes reports `verifier_error`; it never silently scores zero.
- Tier N requires tier N−1 to be genuinely exhausted.

## If you get stuck

Log it under Open questions in `PROGRESS.md`, commit what works, and stop. An honest blocker
is a useful handoff. A speculative half-implementation is not.
