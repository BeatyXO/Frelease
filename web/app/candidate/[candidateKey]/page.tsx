"use client";
import { use, useCallback, useEffect, useRef, useState } from "react";
import { ADDRESSES, configured, reader, short } from "@/lib/genlayer";
import { Pill, TxBanner } from "@/components/Shell";
import { useWallet } from "@/components/Wallet";
import { appealTx, canAppealTx, candidateLifecycle, finalizeTx, inspectTx, writeFreleaseTx } from "@/lib/write-pipeline";

const demo = JSON.stringify([
  { kind: "CHANGELOG", url: "https://example.org/changelog", note: "Release notes" },
  { kind: "API_SURFACE", url: "https://example.org/api", note: "Published API surface" },
  { kind: "TEST_REPORT", url: "https://example.net/tests", note: "Compatibility suite" },
  { kind: "BUILD_MANIFEST", url: "https://raw.githubusercontent.com/OWNER/REPO/0000000000000000000000000000000000000000/build-manifest.json", note: "JSON with commit_sha and artifact_sha256" },
], null, 2);

export default function CandidatePage({ params }: { params: Promise<{ candidateKey: string }> }) {
  const { candidateKey } = use(params);
  const { address, chainOk, connect, switchNetwork } = useWallet();
  const [candidate, setCandidate] = useState<any>(null);
  const [checkpoint, setCheckpoint] = useState<any>({});
  const [head, setHead] = useState<any>({});
  const [manifest, setManifest] = useState(demo);
  const [tx, setTx] = useState<any>(null);
  const [error, setError] = useState("");
  const [canAppeal, setCanAppeal] = useState(false);
  const [lifecycleBusy, setLifecycleBusy] = useState(false);
  const loadedFinality = useRef("");

  const load = useCallback(async () => {
    if (!configured()) return;
    try {
      const client: any = reader();
      const current = await client.readContract({ address: ADDRESSES.evaluator as `0x${string}`, functionName: "get_candidate", args: [candidateKey] });
      setCandidate(current);
      if (current?.policy_key) {
        const key = `${current.policy_key}:${candidateKey}`;
        const [nextCheckpoint, nextHead] = await Promise.all([
          client.readContract({ address: ADDRESSES.registry as `0x${string}`, functionName: "get_checkpoint", args: [key] }),
          client.readContract({ address: ADDRESSES.registry as `0x${string}`, functionName: "get_policy_head", args: [current.policy_key] }),
        ]);
        setCheckpoint(nextCheckpoint);
        setHead(nextHead);
      }
    } catch { /* Keep the page readable while the RPC retries. */ }
  }, [candidateKey]);

  useEffect(() => { void load(); }, [load]);
  useEffect(() => {
    let active = true;
    const refresh = async () => {
      if (!tx?.txId) return;
      try {
        const state = await inspectTx(address || undefined, tx.txId);
        if (!active) return;
        setTx(state);
        if (state.phase === "FINALIZED" && loadedFinality.current !== tx.txId) {
          loadedFinality.current = tx.txId;
          await load();
        }
        if (address && (state.phase === "PROVISIONAL" || state.phase === "READY_TO_FINALIZE")) {
          setCanAppeal(await canAppealTx(address, tx.txId));
        } else setCanAppeal(false);
      } catch { /* Retain last lifecycle state and retry on the next poll. */ }
    };
    void refresh();
    const timer = setInterval(refresh, 5000);
    return () => { active = false; clearInterval(timer); };
  }, [tx?.txId, address, load]);

  const lifecycle = async (action: "finalize" | "appeal") => {
    setError("");
    setLifecycleBusy(true);
    try {
      if (!address) { await connect(); return; }
      if (!chainOk) { await switchNetwork(); return; }
      if (!tx?.txId) throw new Error("Assessment transaction hash is unavailable.");
      if (action === "finalize") await finalizeTx(address, tx.txId);
      else await appealTx(address, tx.txId);
      // The helper submits only. Re-read the lifecycle and canonical records afterward.
      const next = await inspectTx(address, tx.txId);
      setTx(next);
      await load();
      setCanAppeal((next.phase === "PROVISIONAL" || next.phase === "READY_TO_FINALIZE") && await canAppealTx(address, tx.txId));
    } catch (e: any) { setError(e?.message || `${action} failed`); }
    finally { setLifecycleBusy(false); }
  };

  const assess = async () => {
    setError("");
    try {
      if (!candidate) throw new Error("Candidate not loaded.");
      if (!address) { await connect(); return; }
      if (!chainOk) { await switchNetwork(); return; }
      if (address.toLowerCase() !== String(candidate.submitter || "").toLowerCase()) throw new Error("Only the candidate submitter may start its assessment.");
      const result = await writeFreleaseTx({ account: address, address: ADDRESSES.evaluator, functionName: "assess_candidate", args: [candidateKey, manifest], onState: setTx });
      if (result.phase === "FINALIZED") await load();
    } catch (e: any) { setError(e?.message || "Assessment failed"); }
  };

  if (!candidate) return <div className="page"><div className="empty"><h1>{candidateKey}</h1><p>{configured() ? "Reading candidate…" : "Canonical Frelease addresses are not configured yet."}</p></div></div>;

  const finding = candidate.finding || {};
  const state = candidateLifecycle(candidate, tx, checkpoint, head, canAppeal);
  const tone = finding.verdict === "COMPATIBLE" ? "good" : finding.verdict === "BREAKING" ? "bad" : finding.verdict === "INCONCLUSIVE" ? "warn" : "neutral";
  const activationLabel = state.activated ? "ACTIVATED" : state.blocked ? "BLOCKED" : state.registryFinalized ? "REGISTRY CONSEQUENCE FINALIZED" : state.finalized ? "ASSESSMENT FINALIZED" : state.readyToFinalize ? "READY TO FINALIZE" : state.appealable ? "APPEALABLE" : state.provisional ? "PROVISIONAL / ACCEPTED" : state.consensusRunning ? "CONSENSUS RUNNING" : state.assessmentSubmitted ? "ASSESSMENT SUBMITTED" : "NOT ASSESSED";

  return <div className="page">
    <div className="pageHead"><div><span className="kicker">CANDIDATE #{candidate.sequence}</span><h1>{candidate.version}</h1><p>{candidate.candidate_key} · commit {short(candidate.commit_sha)}</p></div><div className="headActions"><Pill tone={state.activated ? "good" : state.blocked ? "bad" : "warn"}>{activationLabel}</Pill><Pill tone={tone as any}>{finding.verdict || candidate.state}</Pill></div></div>
    <TxBanner state={tx} />
    {(tx?.phase === "READY_TO_FINALIZE" || tx?.phase === "PROVISIONAL") && <section className="panel"><span className="kicker">FINALITY REQUIRED</span><h2>{tx.phase === "READY_TO_FINALIZE" ? "Assessment is ready to finalize" : "Assessment is provisional / accepted"}</h2><p>A semantic finding is not activation. The evaluator transaction and Registry consequence must be finalized and confirmed by the canonical policy head.</p><div className="heroActions">{canAppeal && <button className="secondary" disabled={lifecycleBusy} onClick={() => lifecycle("appeal")}>{lifecycleBusy ? "Submitting…" : "Appeal assessment"}</button>}{tx.phase === "READY_TO_FINALIZE" && <button className="primary" disabled={lifecycleBusy} onClick={() => lifecycle("finalize")}>{lifecycleBusy ? "Submitting…" : "Finalize assessment"}</button>}{!address && <button className="secondary" disabled={lifecycleBusy} onClick={() => void connect()}>{lifecycleBusy ? "Connecting…" : "Connect wallet"}</button>}{address && !chainOk && <button className="secondary" disabled={lifecycleBusy} onClick={() => void switchNetwork()}>{lifecycleBusy ? "Switching…" : "Switch to Studionet"}</button>}</div>{!address && <small>Connect the submitting wallet to appeal or finalize.</small>}{address && !chainOk && <small>Switch to Studionet to continue.</small>}</section>}
    {error && <div className="notice bad">{error}</div>}
    <div className="metrics"><div><span>Surface</span><strong>{finding.surface_compatibility || "—"}</strong></div><div><span>Migration</span><strong>{finding.migration_requirement || "—"}</strong></div><div><span>Regression</span><strong>{finding.regression_signal || "—"}</strong></div><div><span>Evidence</span><strong>{finding.evidence_sufficiency || "—"}</strong></div></div>
    <section className="panel"><span className="kicker">Build identity</span><div className="hashLine"><span>Registered commit SHA</span><code>{candidate.commit_sha}</code></div><div className="hashLine"><span>Artifact SHA-256</span><code>{candidate.artifact_sha256}</code></div><div className="hashLine"><span>Frozen policy digest</span><code>{candidate.policy_digest}</code></div></section>
    <section className="panel"><span className="kicker">Release statement</span><p>{candidate.release_statement}</p></section>
    <section className="panel"><span className="kicker">Semantic assessment</span><p>{finding.summary || "This candidate has not been assessed yet."}</p>{finding.provenance && <div className="decisionBox"><strong>Provenance {finding.provenance.status}</strong><span>Commit {short(finding.provenance.observed_commit_sha)} / expected {short(finding.provenance.expected_commit_sha)} · artifact {short(finding.provenance.observed_artifact_sha256)} / expected {short(finding.provenance.expected_artifact_sha256)}</span></div>}{finding.evidence_snapshot_digest && <div className="hashLine"><span>Evidence snapshot</span><code>{finding.evidence_snapshot_digest}</code></div>}{candidate.assessment_digest && <div className="hashLine"><span>Assessment digest</span><code>{candidate.assessment_digest}</code></div>}{checkpoint?.reason && <div className="decisionBox"><strong>{checkpoint.state}</strong><span>{checkpoint.reason}</span></div>}{state.activated && <div className="decisionBox"><strong>Canonical activation confirmed</strong><span>Finalized Registry checkpoint and policy head both identify this candidate and assessment.</span></div>}</section>
    {candidate.state === "CANDIDATE" && <section className="panel assessPanel"><div><span className="kicker">RUN SEMANTIC ASSESSMENT</span><h2>Submit public engineering evidence</h2><p>Include a JSON BUILD_MANIFEST at a raw GitHub URL pinned to a full commit SHA. Its fetched commit_sha and artifact_sha256 must match the frozen identity.</p></div><textarea className="codeInput" rows={14} value={manifest} onChange={e => setManifest(e.target.value)} /><button className="primary actionButton" onClick={assess}>{!address ? "Connect wallet" : !chainOk ? "Switch network" : "Assess candidate"}</button></section>}
    <section className="panel"><span className="kicker">Evidence receipts</span><div className="receiptList">{(finding.evidence_receipts || []).map((receipt: any, index: number) => <div key={index}><div><strong>{receipt.kind}</strong><span>{receipt.fetch_status}</span></div><code>{short(receipt.content_window_sha256)}</code><small>{receipt.content_window_chars} chars {receipt.provenance ? `· provenance ${receipt.provenance.status}` : ""}</small></div>)}</div></section>
  </div>;
}
