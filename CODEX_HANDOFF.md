# Codex handoff — finish Frelease to reviewer-ready state

You are taking over a substantially implemented and CI-green GenLayer project named **Frelease** in the existing repository `BeatyXO/Frelease`. Do not return only a plan, checklist, commentary or mockup. Inspect the entire repository first, preserve the product thesis and two-contract architecture unless a real GenLayer runtime/deployment failure proves a change is necessary, then finish the repository in place and push validated work to `main`.

## Product thesis

Frelease is a software/protocol release compatibility and activation primitive, not a scientific replication project and not a generic “AI decides X” demo.

There are intentionally **two contracts**:

1. `contracts/frelease_registry.py`
   - freezes immutable compatibility policies and policy digests;
   - owns evaluator authorization;
   - owns finalized activation checkpoints and canonical release heads;
   - deterministically enforces activatable verdicts, active-policy status, monotonic release sequence and artifact replay protection.

2. `contracts/frelease_evaluator.py`
   - binds candidate policy/sequence/version/source commit/artifact SHA-256 before assessment;
   - validates typed HTTPS evidence and origin policy;
   - has leader/validators independently fetch bounded evidence windows;
   - hashes exact evidence windows and aggregate receipt snapshot;
   - compares material semantic fields and the full receipt set, not JSON shape alone;
   - emits `register_finalized_assessment(...)` to the registry with `on="finalized"`.

Do **not** split deterministic activation into a third contract unless the real GenLayer runtime makes this architecture impossible. The two-contract shape is a deliberate simplification and differentiation.

## Already verified in GitHub CI

Validation completed against source commit `683ff7cbe1f579cb4ec0429e2d09b9817f1648bc` in GitHub Actions run `36336956469`:

- Python contract compilation — **PASS**.
- deterministic/source-invariant suite — **16 passed**.
- GenVM lint + validation — **PASS** for both contracts.
  - `FreleaseRegistry`: 11 methods (7 view, 4 write).
  - `FreleaseEvaluator`: 7 methods (5 view, 2 write).
- Direct Mode — **10 passed**.
- `python scripts/release_check.py` — **RELEASE CHECK OK**.
- frontend dependency installation — **PASS**.
- frontend TypeScript typecheck — **PASS**.
- frontend production build — **PASS**.

Do not spend the handoff rebuilding architecture that is already green. Re-run these checks after substantive changes, but focus primarily on canonical Studionet deployment, real lifecycle evidence, deployed-source parity, production configuration and reviewer-proof documentation.

## 1. Preserve the green baseline

From repo root, rerun after any substantive contract change:

```bash
pip install -r requirements.txt
python -m py_compile contracts/*.py
pytest -q tests/unit
genvm-lint check contracts/frelease_registry.py
genvm-lint check contracts/frelease_evaluator.py
pytest -q tests/direct
python scripts/release_check.py
```

Frontend:

```bash
cd web
npm install
npm run typecheck
npm run build
```

Do not weaken substantive invariants merely to keep tests green. Preserve the yellow/green visual language and the current product flow.

## 2. Preserve and live-test wallet behavior

This is important:

- injected wallet only;
- on browser reload, query `eth_accounts` and restore the actually-authorized injected account instead of losing connection;
- never store an address as fake source of truth;
- keep `accountsChanged` and `chainChanged` listeners;
- clicking the connected wallet must open a popover with the full address, **Copy wallet address**, network switch when needed, and **Disconnect**;
- manual disconnect opt-out may be persisted so wallets without `wallet_revokePermissions` do not silently reconnect after reload;
- reconnect clears that opt-out.

The implementation is already present and builds. Verify it in the deployed frontend rather than replacing it gratuitously.

## 3. Deploy to GenLayer Studionet only

Target chain ID **61999**.

Use `deploy/deployScript.ts` or equivalent validated GenLayer tooling:

