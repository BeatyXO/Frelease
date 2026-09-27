"use client";
import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

export const CHAIN_ID = 61999;
export const RPC = process.env.NEXT_PUBLIC_GENLAYER_RPC_URL || "https://studio.genlayer.com/api";
export const EXPLORER = process.env.NEXT_PUBLIC_GENLAYER_EXPLORER || "https://explorer-studio.genlayer.com";
export const ADDRESSES = {
  registry: process.env.NEXT_PUBLIC_FRELEASE_REGISTRY_ADDRESS || "",
  evaluator: process.env.NEXT_PUBLIC_FRELEASE_EVALUATOR_ADDRESS || "",
};
export const configured = () => Object.values(ADDRESSES).every(v => /^0x[a-fA-F0-9]{40}$/.test(v));
export const reader = () => createClient({ chain: studionet, endpoint: RPC } as any);
export const signer = (account:string) => createClient({ chain: studionet, endpoint: RPC, account:account as `0x${string}` } as any);
export const short = (value?:string|null) => value ? `${value.slice(0,6)}…${value.slice(-4)}` : "—";
export const explorerTx = (tx?:string) => tx ? `${EXPLORER}/tx/${tx}` : EXPLORER;
