import { describe, expect, it } from "vitest";
import { candidateLifecycle, type TxState } from "./lib/write-pipeline";

const finalized: TxState = { phase: "FINALIZED", txId: "0xabc", message: "Finalized" };
const checkpoint = { checkpoint_key: "policy:candidate-1", policy_key: "policy", candidate_key: "candidate-1", commit_sha: "commit-1", artifact_sha256: "artifact-1", assessment_digest: "digest-1", state: "ACTIVATED" };
const candidate = { candidate_key: "candidate-1", policy_key: "policy", sequence: 1, commit_sha: "commit-1", artifact_sha256: "artifact-1", assessment_digest: "digest-1" };
const head = { policy_key: "policy", candidate_key: "candidate-1", sequence: 1, commit_sha: "commit-1", artifact_sha256: "artifact-1", assessment_digest: "digest-1" };

describe("candidate activation lifecycle", () => {
  it("exposes finalize at READY_TO_FINALIZE", () => {
    expect(candidateLifecycle(candidate, { phase: "READY_TO_FINALIZE", txId: "0xabc", message: "ready" }, {}, {}).readyToFinalize).toBe(true);
  });
  it("exposes Appeal when the transaction is appealable", () => {
    expect(candidateLifecycle(candidate, { phase: "PROVISIONAL", txId: "0xabc", message: "appealable" }, {}, {}, true).appealable).toBe(true);
  });
  it("does not call a provisional accepted result activated", () => {
    expect(candidateLifecycle(candidate, { phase: "PROVISIONAL", message: "accepted" }, checkpoint, head).activated).toBe(false);
  });
  it("does not call finalized semantic result activated before the Registry consequence", () => {
    expect(candidateLifecycle(candidate, finalized, {}, {}).activated).toBe(false);
  });
  it("shows activation after finalized Registry checkpoint and matching policy head", () => {
    expect(candidateLifecycle(candidate, finalized, checkpoint, head).activated).toBe(true);
  });
  it("restores canonical activation from the finalized checkpoint after reload", () => {
    expect(candidateLifecycle(candidate, undefined, checkpoint, head).activated).toBe(true);
  });
  it("does not activate when the policy head points at another assessment", () => {
    expect(candidateLifecycle(candidate, finalized, checkpoint, { ...head, assessment_digest: "other-digest" }).activated).toBe(false);
  });
  it("does not call a blocked checkpoint activated", () => {
    expect(candidateLifecycle(candidate, finalized, { ...checkpoint, state: "BLOCKED" }, head).activated).toBe(false);
  });
});
