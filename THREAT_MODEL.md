# Frelease threat model

## Threats covered

**Mutable or conflicting public evidence.** Validators bind exact bounded evidence-window hashes. Material evidence changes between nodes should produce disagreement rather than a silently durable result.

**Prompt injection inside release notes or docs.** Evidence is explicitly treated as hostile data. Instructions found in fetched pages are evidence content, not evaluator instructions.

**SSRF-style URLs.** Evidence validation requires HTTPS, standard port 443, no URL credentials, no local/single-label hosts, no literal IPv6 and rejects common private, link-local, documentation and non-routable IPv4 ranges.

**Model overreach.** The model returns only a bounded compatibility finding. It cannot choose activation policy, alter release sequence, rewrite policy terms or transfer value.

**Late stale finalization.** A lower/equal sequence is recorded `BLOCKED` even if semantically compatible.

**Artifact replay.** A previously activated artifact digest cannot activate again under the same policy with a new candidate key or sequence.

**Policy retirement race.** Retirement does not mutate frozen terms, but an in-flight candidate finalizing afterward is blocked from activation.

**Unauthorized activation.** Only the configured evaluator contract can register finalized assessments.

**Duplicate candidate sequence.** The evaluator prevents registering the same sequence twice under one policy.

## Explicit non-goals

Frelease does not prove source-to-binary reproducibility by itself; it binds the submitter-provided artifact digest and can evaluate build-manifest evidence. It does not replace formal verification, CI, package signatures or deployment authorization. It is a consensus-backed compatibility/activation primitive.
