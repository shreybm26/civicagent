import { FormEvent, ReactNode, useEffect, useRef, useState } from "react";
import type { Message } from "../../lib/types";
import { SUGGESTIONS } from "../../lib/conversation";
import { localizeAgentText } from "../../lib/i18n";

export function ChatPanel({ messages, onSend, busy, hindi, showSuggestions, contextualStep, composerEnabled = true, mediaUrl }: { messages: Message[]; onSend: (value: string) => void; busy: boolean; hindi: boolean; showSuggestions: boolean; contextualStep?: ReactNode; composerEnabled?: boolean; mediaUrl: (mediaId: string) => string }) {
  const [value, setValue] = useState("");
  const endRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => { endRef.current?.scrollIntoView({ block: "end" }); }, [messages, busy, contextualStep]);
  function submit(event: FormEvent) { event.preventDefault(); if (!value.trim() || busy) return; onSend(value.trim()); setValue(""); }
  return <section className="chat" aria-labelledby="assistant-title">
    <div className="panel-head"><span id="assistant-title">{hindi ? "सहायता सहायक" : "Grievance assistant"}</span><strong>{hindi ? "नागरिक सेवक" : "Civic Sevak"}</strong></div>
    <div className="messages" aria-live="polite">
      {messages.map((message, index) => <div key={`${message.timestamp}-${index}`} className={`bubble ${message.role}`}>
        <strong>{message.role === "citizen" ? (hindi ? "आप" : "You") : hindi ? "सहायक" : "Assistant"}</strong>
        {message.media_id && <img className="chat-image" src={mediaUrl(message.media_id)} alt="Uploaded civic issue" />}
        <span>{message.role === "citizen" ? message.text : localizeAgentText(message.text, hindi)}</span>
      </div>)}
      {busy && <div className="bubble agent typing"><strong>{hindi ? "सहायक" : "Assistant"}</strong><span>{hindi ? "विवरण दर्ज किया जा रहा है…" : "Recording your details…"}</span></div>}
      <div ref={endRef} />
    </div>
    {contextualStep}
    {showSuggestions && <div className="chips" aria-label="Suggested issues">{SUGGESTIONS.map((item) => <button key={item.label} type="button" disabled={busy} onClick={() => onSend(hindi ? item.textHi : item.text)}>{hindi ? item.hi : item.label}</button>)}</div>}
    {composerEnabled && <form onSubmit={submit} className="composer"><label htmlFor="message">{hindi ? "शिकायत लिखें" : "Describe the issue"}</label><div><input id="message" value={value} onChange={(event) => setValue(event.target.value)} disabled={busy} maxLength={4000} placeholder={hindi ? "उदाहरण: सड़क पर गड्ढा है" : "Example: There is a pothole on my street"}/><button className="primary" disabled={busy || !value.trim()}>{hindi ? "भेजें" : "Send"}</button></div></form>}
  </section>;
}
