# Frelease

**Frelease** is a GenLayer-native compatibility and release-activation protocol for software, SDK and protocol upgrades on **GenLayer Studionet (chain ID 61999)**.

A maintainer freezes a compatibility policy before a release candidate is assessed. A candidate then binds an exact release sequence, version, source commit and artifact SHA-256. GenLayer validators independently retrieve typed public engineering evidence and determine one bounded semantic outcome:

- `COMPATIBLE`
- `COMPATIBLE_WITH_MIGRATION`
- `BREAKING`
- `INCONCLUSIVE`

The evaluator **does not activate releases**. Only after the evaluator transaction finalizes does it emit a finalized-only child call to `FreleaseRegistry`. The registry deterministically applies the already-frozen activation policy, policy status, monotonic sequence rule and artifact replay protection. A provisional compatibility verdict therefore never becomes a release head.

## Two-contract architecture

1. **`FreleaseRegistry`** — immutable policy terms, policy retirement, evaluator authorization, finalized activation checkpoints, current policy heads, monotonic sequence protection and artifact replay protection.
2. **`FreleaseEvaluator`** — candidate identity, typed evidence validation, independent evidence retrieval, semantic consensus, evidence-window receipts and finalized-only registry emission.

This split is deliberate: semantic judgment and activation authority are different responsibilities, but a third contract would add no independent domain responsibility.

## Reviewer-relevant invariants

- Policy terms are immutable and digest-bound before candidate evaluation.
- Candidate source commit and artifact digest are fixed before evidence assessment.
- Every assessment requires a fetched `BUILD_MANIFEST` at a raw GitHub URL pinned to a full immutable commit SHA. The deterministic parser extracts commit and artifact SHA-256 fields from JSON or the documented exact Markdown labels and compares both with the registered candidate; missing, malformed or mismatched provenance forces `INCONCLUSIVE` and cannot activate.
- Evidence URLs are HTTPS-only and reject credentials, private/non-routable IPv4 ranges, literal IPv6 and non-standard ports.
- Validators independently re-fetch evidence and compare material semantic fields.
- Each bounded evidence window is SHA-256 committed; validators compare the receipt set and aggregate snapshot digest.
- `COMPATIBLE` and `COMPATIBLE_WITH_MIGRATION` each have deterministic coherence laws.
- The model never decides which verdicts may activate; the policy author froze that list beforehand.
- Parent evaluator finality is required before a registry activation child transaction can exist.
- The candidate screen exposes finalize and appeal actions while an assessment is `READY_TO_FINALIZE`; activation is shown from registry state only after finality.
- A retired policy blocks an in-flight candidate from becoming a new head.
- A lower/equal sequence cannot replace a newer finalized head.
- An artifact already activated under a policy cannot activate again under another candidate identity.

## Frontend

Routes:

- `/` — product thesis and two-contract architecture
- `/releases` — canonical policy lanes
- `/policy/new` — freeze a compatibility policy
- `/policy/[policyKey]` — policy terms, current head and candidates
- `/candidate/new` — bind exact release identity
- `/candidate/[candidateKey]` — candidate evidence, semantic finding and finalized checkpoint
- `/history/[policyKey]` — finalized activation/block history

The UI uses injected wallets only. It restores connection state after reload by querying the provider with `eth_accounts`; it never stores an address as truth. Clicking the connected wallet opens a popover with the full address, **Copy wallet address**, network switch and **Disconnect**. Manual disconnect is stored only as an opt-out so unsupported permission-revocation wallets do not silently reconnect on reload.

### Reproduce the provenance and finality corrections

The exact reviewer steps, behavioral tests, expected observations and current deployment limitations are in [REVIEWER_REMEDIATION.md](REVIEWER_REMEDIATION.md). Run `pytest -q tests/direct/test_frelease_evaluator.py` to exercise the evaluator provenance parser on matching, mismatched, missing and malformed fetched documents. A fresh corrected pair and live positive/negative candidates are recorded in `deployments/studionet.json`; reproduction steps and transaction evidence are documented in `REVIEWER_REMEDIATION.md`.

## Local checks

```bash
python -m py_compile contracts/*.py
pytest -q tests/unit
python scripts/release_check.py
```

With GenLayer development dependencies installed:

```bash
pip install -r requirements.txt
genvm-lint check contracts/frelease_registry.py
genvm-lint check contracts/frelease_evaluator.py
pytest -q tests/direct
```

Frontend:

```bash
cd web
npm install
npm run typecheck
npm run build
npm run dev
```

## Verified Studionet deployment

The canonical corrected two-contract deployment on Studionet 61999 is recorded in [deployments/studionet.json](deployments/studionet.json). The fresh Registry and Evaluator are finalized, configured to each other, and their RPC-fetched source matches the local contract source. The earlier pair is retained only as historical data.

The positive candidate `papito-positive-v3-20260929` binds commit `7c94b1e9a8f47f1aa173f53e2a78b877c93494b0` and artifact SHA-256 `4f2f7f1c870cc223e780f6ee5027fb3938f88678858436909471014c8e762f52`. Its fetched manifest reported matching values with `VERIFIED`; its finalized assessment and Registry child resulted in an `ACTIVATED` checkpoint and sequence 1 policy head.

The live wrong-commit candidate `papito-wrong-commit-v3-20260929` used the same artifact but registered commit `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`. The fetched manifest reported the positive candidate commit, so the evaluator stored `COMMIT_MISMATCH` and `INCONCLUSIVE`; its Registry checkpoint is `BLOCKED` and the policy head remains on the positive candidate. Reproduction commands and validation limits are in [REVIEWER_REMEDIATION.md](REVIEWER_REMEDIATION.md).
