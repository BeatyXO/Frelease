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

The current deployment is recorded in `deployments/studionet.json`. Registry, Evaluator and evaluator-binding transactions all reached `FINALIZED`. The registry `get_config()` readback matched the evaluator and owner addresses. Both deployed source bodies match local source after normalizing line endings; schema hashes were not recorded. The example file remains illustrative only.

After deployment, independently verify `registry.get_config()` returns the evaluator address. Both deployed contract sources were fetched over RPC and matched the local source after line-ending normalization. Record schema hashes only when verified.

## Frontend environment

The repository-root Vercel configuration builds the Next.js app from `web/` and sets its output directory to `web/.next`.

```text
NEXT_PUBLIC_FRELEASE_REGISTRY_ADDRESS=0x...
NEXT_PUBLIC_FRELEASE_EVALUATOR_ADDRESS=0x...
NEXT_PUBLIC_GENLAYER_RPC_URL=https://studio.genlayer.com/api
NEXT_PUBLIC_GENLAYER_EXPLORER=https://explorer-studio.genlayer.com
```

## Live lifecycle

The positive lifecycle is recorded in `deployments/studionet.json`, with a `COMPATIBLE` verdict and `ACTIVATED` checkpoint following finalized parent and child transactions. A separate duplicate-artifact candidate was assessed as `INCONCLUSIVE`; because semantic assessment did not yield an activatable verdict, that attempt does not prove the Registry's `ARTIFACT_ALREADY_ACTIVATED` path. Run a compatible duplicate under the same policy and verify its checkpoint, then run a newer sequence followed by a compatible older sequence to verify stale blocking.
