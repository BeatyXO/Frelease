# Papito review remediation record

## Current status

The deterministic provenance implementation, candidate finality actions, and finality-gated activation UI are present in this correction set. The audited remote `main` baseline was `0ab599f7bcde727bc4939ad6d1fc27d4efd1b150`; implementation correction is `5bfb077d81d17fee53df58407f25795029afaf25`. The current published head before this cleanup is `806bd81289f8eb2d5001fedf216bb5ab8960d273`. The corrected pair and fresh positive/negative lifecycle have been verified on Studionet. GitHub Actions run [36608851753](https://github.com/BeatyXO/Frelease/actions/runs/36608851753) passed both jobs.

The root Vercel configuration now installs and builds the Next.js application from `web/`. The Vercel dashboard environment values remain owner-managed and require a production redeployment after the canonical public RPC, explorer, Registry and Evaluator values are entered.

A fresh corrected two-contract pair is deployed and configured on Studionet. See `deployments/studionet.json` for addresses, source hashes, finalized deployment/configuration transactions, candidate evidence, assessment and Registry child status. The previous pairs are listed under `noncanonical_pairs` as historical and are not designated canonical.

## Changed repository paths

- `contracts/frelease_evaluator.py` — parses fetched provenance document fields deterministically, compares both fields against the frozen candidate, records expected/observed values/status, and forces unverified evidence to `INCONCLUSIVE`.
- `tests/direct/test_frelease_evaluator.py` — behavioral match, per-field/both-field mismatch, missing and malformed provenance tests, plus evidence URL and consensus coverage.
- `tests/unit/test_policy_rules.py` and `tests/unit/test_source_invariants.py` — deterministic parsing/URL and lifecycle architecture checks.
- `web/lib/write-pipeline.ts` — `inspectTx`, `finalizeTx`, `appealTx`, lifecycle and Registry checkpoint/head activation predicate.
- `web/app/candidate/[candidateKey]/page.tsx` — Finalize and eligible Appeal actions, wallet/network/error/loading handling, refresh after action, and explicit lifecycle/activation labels.
- `web/candidate-lifecycle.test.ts`, `web/package.json`, `web/package-lock.json`, `.github/workflows/ci.yml` — lifecycle behavior tests, Vitest runner script/dependency, and CI test step.
- `README.md`, `REVIEW_TARGET.md`, `SUBMISSION_CHECKLIST.md`, `VALIDATION_REPORT.md`, `deployments/studionet.json`, `REVIEWER_REMEDIATION.md` — corrected claims and reproducible reviewer evidence.

## Reproduce provenance checks

From repository root:

```powershell
pytest -q tests/direct/test_frelease_evaluator.py
pytest -q tests/unit/test_policy_rules.py -k provenance
```

Direct Mode includes fetched-document cases for exact match (`VERIFIED`), wrong commit (`COMMIT_MISMATCH`), wrong artifact (`ARTIFACT_MISMATCH`), both wrong, missing fields, malformed JSON, and fail-closed `INCONCLUSIVE`. The submitted evidence manifest contains only URLs and notes; identity claims are read from fetched content. For an end-to-end live result inspect `deployments/studionet.json`: the positive candidate has both expected/observed fields equal and `VERIFIED`; `papito-wrong-commit-v3-20260929` registers `a…a` while the fetched immutable manifest reports `7c94…`, yielding `COMMIT_MISMATCH`, `INCONCLUSIVE`, and a `BLOCKED` checkpoint with the policy head unchanged.

## Reproduce finality and activation

1. On Studionet 61999, register the frozen policy and candidate against the new Evaluator/Registry in `deployments/studionet.json`.
2. Submit `assess_candidate`; observe provisional consensus and then `READY_TO_FINALIZE` when the protocol reaches that state. The candidate UI exposes **Finalize assessment** there. If GenLayer reports appeal eligibility, it exposes **Appeal assessment** and uses `appealTx` with the required bond.
3. After either action the page re-reads the transaction and refreshes candidate/checkpoint/head. `COMPATIBLE`, provisional/accepted, `READY_TO_FINALIZE`, or a finalized semantic result without its Registry checkpoint never renders `ACTIVATED`.
4. Positive live proof: assessment `0x4544c6e7c834bd058bc8cafa51f8c116a21c92b6fed24ea46d7678ea69bbeebc` and Registry child `0x4f9c28fbad17e1a7fcf36aae53104bfe92913797e2192b253d9668e02de6b501` both finalized; Registry checkpoint/head readback is `ACTIVATED`, sequence 1.
5. Negative live proof: the wrong-commit assessment readback is `INCONCLUSIVE`; its finalized Registry checkpoint is `BLOCKED` and the policy head remains the positive candidate. The wrong-commit assessment is `0xddfb946bdb0aa09eeb5113f043e6f42a7b22c2467b480a18dab1b2d24162cbe8`; its finalized Registry child is `0x4800a61487010099ddc7021e876f6f1841ce8e09d95c7b252907550571683d9a`.

## Validation observed

- `python -m py_compile` over `contracts/*.py`: passed.
- `pytest -q tests/unit`: 24 passed.
- `pytest -q tests/direct`: 17 passed.
- `genvm-lint check` for both contracts: 3 static checks pass per contract; overall validation exits nonzero because the SDK cache cannot be read (`WinError 5: Access is denied`).
- `npm install`: passed; `npm run typecheck`: passed; `npm run build`: passed.
- `python scripts/release_check.py`: `RELEASE CHECK OK`.
- GitHub Actions run `36608851753` passed: contracts and frontend jobs both succeeded, including GenVM lint, Direct Mode, typecheck, lifecycle tests and production build.
