# Frelease architecture

## Product thesis

Software releases create an adversarial semantic boundary: maintainers may believe a change is compatible, downstream integrators may disagree, and release notes can omit the exact behavior that matters. Frelease freezes the compatibility promise first, then asks GenLayer validators to independently inspect public engineering evidence for one exact candidate. Final activation is a separate deterministic consequence.

## FreleaseRegistry

The registry owns two kinds of state that belong together: **the frozen release rule** and **the canonical release head governed by that rule**.

A policy freezes project name, maintainer, protected surface, compatibility rule, evidence requirements/origins and which positive verdicts may activate. The immutable terms are canonical-JSON hashed into `policy_digest`. Policies can be retired but never edited.

The registry also owns finalized checkpoints. Only its configured evaluator can submit one. A checkpoint activates only when all conditions hold:

1. policy digest matches the frozen policy;
2. policy is still `ACTIVE` when the finalized child executes;
3. verdict was included in `activatable_verdicts` before assessment;
4. candidate sequence is strictly greater than the current policy head;
5. the exact artifact digest has not already activated under that policy.

Otherwise the checkpoint is stored as `BLOCKED` with an explicit deterministic reason.

## FreleaseEvaluator

The evaluator owns candidate identity and semantic assessment.

`begin_candidate` freezes policy digest, submitter, sequence, version, source commit, artifact SHA-256 and release statement. Sequence numbers are unique per policy inside the evaluator.

`assess_candidate` validates a typed HTTPS manifest and applies deterministic evidence-policy checks before entering nondeterministic consensus. Each validator independently renders the same public evidence, truncates to bounded windows, hashes those windows and asks the model for a bounded finding.

Material fields are:

- verdict
- protected-surface compatibility
- migration requirement
- material regression signal
- evidence sufficiency
- required evidence presence
- evidence snapshot digest
- full evidence receipt set

Validators do not accept schema-shape agreement alone. They re-run the assessment and compare those material fields and receipts.

## Decision law

`COMPATIBLE` requires preserved surface, no migration, no material regression, sufficient evidence and all required evidence.

`COMPATIBLE_WITH_MIGRATION` requires a changed surface, required/documented migration, no material regression, sufficient evidence and all required evidence.

`BREAKING` requires sufficient evidence, all required evidence and either a protected-surface change or material regression.

Missing/unavailable/conflicted evidence or an incoherent result becomes `INCONCLUSIVE`.

## Finality boundary

The evaluator stores the semantic finding after consensus, but it cannot move the release head. It calls:

`registry.emit(on="finalized").register_finalized_assessment(...)`

This means an `ACCEPTED`/provisional evaluator result cannot create the activation child transaction. The child still has its own GenLayer lifecycle and must itself be verified finalized before a production demo calls the candidate activated.

## Why two contracts, not three

A third activation-only contract would split deterministic policy and deterministic release-head state without introducing a new trust domain. Frelease keeps semantic consensus isolated in the evaluator while co-locating the frozen rule and its deterministic consequence in the registry. This yields a smaller attack surface and clearer reviewer story than a three-contract pipeline.
