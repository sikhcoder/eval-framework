# Difficulty calibrator

**Goal:** put a task in a band where the reward signal actually carries information.

## The band

Target roughly **20–70% pass rate** for a current frontier model.

- Near 0%: the task is broken or underspecified, not hard. Almost every gradient is zero and
  the environment teaches nothing.
- Near 100%: spent. No signal left.
- A **bimodal** distribution usually means two different tasks wearing one name — split it.

## Procedure

1. Run N ≥ 20 seeds with a real model.
2. Record score distribution and per-dimension pass rates.
3. Inspect the failures. Are they failing the skill, or failing to understand the
   instruction? **Instruction failures are task defects, not difficulty.** Fix the wording
   before touching difficulty.
4. Tune with the generator's difficulty knobs — number of injected errors, proximity to
   boundaries, distractor density, horizon length.
5. Re-run the red-team gate. Difficulty changes can open exploits.

## Per-dimension calibration

A dimension that always passes contributes nothing and should be dropped or hardened. A
dimension that never passes is either broken or measuring something the instruction never
asked for. Check both before assuming the model is at fault.

## Build a curriculum, not a difficulty

Ship graded variants — easy, medium, hard — from the same generator. A curriculum is worth
more than the sum of its tasks and is much harder for a buyer to replicate piecemeal.

## Record it

Difficulty stats go in the bundle. A buyer needs to know what pass rate to expect; a task
with no reported difficulty is a task they cannot plan a training run around.
