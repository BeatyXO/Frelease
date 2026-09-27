"use client";
import React,{createContext,useCallback,useContext,useEffect,useMemo,useRef,useState} from "react";
import {CHAIN_ID,RPC,EXPLORER,short} from "@/lib/genlayer";

type Provider={request:(x:{method:string;params?:any[]})=>Promise<any>;on?:(e:string,h:(...x:any[])=>void)=>void;removeListener?:(e:string,h:(...x:any[])=>void)=>void};
declare global{interface Window{ethereum?:Provider}}
type WalletCtx={address:string|null;chainOk:boolean;busy:boolean;error:string;connect:()=>Promise<void>;disconnect:()=>Promise<void>;switchNetwork:()=>Promise<void>;refresh:()=>Promise<void>};
const C=createContext<WalletCtx|null>(null);
const HEX=`0x${CHAIN_ID.toString(16)}`;
const OPT_OUT="frelease:manual-wallet-disconnect";

export function WalletProvider({children}:{children:React.ReactNode}){
  const [address,setAddress]=useState<string|null>(null);
  const [chainOk,setChainOk]=useState(false);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");

  const refresh=useCallback(async()=>{
    const p=window.ethereum;
    if(!p){setAddress(null);setChainOk(false);return}
    if(localStorage.getItem(OPT_OUT)==="1"){setAddress(null);const chain=await p.request({method:"eth_chainId"});setChainOk(parseInt(chain,16)===CHAIN_ID);return}
    try{
      const [accounts,chain]=await Promise.all([p.request({method:"eth_accounts"}),p.request({method:"eth_chainId"})]);
      setAddress(accounts?.[0]||null);
      setChainOk(parseInt(chain,16)===CHAIN_ID);
    }catch(e:any){setError(e?.message||"Unable to read injected wallet");setAddress(null);setChainOk(false)}
  },[]);

  useEffect(()=>{
    refresh();
    const p=window.ethereum;if(!p?.on)return;
    const accountsChanged=(accounts:any[])=>{if(accounts?.length){localStorage.removeItem(OPT_OUT);setAddress(accounts[0])}else setAddress(null)};
    const chainChanged=(chain:string)=>setChainOk(parseInt(chain,16)===CHAIN_ID);
    p.on("accountsChanged",accountsChanged);p.on("chainChanged",chainChanged);
    return()=>{p.removeListener?.("accountsChanged",accountsChanged);p.removeListener?.("chainChanged",chainChanged)};
  },[refresh]);

  const switchNetwork=async()=>{
    const p=window.ethereum;if(!p)throw new Error("No injected wallet found");
    setError("");
    try{await p.request({method:"wallet_switchEthereumChain",params:[{chainId:HEX}]})}
    catch(e:any){if(e?.code!==4902)throw e;await p.request({method:"wallet_addEthereumChain",params:[{chainId:HEX,chainName:"GenLayer Studionet",nativeCurrency:{name:"GEN",symbol:"GEN",decimals:18},rpcUrls:[RPC],blockExplorerUrls:[EXPLORER]}]})}
    await refresh();
  };

  const connect=async()=>{
    const p=window.ethereum;if(!p)throw new Error("Install an injected EIP-1193 wallet");
    setBusy(true);setError("");localStorage.removeItem(OPT_OUT);
    try{const accounts=await p.request({method:"eth_requestAccounts"});setAddress(accounts?.[0]||null);await switchNetwork()}
    catch(e:any){setError(e?.message||"Wallet connection failed");throw e}
    finally{setBusy(false)}
  };

  const disconnect=async()=>{
    const p=window.ethereum;setBusy(true);setError("");localStorage.setItem(OPT_OUT,"1");
    try{await p?.request({method:"wallet_revokePermissions",params:[{eth_accounts:{}}]})}catch{/* not all injected wallets implement revoke */}
    finally{setAddress(null);setBusy(false)}
  };

  const value=useMemo(()=>({address,chainOk,busy,error,connect,disconnect,switchNetwork,refresh}),[address,chainOk,busy,error,refresh]);
  return <C.Provider value={value}>{children}</C.Provider>;
}
export function useWallet(){const value=useContext(C);if(!value)throw new Error("WalletProvider missing");return value}

export function WalletButton(){
  const {address,chainOk,busy,error,connect,disconnect,switchNetwork}=useWallet();
  const [open,setOpen]=useState(false),[copied,setCopied]=useState(false);
  const ref=useRef<HTMLDivElement>(null);
  useEffect(()=>{const close=(e:MouseEvent)=>{if(ref.current&&!ref.current.contains(e.target as Node))setOpen(false)};document.addEventListener("mousedown",close);return()=>document.removeEventListener("mousedown",close)},[]);
  if(!address)return <div className="walletEntry"><button className="walletButton" disabled={busy} onClick={()=>connect().catch(()=>{})}>{busy?"Connecting…":"Connect wallet"}</button>{error&&<span className="walletError" title={error}>!</span>}</div>;
  return <div className="walletWrap" ref={ref}>
    <button className={`walletButton ${chainOk?"connected":"warn"}`} onClick={()=>setOpen(v=>!v)}><span className="walletDot"/>{short(address)}<span className="chev">⌄</span></button>
    {open&&<div className="walletMenu">
      <div className="walletMenuHead"><span>Injected wallet</span><strong>{chainOk?"Studionet":"Wrong network"}</strong></div>
      <div className="walletAddr">{address}</div>
      {!chainOk&&<button onClick={()=>switchNetwork().catch(()=>{})}>Switch to Studionet</button>}
      <button onClick={async()=>{await navigator.clipboard.writeText(address);setCopied(true);setTimeout(()=>setCopied(false),1300)}}>{copied?"Address copied ✓":"Copy wallet address"}</button>
      <button className="danger" onClick={()=>{disconnect();setOpen(false)}}>Disconnect</button>
    </div>}
  </div>;
}
