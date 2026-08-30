# Gold set provenance

**Goal:** every reference file has a recorded, reviewable source and license.
**Output:** `references/PROVENANCE.md`, one row per file.
**Gate:** no pack ships until this is clean and the lawyer has signed off.

## Why it gates shipping

Two independent failure modes:

1. **Legal.** A corpus we do not have the right to use contaminates every environment built
   on it, and the exposure lands on the buyer as well as us.
2. **Reproducibility.** A verifier whose answers depend on an unpinned upstream source is
   not auditable. If the answers change when a database updates, we cannot honor a claim
   about what a model scored last quarter.

Having a lawyer in-house makes this a same-week review rather than a quarter-long blocker.
Use it early — it gates wave 1, not wave 3.

## Required per file

| Field | Notes |
|---|---|
| Path | Relative to `references/` |
| Source | URL or system of record |
| License / terms | Explicit. "Public data" is not a license. |
| DUA status | Required, signed, N/A |
| Snapshot date | Pinned version or retrieval date |
| Reviewed by | The lawyer, dated |
| Redistribution | May this ship inside a customer bundle? |

That last column matters most: plenty of sources permit internal use but not redistribution,
and a bundle is redistribution.

## Hard lines

- **Never** Westlaw or Lexis content. Rule text is generally public; headnotes and editorial
  content are not, even where the underlying rule is.
- **No real PHI.** Synthetic first. MIMIC only under its DUA, and never in a shipped bundle.
- **No identifiable patient or client material from our own experts' practices.** This is
  the easiest way to turn a clean synthetic dataset into a HIPAA or privilege problem.
- **No customer's real books** in accounting packs.

## Process

1. Record the row **before** ingesting the file, not after.
2. Lawyer reviews in batches, weekly.
3. CI fails if a file under `references/` has no `PROVENANCE.md` row.
4. Anything unresolved goes to `references/QUARANTINE/`, which is git-ignored and never
   packaged.
