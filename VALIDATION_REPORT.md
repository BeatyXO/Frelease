# Frelease validation and deployment report

## Repository and CI

The most recent completed CI run before this report-only update is [36342835472](https://github.com/BeatyXO/Frelease/actions/runs/36342835472), successful for commit `5bd9f996a20bfd446fe8c150ebb490cff237e415` (2026-09-27). It includes the project's test/build workflow. Earlier detailed test counts were recorded for commit `683ff7cbe1f579cb4ec0429e2d09b9817f1648bc`, run `36336956469`: 16 deterministic tests, 10 Direct Mode tests, both GenVM lint/schema validations, and frontend install, typecheck and build all passed.

This Windows workspace has no Git metadata. A fresh `npm install --no-audit --no-fund` completed successfully. `npm run typecheck` and `npm run build` both passed locally, including a production build with `.env.local` set to the verified Studionet addresses and RPC/explorer endpoints. The environment file is git-ignored.

The built app was opened locally against Studionet and smoke-checked on `/`, `/releases`, `/policy/new`, the live policy detail, `/candidate/new`, the activated candidate detail and `/history/frelease-main-compat-2026`. The history displayed the finalized `ACTIVATED` sequence 1 record and the separate `BLOCKED / INCONCLUSIVE` sequence 2 record. At the browser's 394 px viewport, all checked routes rendered without horizontal overflow. This in-app browser has no injected `window.ethereum` provider, so wallet popover, reload reconnection, copy, disconnect and wrong-network switch could not be exercised interactively.

## Live Studionet deployment

`deployments/studionet.json` records the verified chain-61999 deployment. Registry and Evaluator deployment transactions, plus the one-time evaluator-binding transaction, reached `FINALIZED`. `get_config()` returned the deployed evaluator address and deployer owner. Both deployed source bodies fetched over RPC matched local source after line-ending normalization. The exposed schema counts match the CI-validated APIs: Registry 11 methods (7 view, 4 write), Evaluator 7 methods (5 view, 2 write). No schema hash is asserted.

## Live lifecycle

The positive candidate `frelease-docs-52fd697` binds source commit `52fd697e0528fee1545d2cd07c67967a40234a7d` and archive SHA-256 `21220bd0db846f64832d8934ab6d183a81605558ecb2a3f42ca9a24ae1deba33`. Its assessment parent and finalized-only Registry child both reached `FINALIZED`. The readback was verdict `COMPATIBLE`, checkpoint `ACTIVATED`, reason `FROZEN_POLICY_ACCEPTED_FINALIZED_VERDICT`, head sequence 1. Evidence receipts and snapshot/assessment digests are in the deployment JSON.

One duplicate-artifact attempt did not supply the recommended replay proof: evaluator verdict `INCONCLUSIVE`. Its finalized checkpoint was read back as `BLOCKED` with reason `VERDICT_NOT_ACTIVATABLE_BY_FROZEN_POLICY`; no `ARTIFACT_ALREADY_ACTIVATED` proof is claimed. A live stale-sequence proof has not been run.

## Current environment limits

- The selected deployer account remains configured in GenLayer CLI, but its private key is no longer unlocked in the OS keychain. No further wallet-signed transactions were attempted.
- Direct RPC reads required network-enabled execution. The canonical deployment, positive checkpoint/head, replay checkpoint and both deployed source bodies were retrieved and recorded.
- No Vercel project binding or production URL is configured in this repository. A production site deployment and interactive wallet smoke tests are not claimed.

## Vercel build follow-up

The Vercel build log provided after commit `378f1e3b0b0413ccab0feabeef23a1cc635f103d` shows the repository-root install followed by `cd web && npm run build`; Next compiled, then failed because the root install did not provide `@types/react` and `@types/node`. Those packages (plus `@types/react-dom`) are now declared in the root build manifest so the existing root-directory Vercel configuration installs the types needed by the `web` TypeScript build. This environment could not complete a fresh root `npm install`, so Vercel redeployment is still needed to verify the fix in its clean build environment.

## Verified repository state

GitHub validation was completed against source commit `683ff7cbe1f579cb4ec0429e2d09b9817f1648bc` in CI run `36336956469` on 2026-09-27, as recorded in the source manifest.

### Contracts

- Python syntax compilation: **PASS** for both contracts.
- Deterministic/source-invariant suite: **16 passed**.
- `genvm-lint check contracts/frelease_registry.py`: **PASS** — lint and validation passed; schema exposes **11 methods (7 view, 4 write)**.
- `genvm-lint check contracts/frelease_evaluator.py`: **PASS** — lint and validation passed; schema exposes **7 methods (5 view, 2 write)**.
- Direct Mode: **10 passed**.
- `scripts/release_check.py`: **RELEASE CHECK OK**.

The Direct Mode lifecycle suite covers one-time evaluator configuration, authorization, policy normalization, positive finalized activation, stale/out-of-order finalization, artifact replay blocking, policy-retirement blocking, duplicate evidence URLs, private/link-local evidence hosts and typed multi-origin manifests.

### Frontend

GitHub CI independently completed:

- `npm install --no-audit --no-fund`: **PASS**.
- `npm run typecheck`: **PASS**.
- `npm run build`: **PASS**.

The frontend implements the yellow/green release-rail design and the policy → candidate → assessment → finalized checkpoint/history flow. Wallet state is restored from the injected provider using `eth_accounts`, listens for account/chain changes, never caches an address as source of truth, and exposes the full address, **Copy wallet address**, network switching and **Disconnect** from the connected-wallet popover. A manual-disconnect opt-out prevents silent reload reconnection on wallets that do not support permission revocation.

## Not yet claimed

No canonical Studionet deployment has been performed from this environment. `deployments/studionet.json` is therefore intentionally absent; `deployments/studionet.example.json` is a schema example only. The repository does **not** claim:

- FreleaseRegistry or FreleaseEvaluator contract addresses;
- deployment/configuration transaction IDs;
- deployed-source parity receipts or on-chain schema hashes;
- a finalized parent assessment + finalized registry child lifecycle;
- live stale-sequence/artifact-replay transaction evidence;
- a production frontend URL connected to canonical contract addresses.

Those are the remaining handoff tasks. No deployment receipt, address, hash or production URL is invented.
