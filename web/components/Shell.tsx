"use client";
import Link from "next/link";
import type React from "react";
import {WalletButton} from "./Wallet";
export function Shell({children}:{children:React.ReactNode}){return <><header className="topbar"><Link className="brand" href="/"><span className="brandMark">FL</span><span>Frelease</span></Link><nav><Link href="/releases">Release lanes</Link><Link href="/policy/new">New policy</Link><Link href="/candidate/new">New candidate</Link><a href="https://explorer-studio.genlayer.com" target="_blank" rel="noreferrer">Explorer</a></nav><WalletButton/></header><main>{children}</main><footer><span>Frelease · GenLayer Studionet</span><span>Freeze the rule. Evaluate the evidence. Finalize the release.</span></footer></>}
export function Pill({children,tone="neutral"}:{children:React.ReactNode;tone?:"good"|"warn"|"bad"|"neutral"}){return <span className={`pill ${tone}`}>{children}</span>}
export function TxBanner({state}:{state:any}){if(!state)return null;return <div className={`txBanner ${String(state.phase||"").toLowerCase()}`}><strong>{state.phase}</strong><span>{state.message}</span>{state.txId&&<a target="_blank" rel="noreferrer" href={`https://explorer-studio.genlayer.com/tx/${state.txId}`}>Explorer ↗</a>}</div>}
