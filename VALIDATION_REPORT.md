# Frelease validation report

## Verified repository state

GitHub validation completed against source commit `683ff7cbe1f579cb4ec0429e2d09b9817f1648bc` in CI run `36336956469` on 2026-09-27.

### Contracts

- Python syntax compilation: **PASS** for both contracts.
- Deterministic/source-invariant suite: **16 passed**.
- `genvm-lint check contracts/frelease_registry.py`: **PASS** — lint and validation passed; **11 methods (7 view, 4 write)**.
- `genvm-lint check contracts/frelease_evaluator.py`: **PASS** — lint and validation passed; **7 methods (5 view, 2 write)**.
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

No canonical Studionet deployment has been performed from this environment. Therefore the repository does **not** claim:

- FreleaseRegistry or FreleaseEvaluator contract addresses;
- deployment/configuration transaction IDs;
- deployed-source parity receipts or on-chain schema hashes;
- a finalized parent assessment + finalized registry child lifecycle;
- live stale-sequence/artifact-replay transaction evidence;
- a production frontend URL connected to canonical contract addresses.

Those are the remaining handoff tasks. No deployment receipt, address, hash or production URL is invented.
