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
- Evidence URLs are HTTPS-only and reject credentials, private/non-routable IPv4 ranges, literal IPv6 and non-standard ports.
- Validators independently re-fetch evidence and compare material semantic fields.
- Each bounded evidence window is SHA-256 committed; validators compare the receipt set and aggregate snapshot digest.
- `COMPATIBLE` and `COMPATIBLE_WITH_MIGRATION` each have deterministic coherence laws.
- The model never decides which verdicts may activate; the policy author froze that list beforehand.
- Parent evaluator finality is required before a registry activation child transaction can exist.
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

The two contracts are deployed and configured on Studionet 61999. The Registry is `0x9658E192cdA77De11b7Fa173e7cd998791DB8578`; the Evaluator is `0x8DA441a76AdEAE929C9DD9feBb77f0467da7e704`. Both deployment transactions and the one-time evaluator configuration transaction reached `FINALIZED`. The positive candidate `frelease-docs-52fd697` also reached an `ACTIVATED` registry checkpoint after its finalized assessment parent and finalized registry child.

The machine-readable transaction and lifecycle record is [deployments/studionet.json](deployments/studionet.json). A second attempted assessment returned `INCONCLUSIVE`; it is not represented as proof of replay protection. The stale-sequence live path and production frontend deployment remain unverified. Use `DEPLOYMENT_RUNBOOK.md`, `REVIEW_TARGET.md` and `VALIDATION_REPORT.md` for the evidence and remaining checks.
