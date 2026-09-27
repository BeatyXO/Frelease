# Frelease validation and deployment report

## Submission status

Frelease's core deployment and positive lifecycle are complete on **GenLayer Studionet (chain 61999)**. The remaining unexecuted items are additional live negative-path demonstrations and an interactive injected-wallet smoke test; they are not required to establish that the deployed positive Frelease lifecycle works.

## Repository and CI

The most recent full GitHub Actions run is [36342835472](https://github.com/BeatyXO/Frelease/actions/runs/36342835472), successful for commit `5bd9f996a20bfd446fe8c150ebb490cff237e415` on 2026-09-27.

Verified CI coverage includes:

- Python compilation: **PASS** for both contracts.
- Deterministic/source-invariant suite: **16 passed**.
- GenVM lint + validation: **PASS** for both contracts.
  - `FreleaseRegistry`: 11 methods (7 view, 4 write).
  - `FreleaseEvaluator`: 7 methods (5 view, 2 write).
- Direct Mode: **10 passed**.
- `scripts/release_check.py`: **RELEASE CHECK OK**.
- Frontend dependency installation: **PASS**.
- Frontend TypeScript typecheck: **PASS**.
- Frontend production build: **PASS**.

The built frontend was also smoke-checked locally against Studionet on `/`, `/releases`, `/policy/new`, the live policy detail, `/candidate/new`, the activated candidate detail and `/history/frelease-main-compat-2026`. At a 394 px viewport, the checked routes rendered without horizontal overflow.

## Live Studionet deployment

`deployments/studionet.json` records the canonical deployment.

- **FreleaseRegistry:** `0x9658E192cdA77De11b7Fa173e7cd998791DB8578`
- **FreleaseEvaluator:** `0x8DA441a76AdEAE929C9DD9feBb77f0467da7e704`

Registry and Evaluator deployment transactions reached `FINALIZED`. The one-time Registry → Evaluator configuration transaction also reached `FINALIZED`, and `get_config()` returned the expected evaluator and owner addresses.

Both deployed contract source bodies were fetched and matched the local contract sources after line-ending normalization. The exposed method counts match the CI-validated APIs. No on-chain schema hash is claimed because none was captured from the available tooling.

## Positive live lifecycle

The positive candidate `frelease-docs-52fd697` binds:

- source commit: `52fd697e0528fee1545d2cd07c67967a40234a7d`
- artifact SHA-256: `21220bd0db846f64832d8934ab6d183a81605558ecb2a3f42ca9a24ae1deba33`

The assessment parent transaction reached `FINALIZED`. Its finalized-only Registry child also reached `FINALIZED`.

Canonical readback:

- verdict: `COMPATIBLE`
- checkpoint: `ACTIVATED`
- checkpoint reason: `FROZEN_POLICY_ACCEPTED_FINALIZED_VERDICT`
- policy head sequence: `1`
- policy head candidate: `frelease-docs-52fd697`

Evidence-window receipts, the aggregate evidence snapshot digest and assessment digest are recorded in `deployments/studionet.json`.

This demonstrates the intended Frelease boundary: a semantic finding does not become a release head until the evaluator transaction finalizes and the Registry's deterministic child transaction also finalizes.

## Negative-path evidence

The repository contains **green Direct Mode coverage** for the important deterministic negative paths, including:

- stale/out-of-order sequence blocking;
- artifact replay blocking;
- policy-retirement blocking;
- unauthorized evaluator configuration/calls;
- duplicate evidence URL rejection;
- private/link-local evidence host rejection.

One live duplicate-artifact attempt was also executed on Studionet. It finalized as `INCONCLUSIVE`, so the Registry correctly stored a `BLOCKED` checkpoint with reason `VERDICT_NOT_ACTIVATABLE_BY_FROZEN_POLICY`. Because the semantic verdict was not activatable, that transaction does **not** count as live proof of `ARTIFACT_ALREADY_ACTIVATED`.

A live `STALE_OR_NON_MONOTONIC_SEQUENCE` transaction has not been executed. These two additional live negative demonstrations are optional reviewer-strengthening evidence; they are not represented as completed.

## Frontend / Vercel

The frontend uses the yellow/green release-rail design and implements the policy → candidate → assessment → finalized checkpoint/history flow.

Wallet behavior in source:

- injected wallet only;
- reload restoration through `eth_accounts`;
- no cached address used as wallet truth;
- `accountsChanged` and `chainChanged` listeners;
- connected-wallet popover with full address;
- **Copy wallet address**;
- network switch;
- **Disconnect**;
- manual-disconnect opt-out for wallets that do not support permission revocation.

GitHub reports the latest **Vercel check as successful** for commit `d4b65927f0ecc8a289e4dd63023b5920bdb3b229` after the root TypeScript dependency and `web/.next` output-directory fixes.

The repository does not contain a verified public production URL, so no public `*.vercel.app` address is invented here. Interactive wallet reload/copy/disconnect/wrong-network behavior also remains unclaimed because the smoke-test browser did not expose an injected `window.ethereum` provider.

## Remaining non-blocking evidence

The only items not claimed as complete are:

1. a live compatible duplicate-artifact transaction that reaches the specific `ARTIFACT_ALREADY_ACTIVATED` Registry reason;
2. a live out-of-order candidate transaction that reaches `STALE_OR_NON_MONOTONIC_SEQUENCE`;
3. an interactive production smoke test with a real injected wallet;
4. recording a public production frontend URL if/when it is surfaced by the Vercel project;
5. an on-chain schema hash, if future tooling exposes one.

No address, receipt, status, hash or frontend URL is invented.
