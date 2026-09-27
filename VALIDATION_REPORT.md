# Frelease validation report

## Completed in the initial build environment

- Python syntax compilation: **PASS** for both contracts.
- Deterministic/source-invariant suite: **16 passed**.
- `scripts/release_check.py`: **RELEASE CHECK OK**.
- Wallet implementation includes provider-truth `eth_accounts` refresh, `accountsChanged` / `chainChanged` listeners, copy-address popover and disconnect opt-out.

## Not yet claimed

Direct Mode was authored but this build environment did not expose the `direct_deploy`/`direct_vm` GenLayer pytest fixtures, so Direct Mode is **not claimed as passing here**. GenVM lint, frontend dependency installation/typecheck/build, Studionet deployment, deployed-source parity and live parent/child lifecycle proof must be completed by the handoff agent and recorded with real outputs.

No deployment address, transaction ID, schema hash or production URL is invented in this repository.
