# Prompts

Working prompts for building eval-framework with Claude Code. Four groups:

| Directory | Purpose | Audience |
|---|---|---|
| `build/` | Sequential prompts for the public core | Engineers |
| `packs/` | One prompt per domain pack | Engineers |
| `expert/` | Structured elicitation turning practitioner judgment into verifier code | Lawyer, MDs, + an engineer |
| `generate/` | The recursive production engine — agents building environments | Automation |

Each prompt carries a **Status** line. `implemented` means M0 shipped it and the prompt is
for extending it; `not started` means it is the actual next piece of work.

## How to use one

```
Read prompts/build/09-redteam-harness.md and do what it says.
Read docs/VERIFIERS.md first — the tier ladder and the ship gate are non-negotiable.
```

## The two rules every prompt inherits

1. **Ground truth never enters the sandbox.** Build it first, derive agent-visible material
   from it, never the reverse.
2. **Nothing ships until `ef redteam` passes on the real backend.** A reward-hack policy
   scoring above zero is a defect report about us, not a result about the model.
