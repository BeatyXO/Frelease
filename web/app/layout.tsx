import type {Metadata} from "next";
import type React from "react";
import "./globals.css";
import {WalletProvider} from "@/components/Wallet";
import {Shell} from "@/components/Shell";
export const metadata:Metadata={title:"Frelease",description:"Consensus-backed software release compatibility and activation on GenLayer."};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body><WalletProvider><Shell>{children}</Shell></WalletProvider></body></html>}
