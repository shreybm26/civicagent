import type { SessionView } from "./types";
export type CivicApi = { createSession():Promise<SessionView>; sendMessage(id:string,message:string):Promise<SessionView>; reset(id:string):Promise<SessionView> };
const base = "http://localhost:8000";
async function call(path:string, init?:RequestInit):Promise<SessionView>{const r=await fetch(base+path,init); if(!r.ok) throw new Error("Request failed"); return r.json();}
export const api:CivicApi={createSession:()=>call("/api/session",{method:"POST"}),sendMessage:(id,message)=>call(`/api/session/${id}/message`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message})}),reset:(id)=>call(`/api/session/${id}/reset`,{method:"POST"})};
