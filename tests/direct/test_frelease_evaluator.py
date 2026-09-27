import json

def test_manifest_rejects_duplicate_urls(direct_deploy,direct_vm,direct_alice):
    direct_vm.sender=direct_alice;evaluator=direct_deploy("contracts/frelease_evaluator.py","0x"+"11"*20)
    manifest=json.dumps([{"kind":"CHANGELOG","url":"https://example.org/release","note":"changes"},{"kind":"API_SURFACE","url":"https://example.org/release","note":"surface"}])
    with direct_vm.expect_revert("duplicate evidence URL"): evaluator.validate_evidence_manifest(manifest)

def test_manifest_rejects_private_metadata_host(direct_deploy,direct_vm,direct_alice):
    direct_vm.sender=direct_alice;evaluator=direct_deploy("contracts/frelease_evaluator.py","0x"+"11"*20)
    manifest=json.dumps([{"kind":"CHANGELOG","url":"https://169.254.169.254/latest/meta-data","note":"bad"},{"kind":"API_SURFACE","url":"https://docs.example.org/api","note":"surface"}])
    with direct_vm.expect_revert("private or non-routable evidence hosts are forbidden"): evaluator.validate_evidence_manifest(manifest)

def test_manifest_reports_typed_origins(direct_deploy,direct_vm,direct_alice):
    direct_vm.sender=direct_alice;evaluator=direct_deploy("contracts/frelease_evaluator.py","0x"+"11"*20)
    manifest=json.dumps([{"kind":"CHANGELOG","url":"https://release.example.org/v1","note":"changes"},{"kind":"TEST_REPORT","url":"https://ci.example.net/run/7","note":"tests"}])
    result=evaluator.validate_evidence_manifest(manifest);assert result["items"]==2;assert len(result["distinct_origins"])==2
