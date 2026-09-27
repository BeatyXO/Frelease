# Frelease post-build status

The original Codex handoff is complete. Frelease is now deployed, configured, CI-green and has a finalized positive Studionet lifecycle.

## Completed

- Two-contract architecture preserved:
  - `FreleaseRegistry`
  - `FreleaseEvaluator`
- Python compilation: **PASS**.
- Deterministic/source-invariant tests: **16 passed**.
- GenVM lint + validation: **PASS** for both contracts.
- Direct Mode: **10 passed**.
- Release architecture guard: **PASS**.
- Frontend install/typecheck/production build: **PASS**.
- Canonical Studionet deployment: **complete**.
- Registry → Evaluator configuration: **FINALIZED**.
- Both deployed source bodies match local source after line-ending normalization.
- Positive lifecycle:
  - assessment parent: `FINALIZED`;
  - Registry child: `FINALIZED`;
  - verdict: `COMPATIBLE`;
  - checkpoint: `ACTIVATED`;
  - policy head sequence: `1`.
- Latest Vercel check: **success**.

Canonical addresses:

- Registry: `0x9658E192cdA77De11b7Fa173e7cd998791DB8578`
- Evaluator: `0x8DA441a76AdEAE929C9DD9feBb77f0467da7e704`

Full transaction and lifecycle evidence is in `deployments/studionet.json`.

## Preserve

Do not collapse the architecture or weaken these invariants:

- frozen policy digest;
- exact candidate source/artifact identity;
- typed public HTTPS evidence;
- independent validator evidence retrieval;
- evidence-window SHA-256 receipts;
- finalized-only evaluator → registry boundary;
- deterministic activatable-verdict rule;
- monotonic sequence protection;
- artifact replay protection;
- policy-retirement protection.

Wallet behavior to preserve:

- injected wallet only;
- restore authorized account on reload via `eth_accounts`;
- no cached address as source of truth;
- `accountsChanged` / `chainChanged`;
- wallet popover with full address, **Copy wallet address**, network switching and **Disconnect**;
- persisted manual-disconnect opt-out.

## Optional strengthening work only

No further work below should be described as a core blocker.

If an unlocked Studionet signer and interactive browser are available later:

1. produce a compatible duplicate-artifact transaction that reaches `ARTIFACT_ALREADY_ACTIVATED`;
2. produce an out-of-order compatible candidate that reaches `STALE_OR_NON_MONOTONIC_SEQUENCE`;
3. interactively smoke-test wallet reload/copy/disconnect/wrong-network behavior;
4. record a public production frontend URL when surfaced by the Vercel project;
5. record an on-chain schema hash if future tooling exposes one.

One live duplicate-artifact attempt already finalized as `INCONCLUSIVE` and was stored `BLOCKED`; it is deliberately **not** misrepresented as artifact-replay proof.

Never invent addresses, receipts, hashes, lifecycle state, schema hashes or a production URL.
