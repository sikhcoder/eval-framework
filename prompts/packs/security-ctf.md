# Pack: security / ctf  (wave 2)

**Status:** queued. **Tier:** 0. **Repo:** private.

## The task

Deterministic security work with binary outcomes: capture the flag, patch the vulnerability,
identify the malicious commit in a diff.

## Why it fits

Success is unambiguous by construction — the flag is captured or it is not, the exploit
stops working or it does not. No judgment, no rubric.

## The generator

Inject a known vulnerability class into a synthetic service, or generate a challenge with a
seeded flag. Ground truth is the flag or the vulnerability location.

## The verifier (tier 0)

- `flag_captured` — exact match
- `vulnerability_patched` — the exploit no longer succeeds against the patched service
- `service_still_works` — the functional test suite still passes

The third dimension is essential. Without it, `rm -rf` on the vulnerable service scores as a
successful patch — a degenerate solution RL will find immediately.

## Scope

Defensive and evaluative only: patching, detection, and analysis of synthetic targets we
control. No tooling aimed at systems we do not own.
