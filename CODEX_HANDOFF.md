# Codex handoff — finish Frelease to reviewer-ready state

You are taking over a substantially implemented GenLayer project named **Frelease** in the existing repository `BeatyXO/Frelease`. Do not return only a plan, checklist, commentary or mockup. Inspect the entire repository first, preserve the product thesis and two-contract architecture unless a real GenLayer runtime failure proves a change is necessary, then finish the repository in place and push validated work to `main`.

## Product thesis

Frelease is a software/protocol release compatibility and activation primitive, not a scientific replication project and not a generic “AI decides X” demo.

There are intentionally **two contracts**:

1. `contracts/frelease_registry.py` freezes immutable compatibility policies and policy digests; owns evaluator authorization; owns finalized activation checkpoints and canonical release heads; and deterministically enforces activatable verdicts, active-policy status, monotonic release sequence and artifact replay protection.
2. `contracts/frelease_evaluator.py` binds candidate policy/sequence/version/source commit/artifact SHA-256 before assessment; validates typed HTTPS evidence and origin policy; has leader/validators independently fetch bounded evidence windows; hashes exact evidence windows and aggregate receipt snapshot; compares material semantic fields, not JSON shape alone; and emits `register_finalized_assessment(...)` to the registry with `on="finalized"`.

Do **not** split deterministic activation into a third contract unless the GenLayer runtime makes the current two-contract design impossible.

## Already verified offline

- `python -m py_compile contracts/*.py` — PASS.
- `pytest -q tests/unit` — **16 passed**.
- `python scripts/release_check.py` — `RELEASE CHECK OK`.
- Current `.ts`/`.tsx` files parse successfully with TypeScript syntax transpilation.

The build sandbox could not reach PyPI/npm, so GenLayer dev dependencies and frontend packages were not installed here. Direct Mode is authored but is **not claimed as passing yet**.

## Finish all remaining work

1. Install dependencies and run Python compile, 16+ unit tests, GenVM lint for both contracts, all Direct Mode tests, and `scripts/release_check.py`. Fix real compatibility/runtime bugs without weakening invariants.
2. In `web`, run `npm install`, `npm run typecheck`, and `npm run build`; fix actual Next/TypeScript/genlayer-js mismatches while preserving the yellow/green UI.
3. Preserve wallet behavior: injected wallet only; reload restores authorized account via `eth_accounts`; no cached address as truth; `accountsChanged`/`chainChanged`; clicking connected wallet opens full address, **Copy wallet address**, network switch when needed, **Disconnect**; manual disconnect opt-out persists until reconnect.
4. Deploy only to GenLayer Studionet chain 61999: registry → evaluator(registry) → finalized `set_evaluator_once`; verify config and deployed-source parity. Record real addresses, deployment/config tx IDs, source hashes and schema hashes/method counts if available.
5. Run a positive live lifecycle using real public HTTPS evidence from at least two independent origins: register policy; register candidate with exact source commit + artifact SHA-256; assess; prove parent assessment reaches `FINALIZED`; record evidence receipts/snapshot digest/finding/assessment digest; locate and prove finalized registry child; read checkpoint + policy head showing activation only after child finality.
6. Run strong negative paths: activate newer sequence then finalize an older compatible candidate and prove `STALE_OR_NON_MONOTONIC_SEQUENCE` with no rollback; replay an already-activated artifact digest and prove `ARTIFACT_ALREADY_ACTIVATED`; if practical also prove policy retirement blocks an in-flight activation.
7. Configure the frontend with the two canonical addresses, deploy if Vercel access exists, and smoke-test all routes plus wallet reload/copy/disconnect/wrong-network/mobile behavior. Never present provisional evaluator state as activated; activation comes from registry state only.
8. Update README, VALIDATION_REPORT, DEPLOYMENT_RUNBOOK, SUBMISSION_CHECKLIST, REVIEW_TARGET, SOURCE_CHECKSUMS, SOURCE_MANIFEST and `deployments/studionet.json` using only verified facts. Push final validated `main`.

Final report must include final commit SHA, test counts, GenVM lint status, Registry/Evaluator CAs and deploy txs, evaluator configuration tx, source/schema parity, positive lifecycle txs/digests, negative lifecycle evidence, frontend URL/status, and only genuine remaining blockers. Never invent receipts or hashes.