1. deploy `FreleaseRegistry`;
2. deploy `FreleaseEvaluator(registry_address)`;
3. call `registry.set_evaluator_once(evaluator_address)`;
4. finalize all deployment/configuration transactions;
5. verify `registry.get_config()` reads the exact evaluator address;
6. verify deployed source parity for both contracts;
7. record source hashes, schema hashes/method counts if exposed, addresses and all deployment/configuration tx IDs in `deployments/studionet.json` and `VALIDATION_REPORT.md`.

Never invent a receipt or hash.

## 4. Execute a strong live positive lifecycle

Use real public HTTPS evidence from at least **two independent origins** where possible.

Create one policy with a protected API/protocol surface, clear compatibility rule, required evidence kinds such as `CHANGELOG`, `API_SURFACE`, `TEST_REPORT`, `BUILD_MANIFEST`, `min_distinct_origins >= 2`, and activatable verdicts chosen before assessment.

Then:

1. register candidate sequence N with exact source commit + artifact SHA-256;
2. assess with typed public evidence;
3. capture the parent assessment tx and prove it reaches `FINALIZED`;
4. capture evidence receipts, `evidence_snapshot_digest`, semantic finding and `assessment_digest`;
5. locate the finalized-only registry child transaction produced by parent finalization;
6. prove the child reaches `FINALIZED`;
7. read `get_checkpoint(policy:candidate)` and `get_policy_head(policy)` to prove activation occurs only after child finality.

Do not call a provisional/accepted evaluator result an activated release.

## 5. Execute the reviewer-grade negative paths

At minimum capture real evidence for:

**Out-of-order stale finalization**
- activate a newer sequence;
- then process/finalize an older compatible candidate;
- prove the registry records it `BLOCKED` with `STALE_OR_NON_MONOTONIC_SEQUENCE`;
- prove the newer policy head remains unchanged.

**Artifact replay**
- use a newer candidate with an artifact SHA-256 already activated under the same policy;
- prove the checkpoint becomes `BLOCKED` with `ARTIFACT_ALREADY_ACTIVATED`.

Also run if practical:

**Retirement race**
- begin a candidate while policy is active;
- retire the policy;
- let the assessment finalize;
- prove `POLICY_RETIRED_BEFORE_FINAL_ACTIVATION`.

Do not manufacture these records; capture real transactions and canonical readbacks.

## 6. Production frontend proof

Configure:

```text
NEXT_PUBLIC_FRELEASE_REGISTRY_ADDRESS=0x...
NEXT_PUBLIC_FRELEASE_EVALUATOR_ADDRESS=0x...
NEXT_PUBLIC_GENLAYER_RPC_URL=https://studio.genlayer.com/api
NEXT_PUBLIC_GENLAYER_EXPLORER=https://explorer-studio.genlayer.com
```

Deploy the frontend if project/Vercel access exists. Smoke-test:

- home page;
- `/releases`;
- create policy flow;
- create candidate flow;
- policy detail/current head;
- candidate evidence/assessment flow;
- finalized checkpoint display;
- `/history/[policyKey]`;
- wallet reload persistence;
- wallet popover copy-address and disconnect;
- wrong-network switch;
- mobile/responsive layout.

Activation history must come from registry state only.

## 7. Final documentation and push

Update, using only verified facts:

- `README.md`
- `VALIDATION_REPORT.md`
- `DEPLOYMENT_RUNBOOK.md`
- `SUBMISSION_CHECKLIST.md`
- `REVIEW_TARGET.md`
- `SOURCE_CHECKSUMS.txt`
- `SOURCE_MANIFEST.json`
- `deployments/studionet.json`

Run every check one final time and push final validated `main`.

Your final report must include:

- final commit SHA;
- unit + Direct Mode test counts;
- GenVM lint status;
- Registry CA + deploy tx;
- Evaluator CA + deploy tx;
- evaluator configuration tx;
- deployed-source/schema parity status;
- live positive lifecycle tx IDs/digests/readbacks;
- stale/replay negative lifecycle evidence;
- frontend production URL/status;
- only genuine remaining blockers.

Never invent addresses, receipts, hashes, lifecycle state or a production URL.
