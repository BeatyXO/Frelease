# Frelease reviewer target

Frelease has a live Studionet deployment, finalized configuration and a completed positive activation lifecycle recorded in `deployments/studionet.json`.

## Already demonstrated

1. `FreleaseRegistry` and `FreleaseEvaluator` are deployed on Studionet 61999.
2. Registry → Evaluator configuration reached `FINALIZED`.
3. `get_config()` readback matched the expected evaluator and owner.
4. Both deployed contract source bodies match local source after line-ending normalization.
5. A real policy and candidate were registered.
6. The assessment parent reached `FINALIZED`.
7. The finalized-only Registry child reached `FINALIZED`.
8. Canonical readback returned:
   - verdict `COMPATIBLE`;
   - checkpoint `ACTIVATED`;
   - reason `FROZEN_POLICY_ACCEPTED_FINALIZED_VERDICT`;
   - policy head sequence `1`.
9. Evidence receipts, evidence snapshot digest and assessment digest were recorded.
10. CI is green for contract compilation, deterministic tests, GenVM lint/validation, Direct Mode, architecture guard, frontend typecheck and frontend production build.
11. The latest Vercel check is successful after the repository-root dependency/output-directory fixes.

## Optional strengthening evidence

These are useful but are **not required to establish the deployed positive lifecycle**:

- Run a compatible duplicate-artifact candidate that reaches `ARTIFACT_ALREADY_ACTIVATED`.
- Run an out-of-order compatible candidate that reaches `STALE_OR_NON_MONOTONIC_SEQUENCE`.
- Smoke-test the deployed frontend with a real injected wallet for reload restoration, copy address, disconnect and wrong-network switching.
- Record the public production frontend URL when it is available from the Vercel project.
- Record an on-chain schema hash if future tooling exposes one.

Direct Mode already covers stale-sequence, artifact-replay and retirement protections.

Do not describe `ACCEPTED`, `INCONCLUSIVE` or another provisional evaluator state as an activated release. Canonical activation comes from the Registry checkpoint/head after finalized child execution.
