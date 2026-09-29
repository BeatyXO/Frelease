# Submission checklist

- [x] Two-contract architecture preserved.
- [x] Deterministic fetched provenance compares registered commit and artifact SHA-256.
- [x] Direct Mode behavioral tests cover match, each mismatch, both mismatch, missing and malformed provenance.
- [x] Unverified provenance forces `INCONCLUSIVE`.
- [x] Candidate page connects `inspectTx`, `finalizeTx` and `appealTx`; activation gate requires finalized assessment, matching Registry checkpoint and policy head.
- [x] Lifecycle decision tests cover Finalize, Appeal, provisional/semantic/finalized-without-checkpoint/blocked/activated states.
- [x] New corrected Registry/Evaluator pair deployed and configured on Studionet; source parity verified.
- [x] Fresh positive live lifecycle reached finalized `ACTIVATED` Registry checkpoint and policy head.
- [x] Live wrong-commit evidence rejected as `COMMIT_MISMATCH` / `INCONCLUSIVE`; Registry checkpoint `BLOCKED`; policy head unchanged.
- [x] 24 unit tests and 17 Direct Mode tests pass.
- [x] Frontend typecheck, production build and eight lifecycle tests pass.
- [ ] GenVM lint full SDK validation; static checks pass, SDK cache access fails with Windows `WinError 5`.
- [ ] Push corrected commit to `main` and record the resulting GitHub Actions run.
- [ ] Interactive wallet-based finalize/appeal screen smoke test; no injected wallet provider is available in the browser.
- [ ] Production frontend deployment and canonical address smoke test.
