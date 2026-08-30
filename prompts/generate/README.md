# The generation engine

Prompts for using agents to build environments — the recursive play in §7 of the memo: use
advanced agents to engineer the environments that train the next generation of agents.

## The context-collapse problem

Agents building complex software over long horizons try to finish in one shot, exhaust
context, and leave the repo broken and undocumented. The next session starts from rubble.

The fix (memo §7.4) is a **two-agent split** with enforced state handoff:

1. `initializer-agent.md` runs **once**. It sets up the repo, git history, and an atomic
   feature list in `PROGRESS.md`.
2. `iterative-coding-agent.md` runs **every subsequent session**. It reads `PROGRESS.md` and
   the git log first, verifies the baseline still works, and completes **exactly one**
   feature before stopping.

The discipline is the whole point: one feature, one commit, `PROGRESS.md` updated, stop.

## Roles

| Prompt | Role |
|---|---|
| `initializer-agent.md` | Scaffolds a pack, writes the feature list |
| `iterative-coding-agent.md` | Completes one atomic feature per session |
| `task-author.md` | Designs a task and its generator |
| `verifier-author.md` | Writes the verifier |
| `redteam-reward-hacker.md` | Attacks our own verifier |
| `difficulty-calibrator.md` | Tunes difficulty to a useful band |
| `packager.md` | Assembles the customer bundle |
