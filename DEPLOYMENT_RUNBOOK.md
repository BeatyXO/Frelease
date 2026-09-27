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

## Canonical deployment

The current deployment is recorded in `deployments/studionet.json`.

- Registry, Evaluator and evaluator-binding transactions all reached `FINALIZED`.
- `registry.get_config()` matched the evaluator and owner addresses.
- Both deployed contract source bodies matched local source after line-ending normalization.
- Schema method counts are recorded; no schema hash is claimed.

The original deployment order was:

1. deploy `contracts/frelease_registry.py`;
2. deploy `contracts/frelease_evaluator.py` with the Registry address;
3. call `FreleaseRegistry.set_evaluator_once(evaluator)`;
4. finalize configuration;
5. verify Registry configuration and source parity.

`deploy/deployScript.ts` remains the reproducible deployment script for a future redeployment.

## Frontend environment

The repository-root Vercel configuration builds the Next.js app from `web/` and uses `web/.next` as its output directory.

```text
NEXT_PUBLIC_FRELEASE_REGISTRY_ADDRESS=0x9658E192cdA77De11b7Fa173e7cd998791DB8578
NEXT_PUBLIC_FRELEASE_EVALUATOR_ADDRESS=0x8DA441a76AdEAE929C9DD9feBb77f0467da7e704
NEXT_PUBLIC_GENLAYER_RPC_URL=https://studio.genlayer.com/api
NEXT_PUBLIC_GENLAYER_EXPLORER=https://explorer-studio.genlayer.com
```

GitHub reports the latest Vercel check as successful for commit `d4b65927f0ecc8a289e4dd63023b5920bdb3b229`. A public production URL is not recorded in this repository and is therefore not asserted here.

## Live lifecycle

The positive lifecycle is complete and recorded in `deployments/studionet.json`:

- parent assessment: `FINALIZED`;
- finalized-only Registry child: `FINALIZED`;
- verdict: `COMPATIBLE`;
- checkpoint: `ACTIVATED`;
- policy head: sequence `1`.

## Optional additional evidence

If an unlocked Studionet signer is available later, useful extra demonstrations are:

- a compatible duplicate artifact that reaches `ARTIFACT_ALREADY_ACTIVATED`;
- an out-of-order compatible candidate that reaches `STALE_OR_NON_MONOTONIC_SEQUENCE`;
- a retirement-race proof.

These protections already have green Direct Mode coverage and are not represented as missing core functionality.
