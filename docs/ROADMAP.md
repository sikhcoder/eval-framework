# Roadmap

| Milestone | Content | Gate |
|---|---|---|
| **M0** ✅ | Repos, docs, prompts, core packages, demo pack, CI | `uv sync`, `pytest`, `ruff`, `pyright` all green; demo pack passes its own red-team |
| **M1** | Accounting month-end close, end to end | Gameability Report passes on Docker, ≥3 seeds |
| **M2** | Core generalized from M1; **wave 1 packs land** — legal docket deadlines, legal citation verification, medical coding, software replication | Same gate per pack, **plus** expert agreement rate published |
| **M3** | Insurance adjudication, security/CTF | Same gate |
| **M4** | Medical prior-auth and denials; tax computation; scale generators to thousands of variants per pack | Same gate |
| **M5+** | Tier 2: contract-vs-playbook redline, clinical reasoning | Gate plus measured human agreement (κ) |

## M0 — complete

Core interfaces are real, not stubs. The demo pack (`demo/ledger-balance`) is a working
tier-0 environment that passes the full five-policy red-team against Docker, and the test
suite includes a deliberately broken verifier proving the gate *catches* gameability rather
than rubber-stamping.

## M1 — month-end close

Container with a synthetic company's messy books: Postgres ledger, bank statements,
invoices, FX rate table. One instruction: reconcile, post adjusting entries, produce a trial
balance and financial statements.

The generator starts from known-correct books and injects specific errors. Ground truth is
exact and free. Verifier is tier 0: debits equal credits, each injected error found or not
(dimensional credit per error), final trial balance ties to the penny. No model judge
anywhere in the loop.

Done when:
```bash
uv run ef generate accounting/month-end-close --seed 42
uv run ef run      accounting/month-end-close --seed 42 --agent claude
uv run ef redteam  accounting/month-end-close --seeds 1,2,3   # the gate
uv run ef export   accounting/month-end-close --fmt inspect
```

## M2 — wave 1

All four packs sit at tier 0/1 and share M1's verifier machinery, so the engineering is
near-identical. What differs is the generator and the gold data — expert work that proceeds
in parallel with M1 engineering, starting now via [`prompts/expert/`](../prompts/expert/).

Two extra gates the generic harness cannot check:

- **Expert agreement.** Lawyer and MDs independently score a held-out sample. Every
  verifier-vs-expert disagreement is triaged and becomes a regression test. The agreement
  rate is published — it is a selling point, and a low one is a defect signal.
- **Provenance clean.** Every file under `references/` has a recorded source and license,
  signed off before packaging.

## Sequencing rule

**If M1's red-team gate does not hold, M2 does not start.** Four packs built on a broken
pattern is four times the rework. The only reason parallel domains are safe is that they
reuse machinery already proven against adversarial pressure.

Likewise, tier-2 work waits. Experts make tier 2 *possible*; they do not make it cheap.
