# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import hashlib
import json
import re
from urllib.parse import urlsplit
from genlayer import *


class FreleaseRegistry(gl.Contract):
    """Immutable release policies plus deterministic finalized activation state.

    Policy authors freeze compatibility rules before candidate assessment. The
    configured FreleaseEvaluator may later register only finalized semantic
    assessments. This contract then deterministically decides whether that
    finalized verdict may advance the policy head.
    """

    owner_address: str
    evaluator_address: str
    policies: TreeMap[str, str]
    policy_keys_json: str
    policy_heads: TreeMap[str, str]
    checkpoints_json: str
    checkpoint_keys_json: str
    activated_artifacts: TreeMap[str, str]
    policy_count: u256
    checkpoint_count: u256

    ALLOWED_EVIDENCE_KINDS = [
        "CHANGELOG",
        "API_SURFACE",
        "TEST_REPORT",
        "MIGRATION_GUIDE",
        "SECURITY_NOTE",
        "BUILD_MANIFEST",
    ]
    ACTIVATABLE_VERDICTS = ["COMPATIBLE", "COMPATIBLE_WITH_MIGRATION"]

    def __init__(self):
        self.owner_address = gl.message.sender_address.as_hex.lower()
        self.evaluator_address = ""
        self.policies = TreeMap()
        self.policy_keys_json = "[]"
        self.policy_heads = TreeMap()
        self.checkpoints_json = "{}"
        self.checkpoint_keys_json = "[]"
        self.activated_artifacts = TreeMap()
        self.policy_count = u256(0)
        self.checkpoint_count = u256(0)

    def _sender(self) -> str:
        return gl.message.sender_address.as_hex.lower()

    def _now(self) -> str:
        return str(gl.message_raw["datetime"])

    def _digest(self, payload: str) -> str:
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _key_ok(self, value: str) -> bool:
        return re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{2,71}", value or "") is not None

    def _canonical_origin(self, value: str) -> str:
        text = (value or "").strip()
        try:
            parsed = urlsplit(text)
        except Exception:
            raise gl.vm.UserError("invalid evidence origin")
        if parsed.scheme.lower() != "https":
            raise gl.vm.UserError("evidence origins must use https")
        if parsed.username or parsed.password:
            raise gl.vm.UserError("credentials in evidence origin are forbidden")
        host = (parsed.hostname or "").lower().rstrip(".")
        if not host or "." not in host or len(host) > 253 or ":" in host:
            raise gl.vm.UserError("invalid evidence origin host")
        try:
            port = parsed.port
        except Exception:
            raise gl.vm.UserError("invalid evidence origin port")
        if port not in [None, 443]:
            raise gl.vm.UserError("evidence origins may only use port 443")
        if parsed.path not in ["", "/"] or parsed.query or parsed.fragment:
            raise gl.vm.UserError("evidence origin must not include path, query, or fragment")
        for label in host.split("."):
            if (
                not label
                or len(label) > 63
                or re.fullmatch(r"[a-z0-9-]+", label) is None
                or label.startswith("-")
                or label.endswith("-")
            ):
                raise gl.vm.UserError("invalid evidence origin host")
        return "https://" + host

    def _parse_evidence_policy(self, raw: str) -> dict:
        if len(raw) > 12000:
            raise gl.vm.UserError("evidence policy too large")
        try:
            value = json.loads(raw)
        except Exception:
            raise gl.vm.UserError("evidence policy must be valid JSON")
        if not isinstance(value, dict):
            raise gl.vm.UserError("evidence policy must be a JSON object")

        required = value.get("required_kinds", [])
        if not isinstance(required, list) or len(required) < 2 or len(required) > 6:
            raise gl.vm.UserError("required_kinds must contain 2 to 6 items")
        normalized_required = []
        for item in required:
            kind = str(item).strip().upper()
            if kind not in self.ALLOWED_EVIDENCE_KINDS:
                raise gl.vm.UserError("unsupported required evidence kind")
            if kind in normalized_required:
                raise gl.vm.UserError("duplicate required evidence kind")
            normalized_required.append(kind)

        try:
            min_origins = int(value.get("min_distinct_origins", 1))
        except Exception:
            raise gl.vm.UserError("min_distinct_origins must be an integer")
        if min_origins < 1 or min_origins > 5:
            raise gl.vm.UserError("min_distinct_origins must be between 1 and 5")

        allowed_raw = value.get("allowed_origins", [])
        required_origins_raw = value.get("required_origins", [])
        if not isinstance(allowed_raw, list) or not isinstance(required_origins_raw, list):
            raise gl.vm.UserError("origin rules must be arrays")
        if len(allowed_raw) > 12 or len(required_origins_raw) > 6:
            raise gl.vm.UserError("too many evidence origins")

        allowed = []
        for item in allowed_raw:
            origin = self._canonical_origin(str(item))
            if origin not in allowed:
                allowed.append(origin)
        required_origins = []
        for item in required_origins_raw:
            origin = self._canonical_origin(str(item))
            if origin not in required_origins:
                required_origins.append(origin)
        if allowed and any(origin not in allowed for origin in required_origins):
            raise gl.vm.UserError("required origin must also be allowed")
        if len(required_origins) > min_origins:
            raise gl.vm.UserError("min_distinct_origins cannot be lower than required origins")

        return {
            "required_kinds": normalized_required,
            "min_distinct_origins": min_origins,
            "allowed_origins": allowed,
            "required_origins": required_origins,
        }

    def _parse_activatable_verdicts(self, raw: str) -> list:
        if len(raw) > 500:
            raise gl.vm.UserError("activatable verdict list too large")
        try:
            values = json.loads(raw)
        except Exception:
            raise gl.vm.UserError("activatable verdicts must be valid JSON")
        if not isinstance(values, list) or len(values) < 1 or len(values) > 2:
            raise gl.vm.UserError("activatable verdicts must contain 1 or 2 items")
        normalized = []
        for item in values:
            verdict = str(item).strip().upper()
            if verdict not in self.ACTIVATABLE_VERDICTS:
                raise gl.vm.UserError("unsupported activatable verdict")
            if verdict in normalized:
                raise gl.vm.UserError("duplicate activatable verdict")
            normalized.append(verdict)
        return normalized

    @gl.public.write
    def set_evaluator_once(self, evaluator_address: Address) -> None:
        if self._sender() != self.owner_address:
            raise gl.vm.UserError("only owner may set evaluator")
        if self.evaluator_address:
            raise gl.vm.UserError("evaluator already configured")
        text = evaluator_address.as_hex if hasattr(evaluator_address, "as_hex") else str(evaluator_address)
        if not text.startswith("0x") or len(text) != 42:
            raise gl.vm.UserError("invalid evaluator address")
        self.evaluator_address = text.lower()

    @gl.public.write
    def register_policy(
        self,
        policy_key: str,
        project_name: str,
        protected_surface: str,
        compatibility_rule: str,
        evidence_policy_json: str,
        activatable_verdicts_json: str,
    ) -> str:
        if not self._key_ok(policy_key):
            raise gl.vm.UserError("invalid policy_key")
        if policy_key in self.policies:
            raise gl.vm.UserError("policy_key already exists")
        name = project_name.strip()
        surface = protected_surface.strip()
        rule = compatibility_rule.strip()
        if len(name) < 2 or len(name) > 120:
            raise gl.vm.UserError("project_name length out of range")
        if len(surface) < 20 or len(surface) > 7000:
            raise gl.vm.UserError("protected_surface length out of range")
        if len(rule) < 20 or len(rule) > 5000:
            raise gl.vm.UserError("compatibility_rule length out of range")

        evidence_policy = self._parse_evidence_policy(evidence_policy_json)
        activatable = self._parse_activatable_verdicts(activatable_verdicts_json)
        immutable_terms = {
            "policy_key": policy_key,
            "project_name": name,
            "maintainer": self._sender(),
            "protected_surface": surface,
            "compatibility_rule": rule,
            "evidence_policy": evidence_policy,
            "activatable_verdicts": activatable,
        }
        policy_digest = self._digest(json.dumps(immutable_terms, sort_keys=True, separators=(",", ":")))
        snapshot = dict(immutable_terms)
        snapshot.update({
            "policy_digest": policy_digest,
            "status": "ACTIVE",
            "created_at": self._now(),
            "retired_at": "",
        })
        self.policies[policy_key] = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
        keys = json.loads(self.policy_keys_json)
        keys.append(policy_key)
        self.policy_keys_json = json.dumps(keys, separators=(",", ":"))
        self.policy_count = u256(int(self.policy_count) + 1)
        return policy_key

    @gl.public.write
    def retire_policy(self, policy_key: str) -> None:
        raw = self.policies.get(policy_key)
        if not raw:
            raise gl.vm.UserError("policy not found")
        policy = json.loads(raw)
        if policy["maintainer"] != self._sender():
            raise gl.vm.UserError("only maintainer may retire policy")
        if policy["status"] != "ACTIVE":
            raise gl.vm.UserError("policy already retired")
        policy["status"] = "RETIRED"
        policy["retired_at"] = self._now()
        self.policies[policy_key] = json.dumps(policy, sort_keys=True, separators=(",", ":"))

    @gl.public.write
    def register_finalized_assessment(
        self,
        policy_key: str,
        candidate_key: str,
        submitter: str,
        sequence: int,
        version: str,
        commit_sha: str,
        artifact_sha256: str,
        verdict: str,
        assessment_digest: str,
        policy_digest: str,
    ) -> str:
        if not self.evaluator_address or self._sender() != self.evaluator_address:
            raise gl.vm.UserError("only configured evaluator may register assessments")
        if not self._key_ok(candidate_key):
            raise gl.vm.UserError("invalid candidate_key")
        checkpoint_key = policy_key + ":" + candidate_key
        records = json.loads(self.checkpoints_json)
        if checkpoint_key in records:
            raise gl.vm.UserError("checkpoint already exists")

        raw = self.policies.get(policy_key)
        if not raw:
            raise gl.vm.UserError("policy not found")
        policy = json.loads(raw)
        if policy.get("policy_digest") != str(policy_digest).lower():
            raise gl.vm.UserError("policy digest mismatch")
        verdict_text = str(verdict).upper()
        if verdict_text not in ["COMPATIBLE", "COMPATIBLE_WITH_MIGRATION", "BREAKING", "INCONCLUSIVE"]:
            raise gl.vm.UserError("unsupported verdict")
        if sequence < 1 or sequence > 1000000000:
            raise gl.vm.UserError("sequence out of range")
        artifact_text = str(artifact_sha256).lower()
        assessment_text = str(assessment_digest).lower()
        if re.fullmatch(r"[a-f0-9]{64}", artifact_text) is None:
            raise gl.vm.UserError("invalid artifact_sha256")
        if re.fullmatch(r"[a-f0-9]{64}", assessment_text) is None:
            raise gl.vm.UserError("invalid assessment_digest")

        head_raw = self.policy_heads.get(policy_key)
        head = json.loads(head_raw) if head_raw else {"sequence": 0}
        accepted = [str(x).upper() for x in policy.get("activatable_verdicts", [])]
        semantic_allowed = verdict_text in accepted
        active_policy = policy.get("status") == "ACTIVE"
        monotonic = int(sequence) > int(head.get("sequence", 0))
        artifact_key = policy_key + ":" + artifact_text
        replay = bool(self.activated_artifacts.get(artifact_key))
        activated = active_policy and semantic_allowed and monotonic and not replay

        if not active_policy:
            reason = "POLICY_RETIRED_BEFORE_FINAL_ACTIVATION"
        elif not semantic_allowed:
            reason = "VERDICT_NOT_ACTIVATABLE_BY_FROZEN_POLICY"
        elif not monotonic:
            reason = "STALE_OR_NON_MONOTONIC_SEQUENCE"
        elif replay:
            reason = "ARTIFACT_ALREADY_ACTIVATED"
        else:
            reason = "FROZEN_POLICY_ACCEPTED_FINALIZED_VERDICT"

        record = {
            "checkpoint_key": checkpoint_key,
            "policy_key": policy_key,
            "candidate_key": candidate_key,
            "submitter": str(submitter).lower(),
            "sequence": int(sequence),
            "version": str(version),
            "commit_sha": str(commit_sha).lower(),
            "artifact_sha256": artifact_text,
            "verdict": verdict_text,
            "assessment_digest": assessment_text,
            "policy_digest": str(policy_digest).lower(),
            "state": "ACTIVATED" if activated else "BLOCKED",
            "reason": reason,
            "recorded_at": self._now(),
        }
        records[checkpoint_key] = record
        self.checkpoints_json = json.dumps(records, sort_keys=True, separators=(",", ":"))
        keys = json.loads(self.checkpoint_keys_json)
        keys.append(checkpoint_key)
        self.checkpoint_keys_json = json.dumps(keys, separators=(",", ":"))
        self.checkpoint_count = u256(int(self.checkpoint_count) + 1)

        if activated:
            head_record = {
                "policy_key": policy_key,
                "candidate_key": candidate_key,
                "sequence": int(sequence),
                "version": str(version),
                "commit_sha": str(commit_sha).lower(),
                "artifact_sha256": artifact_text,
                "assessment_digest": assessment_text,
                "policy_digest": str(policy_digest).lower(),
                "activated_at": self._now(),
            }
            self.policy_heads[policy_key] = json.dumps(head_record, sort_keys=True, separators=(",", ":"))
            self.activated_artifacts[artifact_key] = candidate_key
        return checkpoint_key

    @gl.public.view
    def get_policy(self, policy_key: str) -> dict:
        raw = self.policies.get(policy_key)
        return json.loads(raw) if raw else {}

    @gl.public.view
    def get_policy_head(self, policy_key: str) -> dict:
        raw = self.policy_heads.get(policy_key)
        return json.loads(raw) if raw else {}

    @gl.public.view
    def get_checkpoint(self, checkpoint_key: str) -> dict:
        return json.loads(self.checkpoints_json).get(checkpoint_key, {})

    @gl.public.view
    def list_policies(self, offset: int, limit: int) -> dict:
        if offset < 0:
            offset = 0
        if limit < 1:
            limit = 1
        if limit > 50:
            limit = 50
        keys = json.loads(self.policy_keys_json)
        selected = keys[offset : offset + limit]
        return {"items": [json.loads(self.policies[k]) for k in selected], "total": len(keys)}

    @gl.public.view
    def list_checkpoints(self, offset: int, limit: int) -> dict:
        if offset < 0:
            offset = 0
        if limit < 1:
            limit = 1
        if limit > 50:
            limit = 50
        keys = json.loads(self.checkpoint_keys_json)
        selected = keys[offset : offset + limit]
        records = json.loads(self.checkpoints_json)
        return {"items": [records[k] for k in selected], "total": len(keys)}

    @gl.public.view
    def validate_policy_inputs(self, evidence_policy_json: str, activatable_verdicts_json: str) -> dict:
        return {
            "evidence_policy": self._parse_evidence_policy(evidence_policy_json),
            "activatable_verdicts": self._parse_activatable_verdicts(activatable_verdicts_json),
        }

    @gl.public.view
    def get_config(self) -> dict:
        return {
            "owner_address": self.owner_address,
            "evaluator_address": self.evaluator_address,
            "policies": int(self.policy_count),
            "checkpoints": int(self.checkpoint_count),
        }
