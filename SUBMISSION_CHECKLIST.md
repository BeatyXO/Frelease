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
- [x] GenVM lint full SDK validation passed in the Linux GitHub Actions contracts job (local Windows SDK cache had a permission error).
- [x] Push corrected commit to `main` and record the successful GitHub Actions run `36608851753`.
- [ ] Interactive wallet-based finalize/appeal screen smoke test; no injected wallet provider is available in the browser.
- [ ] Production Vercel redeployment with canonical corrected Studionet Registry/Evaluator environment variables — owner-managed Vercel step.
