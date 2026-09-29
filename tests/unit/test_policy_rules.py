import hashlib
import json
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def coherent(f):
    if f["verdict"] == "COMPATIBLE":
        return (
            f["surface_compatibility"] == "PRESERVED"
            and f["migration_requirement"] == "NONE"
            and f["regression_signal"] == "NONE"
            and f["evidence_sufficiency"] == "SUFFICIENT"
            and f["required_evidence_present"] == "YES"
        )
    if f["verdict"] == "COMPATIBLE_WITH_MIGRATION":
        return (
            f["surface_compatibility"] == "CHANGED"
            and f["migration_requirement"] == "REQUIRED"
            and f["regression_signal"] == "NONE"
            and f["evidence_sufficiency"] == "SUFFICIENT"
            and f["required_evidence_present"] == "YES"
        )
    if f["verdict"] == "BREAKING":
        return (
            f["evidence_sufficiency"] == "SUFFICIENT"
            and f["required_evidence_present"] == "YES"
            and (f["surface_compatibility"] == "CHANGED" or f["regression_signal"] == "MATERIAL")
        )
    return f["verdict"] == "INCONCLUSIVE"


def activate(policy_active, activatable, verdict, sequence, head_sequence, artifact_replay=False):
    if not policy_active:
        return "BLOCKED", "POLICY_RETIRED_BEFORE_FINAL_ACTIVATION"
    if verdict not in activatable:
        return "BLOCKED", "VERDICT_NOT_ACTIVATABLE_BY_FROZEN_POLICY"
    if sequence <= head_sequence:
        return "BLOCKED", "STALE_OR_NON_MONOTONIC_SEQUENCE"
    if artifact_replay:
        return "BLOCKED", "ARTIFACT_ALREADY_ACTIVATED"
    return "ACTIVATED", "FROZEN_POLICY_ACCEPTED_FINALIZED_VERDICT"


def test_compatible_requires_preserved_surface_and_no_migration():
    assert coherent({"verdict":"COMPATIBLE","surface_compatibility":"PRESERVED","migration_requirement":"NONE","regression_signal":"NONE","evidence_sufficiency":"SUFFICIENT","required_evidence_present":"YES"})


def test_compatible_rejects_material_regression():
    assert not coherent({"verdict":"COMPATIBLE","surface_compatibility":"PRESERVED","migration_requirement":"NONE","regression_signal":"MATERIAL","evidence_sufficiency":"SUFFICIENT","required_evidence_present":"YES"})


def test_migration_verdict_has_separate_law():
    assert coherent({"verdict":"COMPATIBLE_WITH_MIGRATION","surface_compatibility":"CHANGED","migration_requirement":"REQUIRED","regression_signal":"NONE","evidence_sufficiency":"SUFFICIENT","required_evidence_present":"YES"})


def test_breaking_requires_sufficient_evidence():
    assert not coherent({"verdict":"BREAKING","surface_compatibility":"CHANGED","migration_requirement":"REQUIRED","regression_signal":"UNKNOWN","evidence_sufficiency":"INSUFFICIENT","required_evidence_present":"YES"})


def test_frozen_policy_controls_activation_not_model_preference():
    assert activate(True,["COMPATIBLE"],"COMPATIBLE_WITH_MIGRATION",3,2)[0] == "BLOCKED"


def test_out_of_order_finalization_cannot_roll_back_head():
    assert activate(True,["COMPATIBLE"],"COMPATIBLE",4,5)[1] == "STALE_OR_NON_MONOTONIC_SEQUENCE"


def test_retired_policy_blocks_inflight_finalization():
    assert activate(False,["COMPATIBLE"],"COMPATIBLE",6,5)[1] == "POLICY_RETIRED_BEFORE_FINAL_ACTIVATION"


def test_replayed_artifact_cannot_activate_again():
    assert activate(True,["COMPATIBLE"],"COMPATIBLE",7,6,True)[1] == "ARTIFACT_ALREADY_ACTIVATED"


def test_policy_digest_is_stable_for_canonical_json():
    payload={"project":"demo","rule":"no removals","required":["API_SURFACE","TEST_REPORT"]}
    left=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    right=hashlib.sha256(json.dumps({"required":["API_SURFACE","TEST_REPORT"],"rule":"no removals","project":"demo"},sort_keys=True,separators=(",",":")).encode()).hexdigest()
    assert left == right


def provenance_matches(manifest_text, commit_sha, artifact_sha256):
    source = (ROOT / "contracts" / "frelease_evaluator.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    contract = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "FreleaseEvaluator")
    matcher = next(node for node in contract.body if isinstance(node, ast.FunctionDef) and node.name == "_provenance_observation")
    namespace = {"json": json, "re": __import__("re")}
    exec(compile(ast.Module(body=[matcher], type_ignores=[]), "frelease_evaluator.py", "exec"), namespace)
    return namespace["_provenance_observation"](None, manifest_text, commit_sha, artifact_sha256)


def test_candidate_provenance_accepts_exact_commit_and_artifact():
    commit, digest = "a" * 40, "b" * 64
    evidence = json.dumps({"provenance": {"commit_sha": commit, "artifact_sha256": digest}})
    assert provenance_matches(evidence, commit, digest)["verified"]


def test_candidate_provenance_rejects_mismatched_commit():
    evidence = json.dumps({"commit_sha": "c" * 40, "artifact_sha256": "b" * 64})
    assert provenance_matches(evidence, "a" * 40, "b" * 64)["status"] == "COMMIT_MISMATCH"


def test_candidate_provenance_rejects_mismatched_artifact():
    evidence = json.dumps({"commit_sha": "a" * 40, "artifact_sha256": "c" * 64})
    assert provenance_matches(evidence, "a" * 40, "b" * 64)["status"] == "ARTIFACT_MISMATCH"


def test_candidate_provenance_rejects_missing_or_invalid_manifest():
    assert provenance_matches('{"commit_sha":"' + "a" * 40 + '"}', "a" * 40, "b" * 64)["status"] == "MISSING_FIELDS"
    assert provenance_matches("not json", "a" * 40, "b" * 64)["status"] == "MALFORMED"


def test_contract_uses_same_provenance_matcher():
    evaluator = (ROOT / "contracts" / "frelease_evaluator.py").read_text(encoding="utf-8")
    assert "def _provenance_matches_candidate" in evaluator
    assert 'observed_commit_sha": observed_commit' in evaluator
    assert 'observed_artifact_sha256": observed_artifact' in evaluator


def immutable_provenance_url(url):
    source = (ROOT / "contracts" / "frelease_evaluator.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    contract = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "FreleaseEvaluator")
    matcher = next(node for node in contract.body if isinstance(node, ast.FunctionDef) and node.name == "_provenance_url_is_immutable")
    namespace = {"urlsplit": __import__("urllib.parse", fromlist=["urlsplit"]).urlsplit, "re": __import__("re")}
    exec(compile(ast.Module(body=[matcher], type_ignores=[]), "frelease_evaluator.py", "exec"), namespace)
    return namespace["_provenance_url_is_immutable"](None, url)


def test_provenance_manifest_must_use_commit_pinned_github_raw_url():
    commit = "c" * 40
    assert immutable_provenance_url(f"https://raw.githubusercontent.com/acme/project/{commit}/build.json")
    assert not immutable_provenance_url("https://raw.githubusercontent.com/acme/project/main/build.json")
    assert not immutable_provenance_url(f"https://example.org/acme/project/{commit}/build.json")
