# Frelease reviewer target

The audited remote `main` baseline was `0ab599f7bcde727bc4939ad6d1fc27d4efd1b150`; the checksum refresh did not itself fix provenance or finality. Source changes and reproducible steps are recorded in `REVIEWER_REMEDIATION.md`.

The corrected evaluator and finality-gated UI are implemented in this checkout. A fresh two-contract canonical pair is deployed on Studionet and its source parity, config, positive lifecycle, and wrong-commit rejection are recorded in `deployments/studionet.json`. The previous deployment remains historical only.

The correction is published at `806bd81289f8eb2d5001fedf216bb5ab8960d273`; GitHub Actions run [36608851753](https://github.com/BeatyXO/Frelease/actions/runs/36608851753) passed contracts and frontend. Browser lifecycle tests cover action eligibility and refresh logic; no injected wallet was available for signing transactions in the browser. The on-chain positive flow is verified: assessment finalized, Registry child finalized, Registry checkpoint and head confirm `ACTIVATED`. The live mismatch is verified as `COMMIT_MISMATCH` → `INCONCLUSIVE` → `BLOCKED`, with the positive policy head unchanged. Remaining owner-managed work is entering the documented public environment values in Vercel and redeploying production.
