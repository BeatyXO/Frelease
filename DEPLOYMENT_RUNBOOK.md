# Frelease Studionet deployment runbook

Target **GenLayer Studionet / chain 61999** only.

## Preflight

```bash
python -m py_compile contracts/*.py
pytest -q tests/unit
python scripts/release_check.py
pip install -r requirements.txt
genvm-lint check contracts/frelease_registry.py
genvm-lint check contracts/frelease_evaluator.py
pytest -q tests/direct
cd web && npm install && npm run typecheck && npm run build
```

## Deployment order

1. Deploy `contracts/frelease_registry.py` with no constructor arguments.
2. Deploy `contracts/frelease_evaluator.py` with the registry address.
3. Call `FreleaseRegistry.set_evaluator_once(evaluator)` from the registry deployer and finalize it.
4. Verify registry config reads the exact evaluator address.
5. Verify deployed source parity and record source/schema hashes.

`deploy/deployScript.ts` performs the deployment/configuration sequence and writes `deployments/studionet.json`.

Run it only from an authenticated GenLayer deployment environment after confirming the connected wallet, chain ID 61999, and sufficient Studionet funds. The script waits for each deployment/configuration transaction to become `FINALIZED`; preserve its output and verify the generated manifest against canonical explorer/state reads before treating deployment as complete. The checked-in `deployments/studionet.example.json` contains empty illustrative fields and is not a deployment receipt. Never copy those empty fields into a file presented as a completed deployment.

After deployment, independently verify `registry.get_config()` returns the evaluator address. Compare both deployed contract sources to the local source hashes recorded by the script (and verify schema parity when available). The script currently records source hashes, addresses and transaction IDs; add schema hashes/method counts only when the deployment tooling exposes verified values.

## Frontend environment

```text
NEXT_PUBLIC_FRELEASE_REGISTRY_ADDRESS=0x...
NEXT_PUBLIC_FRELEASE_EVALUATOR_ADDRESS=0x...
NEXT_PUBLIC_GENLAYER_RPC_URL=https://studio.genlayer.com/api
NEXT_PUBLIC_GENLAYER_EXPLORER=https://explorer-studio.genlayer.com
```

## Live lifecycle

Use at least two real public evidence origins. Record policy registration, candidate registration, assessment parent tx, finalized registry child tx, evidence snapshot digest, assessment digest, checkpoint readback and policy-head readback. Then exercise a stale sequence or artifact replay negative path.
