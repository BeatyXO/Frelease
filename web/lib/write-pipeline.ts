"use client";
import {signer,reader} from "./genlayer";
import {transactionsStatusNumberToName} from "genlayer-js/types";

export type TxPhase="AWAITING_SIGNATURE"|"SUBMITTED"|"CONSENSUS_RUNNING"|"PROVISIONAL"|"UNDETERMINED"|"READY_TO_FINALIZE"|"FINALIZED"|"FAILED";
export type TxState={phase:TxPhase;txId?:string;statusName?:string;message:string;receipt?:any};
export type CandidateLifecycle={assessmentSubmitted:boolean;consensusRunning:boolean;provisional:boolean;appealable:boolean;readyToFinalize:boolean;finalized:boolean;registryFinalized:boolean;activated:boolean;blocked:boolean};
export function candidateLifecycle(candidate:any,assessmentTx:TxState|undefined,checkpoint:any,head:any,appealable=false):CandidateLifecycle{
 const phase=assessmentTx?.phase;
 const checkpointMatchesCandidate=!!checkpoint?.checkpoint_key&&checkpoint?.candidate_key===candidate?.candidate_key&&checkpoint?.assessment_digest===candidate?.assessment_digest&&checkpoint?.policy_key===candidate?.policy_key&&checkpoint?.commit_sha===candidate?.commit_sha&&checkpoint?.artifact_sha256===candidate?.artifact_sha256;
 const assessmentFinalized=phase==="FINALIZED"||(!phase&&checkpointMatchesCandidate&&(checkpoint?.state==="ACTIVATED"||checkpoint?.state==="BLOCKED"));
 const registryFinalized=!!checkpoint?.checkpoint_key&&!!checkpoint?.assessment_digest;
 const checkpointConfirmsActivation=checkpointMatchesCandidate&&checkpoint?.state==="ACTIVATED";
 const headConfirms=!!head&&String(head.candidate_key||"")===String(candidate?.candidate_key||"")&&Number(head.sequence)===Number(candidate?.sequence)&&head?.policy_key===candidate?.policy_key&&head?.assessment_digest===candidate?.assessment_digest&&head?.commit_sha===candidate?.commit_sha&&head?.artifact_sha256===candidate?.artifact_sha256;
 const activated=assessmentFinalized&&registryFinalized&&checkpointConfirmsActivation&&headConfirms;
 return {assessmentSubmitted:!!assessmentTx?.txId||candidate?.state==="ASSESSED",consensusRunning:phase==="CONSENSUS_RUNNING"||phase==="SUBMITTED",provisional:phase==="PROVISIONAL"||phase==="UNDETERMINED",appealable,readyToFinalize:phase==="READY_TO_FINALIZE",finalized:assessmentFinalized,registryFinalized,activated,blocked:checkpoint?.state==="BLOCKED"};
}
function statusNameOf(...values:any[]){for(const value of values){if(value===undefined||value===null||value==="")continue;const raw=String(value);const mapped=(transactionsStatusNumberToName as Record<string,string>)[raw];return String(mapped||raw).toUpperCase()}return ""}
function feeArgs(e:any){return e?.distribution&&e?.feeValue!==undefined?{distribution:e.distribution,feeValue:e.feeValue}:undefined}
export async function writeFreleaseTx(opts:{account:string,address:string,functionName:string,args:any[],onState?:(s:TxState)=>void}){
 const {account,address,functionName,args,onState}=opts;if(!/^0x[a-fA-F0-9]{40}$/.test(address))throw new Error("Canonical Studionet contract address is not configured.");
 const client:any=signer(account);onState?.({phase:"AWAITING_SIGNATURE",message:"Review the transaction in your wallet."});
 const draft={address:address as `0x${string}`,functionName,args,value:0n};let estimate:any;try{estimate=await client.estimateTransactionFeesForWrite({...draft,account:account as `0x${string}`})}catch{}
 const fees=feeArgs(estimate);const txId=await client.writeContract({...draft,...(fees?{fees}:{})});onState?.({phase:"SUBMITTED",txId,message:"Submitted to GenLayer."});onState?.({phase:"CONSENSUS_RUNNING",txId,message:"Validators are processing this transaction."});
 const decided=await client.waitForTransactionReceipt({hash:txId,waitUntil:"decided",retries:180,interval:4000,fullTransaction:true});const tx=await client.getTransaction({hash:txId});const name=statusNameOf(tx?.statusName,tx?.status_name,tx?.status,decided?.statusName,decided?.status_name,decided?.status);
 if(name.includes("FINALIZED")){const s={phase:"FINALIZED" as const,txId,statusName:name,message:"Finalized. Canonical consequences may now be relied on.",receipt:decided};onState?.(s);return s}
 if(name.includes("READY_TO_FINALIZE")){const s={phase:"READY_TO_FINALIZE" as const,txId,statusName:name,message:"Appeal window closed; transaction is ready to finalize.",receipt:decided};onState?.(s);return s}
 if(name.includes("UNDETERMINED")){const s={phase:"UNDETERMINED" as const,txId,statusName:name,message:"Consensus is undetermined. No release activation may be inferred.",receipt:decided};onState?.(s);return s}
 if(name.includes("FAIL")||name.includes("REVERT")||name.includes("CANCEL")||name.includes("TIMEOUT")){const s={phase:"FAILED" as const,txId,statusName:name,message:"Transaction failed or reverted.",receipt:decided};onState?.(s);return s}
 const s={phase:"PROVISIONAL" as const,txId,statusName:name,message:"A provisional result exists. It is not an activated release.",receipt:decided};onState?.(s);return s;
}
export async function inspectTx(account:string|undefined,txId:string):Promise<TxState>{const c:any=account?signer(account):reader();const tx:any=await c.getTransaction({hash:txId as `0x${string}`});const name=statusNameOf(tx?.statusName,tx?.status_name,tx?.status);if(name.includes("FINALIZED"))return{phase:"FINALIZED",txId,statusName:name,message:"Finalized.",receipt:tx};if(name.includes("READY_TO_FINALIZE"))return{phase:"READY_TO_FINALIZE",txId,statusName:name,message:"Ready to finalize.",receipt:tx};if(name.includes("UNDETERMINED"))return{phase:"UNDETERMINED",txId,statusName:name,message:"Consensus is undetermined.",receipt:tx};if(name.includes("ACCEPTED")||name.includes("PROVISIONAL"))return{phase:"PROVISIONAL",txId,statusName:name,message:"Accepted provisionally; not final.",receipt:tx};if(name.includes("FAIL")||name.includes("REVERT")||name.includes("CANCEL")||name.includes("TIMEOUT"))return{phase:"FAILED",txId,statusName:name,message:"Transaction failed or reverted.",receipt:tx};return{phase:"CONSENSUS_RUNNING",txId,statusName:name,message:"Transaction lifecycle is still running.",receipt:tx}}
export async function finalizeTx(account:string,txId:string){return (signer(account) as any).finalizeTransaction({account:account as `0x${string}`,txId:txId as `0x${string}`})}
export async function canAppealTx(account:string,txId:string){return (signer(account) as any).canAppeal({txId:txId as `0x${string}`})}
export async function appealTx(account:string,txId:string){const c:any=signer(account);const can=await c.canAppeal({txId:txId as `0x${string}`});if(!can)throw new Error("This transaction is not currently appealable.");const bond=await c.getMinAppealBond({txId:txId as `0x${string}`});return c.appealTransaction({account:account as `0x${string}`,txId:txId as `0x${string}`,value:bond})}
