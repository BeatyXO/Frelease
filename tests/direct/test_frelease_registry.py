import json

def _policy_args():
    evidence=json.dumps({"required_kinds":["API_SURFACE","TEST_REPORT"],"min_distinct_origins":1,"allowed_origins":[],"required_origins":[]})
    return ["demo-policy","Demo SDK","Public API symbols and wire response fields must remain compatible.","Existing documented calls must keep their meaning; migration-only changes require an explicit guide.",evidence,json.dumps(["COMPATIBLE","COMPATIBLE_WITH_MIGRATION"])]

def _hex_address(value):
    if isinstance(value,(bytes,bytearray)):
        return "0x"+bytes(value).hex()
    return value.as_hex if hasattr(value,"as_hex") else str(value)

def test_evaluator_can_only_be_configured_once(direct_deploy,direct_vm,direct_alice):
    direct_vm.sender=direct_alice;registry=direct_deploy("contracts/frelease_registry.py");registry.set_evaluator_once("0x"+"22"*20)
    with direct_vm.expect_revert("evaluator already configured"): registry.set_evaluator_once("0x"+"33"*20)

def test_non_owner_cannot_configure_evaluator(direct_deploy,direct_vm,direct_alice,direct_bob):
    direct_vm.sender=direct_alice;registry=direct_deploy("contracts/frelease_registry.py");direct_vm.sender=direct_bob
    with direct_vm.expect_revert("only owner may set evaluator"): registry.set_evaluator_once("0x"+"22"*20)

def test_policy_inputs_are_normalized(direct_deploy,direct_vm,direct_alice):
    direct_vm.sender=direct_alice;registry=direct_deploy("contracts/frelease_registry.py")
    evidence=json.dumps({"required_kinds":["api_surface","test_report"],"min_distinct_origins":1,"allowed_origins":[],"required_origins":[]})
    result=registry.validate_policy_inputs(evidence,json.dumps(["compatible"]))
    assert result["evidence_policy"]["required_kinds"]==["API_SURFACE","TEST_REPORT"];assert result["activatable_verdicts"]==["COMPATIBLE"]

def _setup_registry(direct_deploy,direct_vm,direct_alice,direct_bob):
    direct_vm.sender=direct_alice;registry=direct_deploy("contracts/frelease_registry.py");registry.set_evaluator_once(_hex_address(direct_bob));registry.register_policy(*_policy_args());return registry

def test_finalized_compatible_result_advances_head(direct_deploy,direct_vm,direct_alice,direct_bob):
    registry=_setup_registry(direct_deploy,direct_vm,direct_alice,direct_bob);policy=registry.get_policy("demo-policy");direct_vm.sender=direct_bob
    key=registry.register_finalized_assessment("demo-policy","cand-2",_hex_address(direct_alice),2,"2.0.0","deadbeef","11"*32,"COMPATIBLE","aa"*32,policy["policy_digest"])
    assert key=="demo-policy:cand-2";assert registry.get_checkpoint(key)["state"]=="ACTIVATED";assert registry.get_policy_head("demo-policy")["sequence"]==2

def test_stale_finalization_is_recorded_but_cannot_rollback(direct_deploy,direct_vm,direct_alice,direct_bob):
    registry=_setup_registry(direct_deploy,direct_vm,direct_alice,direct_bob);p=registry.get_policy("demo-policy");direct_vm.sender=direct_bob
    registry.register_finalized_assessment("demo-policy","cand-5",_hex_address(direct_alice),5,"5.0.0","deadbeef","22"*32,"COMPATIBLE","aa"*32,p["policy_digest"])
    key=registry.register_finalized_assessment("demo-policy","cand-4",_hex_address(direct_alice),4,"4.0.0","feedface","33"*32,"COMPATIBLE","bb"*32,p["policy_digest"])
    row=registry.get_checkpoint(key);assert row["state"]=="BLOCKED";assert row["reason"]=="STALE_OR_NON_MONOTONIC_SEQUENCE";assert registry.get_policy_head("demo-policy")["sequence"]==5

def test_replayed_artifact_is_blocked(direct_deploy,direct_vm,direct_alice,direct_bob):
    registry=_setup_registry(direct_deploy,direct_vm,direct_alice,direct_bob);p=registry.get_policy("demo-policy");direct_vm.sender=direct_bob;artifact="44"*32
    registry.register_finalized_assessment("demo-policy","cand-1",_hex_address(direct_alice),1,"1.0.0","deadbeef",artifact,"COMPATIBLE","aa"*32,p["policy_digest"])
    key=registry.register_finalized_assessment("demo-policy","cand-2",_hex_address(direct_alice),2,"2.0.0","feedface",artifact,"COMPATIBLE","bb"*32,p["policy_digest"])
    assert registry.get_checkpoint(key)["reason"]=="ARTIFACT_ALREADY_ACTIVATED"

def test_retired_policy_blocks_inflight_activation(direct_deploy,direct_vm,direct_alice,direct_bob):
    registry=_setup_registry(direct_deploy,direct_vm,direct_alice,direct_bob);p=registry.get_policy("demo-policy");direct_vm.sender=direct_alice;registry.retire_policy("demo-policy");direct_vm.sender=direct_bob
    key=registry.register_finalized_assessment("demo-policy","cand-1",_hex_address(direct_alice),1,"1.0.0","deadbeef","55"*32,"COMPATIBLE","aa"*32,p["policy_digest"])
    assert registry.get_checkpoint(key)["reason"]=="POLICY_RETIRED_BEFORE_FINAL_ACTIVATION"
