import json
import re


def test_fetched_provenance_accepts_exact_candidate_identity(direct_deploy, direct_vm, direct_alice):
    direct_vm.sender = direct_alice
    evaluator = direct_deploy("contracts/frelease_evaluator.py", "0x" + "11" * 20)
    commit, artifact = "a" * 40, "b" * 64
    record = json.dumps({"provenance": {"commit_sha": commit, "artifact_sha256": artifact}})
    observed = evaluator._provenance_observation(record, commit, artifact)
    assert observed == {
        "expected_commit_sha": commit,
        "observed_commit_sha": commit,
        "expected_artifact_sha256": artifact,
        "observed_artifact_sha256": artifact,
        "status": "VERIFIED",
        "verified": True,
    }


def test_fetched_immutable_markdown_manifest_parses_both_identity_fields(direct_deploy, direct_vm, direct_alice):
    direct_vm.sender = direct_alice
    evaluator = direct_deploy("contracts/frelease_evaluator.py", "0x" + "11" * 20)
    commit = "7c94b1e9a8f47f1aa173f53e2a78b877c93494b0"
    artifact = "4f2f7f1c870cc223e780f6ee5027fb3938f88678858436909471014c8e762f52"
    manifest = f"# Build manifest\n\nSource commit: {commit}\nArtifact SHA-256: {artifact}\n"
    result = evaluator._provenance_observation(manifest, commit, artifact)
    assert result["status"] == "VERIFIED" and result["verified"]


def test_fetched_provenance_rejects_wrong_commit(direct_deploy, direct_vm, direct_alice):
    direct_vm.sender = direct_alice
    evaluator = direct_deploy("contracts/frelease_evaluator.py", "0x" + "11" * 20)
    expected_commit, artifact = "a" * 40, "b" * 64
    record = json.dumps({"commit_sha": "c" * 40, "artifact_sha256": artifact})
    result = evaluator._provenance_observation(record, expected_commit, artifact)
    assert result["status"] == "COMMIT_MISMATCH" and not result["verified"]


def test_fetched_provenance_rejects_wrong_artifact(direct_deploy, direct_vm, direct_alice):
    direct_vm.sender = direct_alice
    evaluator = direct_deploy("contracts/frelease_evaluator.py", "0x" + "11" * 20)
    commit, expected_artifact = "a" * 40, "b" * 64
    record = json.dumps({"commit_sha": commit, "artifact_sha256": "c" * 64})
    result = evaluator._provenance_observation(record, commit, expected_artifact)
    assert result["status"] == "ARTIFACT_MISMATCH" and not result["verified"]


def test_fetched_provenance_rejects_both_mismatches(direct_deploy, direct_vm, direct_alice):
    direct_vm.sender = direct_alice
    evaluator = direct_deploy("contracts/frelease_evaluator.py", "0x" + "11" * 20)
    result = evaluator._provenance_observation(
        json.dumps({"commit_sha": "c" * 40, "artifact_sha256": "d" * 64}), "a" * 40, "b" * 64
    )
    assert result["status"] == "COMMIT_MISMATCH" and not result["verified"]


def test_fetched_provenance_rejects_missing_and_malformed_records(direct_deploy, direct_vm, direct_alice):
    direct_vm.sender = direct_alice
    evaluator = direct_deploy("contracts/frelease_evaluator.py", "0x" + "11" * 20)
    commit, artifact = "a" * 40, "b" * 64
    missing = evaluator._provenance_observation("{}", commit, artifact)
    malformed = evaluator._provenance_observation('{"provenance":', commit, artifact)
    assert missing["status"] == "MISSING_FIELDS" and not missing["verified"]
    assert malformed["status"] == "MALFORMED" and not malformed["verified"]


def test_mismatched_fetched_provenance_forces_nonactivatable_finding(direct_deploy, direct_vm, direct_alice):
    direct_vm.sender = direct_alice
    evaluator = direct_deploy("contracts/frelease_evaluator.py", "0x" + "11" * 20)
    candidate = {"commit_sha": "a" * 40, "artifact_sha256": "b" * 64}
    observed = evaluator._provenance_observation(
        json.dumps({"commit_sha": "c" * 40, "artifact_sha256": candidate["artifact_sha256"]}),
        candidate["commit_sha"], candidate["artifact_sha256"],
    )
    semantic_result = {
        "verdict": "COMPATIBLE", "surface_compatibility": "PRESERVED", "migration_requirement": "NONE",
        "regression_signal": "NONE", "evidence_sufficiency": "SUFFICIENT", "required_evidence_present": "YES",
    }
    gated = evaluator._enforce_provenance_gate(semantic_result, observed)
    assert gated["verdict"] == "INCONCLUSIVE"
    assert gated["verdict"] not in ("COMPATIBLE", "COMPATIBLE_WITH_MIGRATION")
    assert gated["provenance_failure"] == {
        "status": "COMMIT_MISMATCH",
        "reason": "FETCHED_COMMIT_DOES_NOT_MATCH_REGISTERED_CANDIDATE",
    }


def test_manifest_rejects_duplicate_urls(direct_deploy, direct_vm, direct_alice):
    direct_vm.sender = direct_alice
    evaluator = direct_deploy("contracts/frelease_evaluator.py", "0x" + "11" * 20)
    manifest = json.dumps([
        {"kind": "CHANGELOG", "url": "https://example.org/release", "note": "changes"},
        {"kind": "API_SURFACE", "url": "https://example.org/release", "note": "surface"},
    ])
    with direct_vm.expect_revert("duplicate evidence URL"):
        evaluator.validate_evidence_manifest(manifest)


def test_manifest_rejects_private_metadata_host(direct_deploy, direct_vm, direct_alice):
    direct_vm.sender = direct_alice
    evaluator = direct_deploy("contracts/frelease_evaluator.py", "0x" + "11" * 20)
    manifest = json.dumps([
        {"kind": "CHANGELOG", "url": "https://169.254.169.254/latest/meta-data", "note": "bad"},
        {"kind": "API_SURFACE", "url": "https://docs.example.org/api", "note": "surface"},
    ])
    with direct_vm.expect_revert("private or non-routable evidence hosts are forbidden"):
        evaluator.validate_evidence_manifest(manifest)


def test_manifest_reports_typed_origins(direct_deploy, direct_vm, direct_alice):
    direct_vm.sender = direct_alice
    evaluator = direct_deploy("contracts/frelease_evaluator.py", "0x" + "11" * 20)
    manifest = json.dumps([
        {"kind": "CHANGELOG", "url": "https://release.example.org/v1", "note": "changes"},
        {"kind": "TEST_REPORT", "url": "https://ci.example.net/run/7", "note": "tests"},
    ])
    result = evaluator.validate_evidence_manifest(manifest)
    assert result["items"] == 2
    assert len(result["distinct_origins"]) == 2
