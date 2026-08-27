import { FormEvent, useEffect, useRef, useState } from "react";
import type { Message } from "../../lib/types";
import { SUGGESTIONS } from "../../lib/conversation";
import { localizeAgentText } from "../../lib/i18n";

type ChatPanelProps = {
  messages: Message[];
  onSend: (value: string) => void;
  busy: boolean;
  hindi: boolean;
  showSuggestions: boolean;
};

export function ChatPanel({ messages, onSend, busy, hindi, showSuggestions }: ChatPanelProps) {
  const [value, setValue] = useState("");
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [messages, busy]);

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!value.trim() || busy) return;
    onSend(value.trim());
    setValue("");
  }

  return (
    <section className="chat" aria-labelledby="assistant-title">
      <div className="panel-head">
        <span id="assistant-title">{hindi ? "सहायता सहायक" : "Grievance assistant"}</span>
        <strong>{hindi ? "नागरिक सेवक" : "Civic Sevak"}</strong>
      </div>
      <div className="messages" aria-live="polite">
        {messages.map((message, index) => (
          <p key={`${message.timestamp}-${index}`} className={`bubble ${message.role}`}>
            <strong>{message.role === "citizen" ? (hindi ? "आप" : "You") : hindi ? "सहायक" : "Assistant"}</strong>
            {message.role === "citizen" ? message.text : localizeAgentText(message.text, hindi)}
          </p>
        ))}
        {busy && (
          <p className="bubble agent typing">
            <strong>{hindi ? "सहायक" : "Assistant"}</strong>
            {hindi ? "विवरण दर्ज किया जा रहा है…" : "Recording your details…"}
          </p>
        )}
        <div ref={endRef} />
      </div>
      {showSuggestions && (
        <div className="chips" aria-label={hindi ? "सुझाए गए विषय" : "Suggested issues"}>
          {SUGGESTIONS.map((item) => (
            <button key={item.label} type="button" disabled={busy} onClick={() => onSend(hindi ? item.textHi : item.text)}>
              {hindi ? item.hi : item.label}
            </button>
          ))}
        </div>
      )}
      <form onSubmit={submit} className="composer">
        <label htmlFor="message">{hindi ? "शिकायत लिखें" : "Describe the issue"}</label>
        <div>
          <input
            id="message"
            value={value}
            onChange={(event) => setValue(event.target.value)}
            disabled={busy}
            maxLength={4000}
            placeholder={hindi ? "उदाहरण: जेएनटीयू मेट्रो के पास गड्ढा है" : "Example: There is a pothole near JNTU Metro"}
          />
          <button className="primary" disabled={busy || !value.trim()}>
            {hindi ? "भेजें" : "Send"}
          </button>
        </div>
      </form>
    </section>
  );
}
