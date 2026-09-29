# Frelease reviewer target

The audited remote `main` baseline was `0ab599f7bcde727bc4939ad6d1fc27d4efd1b150`; the checksum refresh did not itself fix provenance or finality. Source changes and reproducible steps are recorded in `REVIEWER_REMEDIATION.md`.

The corrected evaluator and finality-gated UI are implemented in this checkout. A fresh two-contract canonical pair is deployed on Studionet and its source parity, config, positive lifecycle, and wrong-commit rejection are recorded in `deployments/studionet.json`. The previous deployment remains historical only.

Outstanding handoff items: publish the correction to `main` and verify GitHub Actions; complete full SDK schema validation once Windows cache access is corrected. Browser lifecycle tests cover action eligibility and refresh logic; no injected wallet was available for signing transactions in the browser. The on-chain positive flow is verified: assessment finalized, Registry child finalized, Registry checkpoint and head confirm `ACTIVATED`. The live mismatch is verified as `COMMIT_MISMATCH` → `INCONCLUSIVE` → `BLOCKED`, with the positive policy head unchanged.
