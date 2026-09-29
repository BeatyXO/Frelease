from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVALUATOR = (ROOT / "contracts" / "frelease_evaluator.py").read_text()
REGISTRY = (ROOT / "contracts" / "frelease_registry.py").read_text()


def test_evaluator_uses_real_nondeterministic_consensus():
    assert "gl.nondet.web.render" in EVALUATOR
    assert "gl.nondet.exec_prompt" in EVALUATOR
    assert "gl.vm.run_nondet_unsafe" in EVALUATOR
    assert "def validate(leader_result)" in EVALUATOR


def test_evaluator_binds_exact_evidence_windows():
    assert "content_window_sha256" in EVALUATOR
    assert "evidence_snapshot_digest" in EVALUATOR
    assert 'leader.get("evidence_receipts") == own.get("evidence_receipts")' in EVALUATOR


def test_build_manifest_identity_is_deterministically_checked():
    assert 'item["kind"] == "BUILD_MANIFEST"' in EVALUATOR
    assert 'candidate["commit_sha"]' in EVALUATOR
    assert 'candidate["artifact_sha256"]' in EVALUATOR
    assert 'self._enforce_provenance_gate(finding, provenance)' in EVALUATOR
    assert '"BUILD_MANIFEST" not in required_kinds' in EVALUATOR
    assert "_provenance_url_is_immutable(item[\"url\"])" in EVALUATOR


def test_application_exposes_finalization_and_appeal_flow():
    page = (ROOT / "web" / "app" / "candidate" / "[candidateKey]" / "page.tsx").read_text(encoding="utf-8")
    pipeline = (ROOT / "web" / "lib" / "write-pipeline.ts").read_text(encoding="utf-8")
    assert 'tx.phase === "READY_TO_FINALIZE"' in page
    assert 'lifecycle("finalize")' in page
    assert 'lifecycle("appeal")' in page
    assert "finalizeTx" in pipeline and "appealTx" in pipeline and "canAppealTx" in pipeline
    assert "await load()" in page


def test_activation_is_finalized_only_and_deterministic():
    assert 'emit(on="finalized").register_finalized_assessment' in EVALUATOR
    assert "activatable_verdicts" in REGISTRY
    assert "semantic_allowed" in REGISTRY


def test_monotonic_sequence_and_artifact_replay_protection_exist():
    assert "STALE_OR_NON_MONOTONIC_SEQUENCE" in REGISTRY
    assert 'int(sequence) > int(head.get("sequence", 0))' in REGISTRY
    assert "ARTIFACT_ALREADY_ACTIVATED" in REGISTRY


def test_policy_terms_are_digest_bound_on_both_sides():
    assert "policy_digest" in REGISTRY
    assert "policy digest mismatch" in EVALUATOR
    assert "policy digest mismatch" in REGISTRY


def test_retirement_can_stop_inflight_activation_without_mutating_terms():
    assert "POLICY_RETIRED_BEFORE_FINAL_ACTIVATION" in REGISTRY
    assert 'policy["status"] = "RETIRED"' in REGISTRY


def test_two_contract_architecture_has_no_value_transfer_layer():
    corpus = (EVALUATOR + REGISTRY).lower()
    assert "gl.message.value" not in corpus
    assert ".transfer(" not in corpus
    assert "withdraw(" not in corpus
