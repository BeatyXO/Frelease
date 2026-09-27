from pathlib import Path
root=Path(__file__).resolve().parents[1]
required=["contracts/frelease_registry.py","contracts/frelease_evaluator.py","ARCHITECTURE.md","DIFFERENTIATION.md","THREAT_MODEL.md","web/app/page.tsx","web/app/policy/new/page.tsx","web/app/candidate/new/page.tsx","web/components/Wallet.tsx"]
for rel in required:
    if not (root/rel).exists(): raise SystemExit(f"missing required file: {rel}")
evaluator=(root/"contracts/frelease_evaluator.py").read_text();registry=(root/"contracts/frelease_registry.py").read_text();wallet=(root/"web/components/Wallet.tsx").read_text()
checks={"finalized child":'emit(on="finalized").register_finalized_assessment' in evaluator,"independent validator":"def validate(leader_result)" in evaluator and "run_nondet_unsafe" in evaluator,"evidence receipts":"content_window_sha256" in evaluator and "evidence_snapshot_digest" in evaluator,"policy digest":"policy_digest" in registry and "policy digest mismatch" in evaluator,"monotonic activation":"STALE_OR_NON_MONOTONIC_SEQUENCE" in registry,"artifact replay":"ARTIFACT_ALREADY_ACTIVATED" in registry,"retirement safety":"POLICY_RETIRED_BEFORE_FINAL_ACTIVATION" in registry,"wallet provider refresh":'method:"eth_accounts"' in wallet and 'accountsChanged' in wallet,"wallet popover":"Copy wallet address" in wallet and "Disconnect" in wallet}
failed=[k for k,v in checks.items() if not v]
if failed: raise SystemExit("release check failed: "+", ".join(failed))
print("RELEASE CHECK OK")
