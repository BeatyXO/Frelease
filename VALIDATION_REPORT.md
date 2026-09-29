# Frelease validation and live remediation report

## Repository state

The reviewed upstream `main` baseline was commit `0ab599f7bcde727bc4939ad6d1fc27d4efd1b150`. It refreshed checksums, but did not implement provenance verification or connect transaction finality controls. This correction is being prepared in an actual checkout of that `main`. The correction commit and Actions result will be recorded after publication; neither is claimed before a successful push and verified workflow run.

## Local validation of the corrected files

- Python compile for all contracts: passed.
- `pytest -q tests/unit`: 24 passed.
- `pytest -q tests/direct`: 17 passed.
- `genvm-lint check contracts/frelease_registry.py` and `...frelease_evaluator.py`: three static checks pass each; overall tool exits nonzero because loading the SDK cache fails with Windows `WinError 5: Access is denied`.
- `npm install`: passed.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `python scripts/release_check.py`: `RELEASE CHECK OK`.
- `npm run test:lifecycle`: eight lifecycle tests (`npm run test:lifecycle` from `web`).

## Corrected canonical Studionet pair

`deployments/studionet.json` records the new Registry and Evaluator, finalized deployment and one-time configuration receipts, local source SHA-256 values, RPC-fetched source parity, and fresh candidate lifecycle. The prior pair is explicitly historical and not canonical.

## Live positive and negative lifecycle

Candidate `papito-positive-v3-20260929` registered commit `7c94b1e9a8f47f1aa173f53e2a78b877c93494b0`, artifact `4f2f7f1c870cc223e780f6ee5027fb3938f88678858436909471014c8e762f52`. The fetched immutable build manifest matched both. Assessment transaction `0x4544c6e7c834bd058bc8cafa51f8c116a21c92b6fed24ea46d7678ea69bbeebc` and Registry child `0x4f9c28fbad17e1a7fcf36aae53104bfe92913797e2192b253d9668e02de6b501` reached `FINALIZED`. Readback confirmed checkpoint `ACTIVATED`, reason `FROZEN_POLICY_ACCEPTED_FINALIZED_VERDICT`, sequence 1 policy head.

Candidate `papito-wrong-commit-v3-20260929` registered `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` while retaining the correct artifact. Fetched provenance reported commit `7c94b1e9a8f47f1aa173f53e2a78b877c93494b0`; the evaluator recorded `COMMIT_MISMATCH`, `verified: false`, and `INCONCLUSIVE`. Its Registry child reached finality; checkpoint readback is `BLOCKED`, reason `VERDICT_NOT_ACTIVATABLE_BY_FROZEN_POLICY`; head remains the positive sequence 1. Negative assessment transaction `0xddfb946bdb0aa09eeb5113f043e6f42a7b22c2467b480a18dab1b2d24162cbe8` and Registry child `0x4800a61487010099ddc7021e876f6f1841ce8e09d95c7b252907550571683d9a` both finalized.

## Remaining verification

A push to `main` and a corresponding GitHub Actions run have not yet happened. The live positive and blocked candidate pages were opened locally against the corrected addresses and visibly showed `ACTIVATED`/`COMPATIBLE`/`VERIFIED` versus `BLOCKED`/`INCONCLUSIVE`/`COMMIT_MISMATCH`. No injected wallet was available, so wallet-driven finalize/appeal interaction and a production frontend deployment are not claimed. The code exposes Finalize at `READY_TO_FINALIZE`, Appeal when eligible (including bond handling), and re-reads transaction/checkpoint/head after action; five testable lifecycle cases exercise the activation gate. Full SDK lint is blocked only at SDK cache loading, after each contract's three static checks passed.
