import { FormEvent, ReactNode, useEffect, useRef, useState } from "react";
import type { Message } from "../../lib/types";
import { SUGGESTIONS } from "../../lib/conversation";
import { localizeAgentText } from "../../lib/i18n";
import { activityLabel, type AvatarState, type PendingAction } from "../../lib/activity";
import { CivicSevakAvatar } from "./CivicSevakAvatar";
import { StreamingAgentText } from "./StreamingAgentText";

type Props = {
  messages: Message[];
  onSend: (value: string) => void;
  busy: boolean;
  hindi: boolean;
  showSuggestions: boolean;
  contextualStep?: ReactNode;
  /** Stable id for the current step so the form stays mounted across busy/stream. */
  contextualKey?: string;
  composerEnabled?: boolean;
  mediaUrl: (mediaId: string) => string;
  pendingAction?: PendingAction;
  avatarState?: AvatarState;
  scrollToken?: number;
};

function messageKey(message: Message, index: number): string {
  return `${message.role}-${message.timestamp}-${message.media_id ?? ""}-${message.text.slice(0, 48)}-${index}`;
}

export function ChatPanel({
  messages,
  onSend,
  busy,
  hindi,
  showSuggestions,
  contextualStep,
  contextualKey = "",
  composerEnabled = true,
  mediaUrl,
  pendingAction = null,
  avatarState = "idle",
  scrollToken = 0,
}: Props) {
  const [value, setValue] = useState("");
  const [awayFromLatest, setAwayFromLatest] = useState(false);
  const [, setStreamTick] = useState(0);
  const [anchoredStep, setAnchoredStep] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement | null>(null);
  const messagesRef = useRef<HTMLDivElement | null>(null);
  const contextualRef = useRef<HTMLDivElement | null>(null);
  const nearBottomRef = useRef(true);
  const forceScrollRef = useRef(false);
  const completedRef = useRef<Set<string>>(new Set());

  const latestIndex = messages.length - 1;
  const latest = latestIndex >= 0 ? messages[latestIndex] : null;
  const latestKey = latest ? messageKey(latest, latestIndex) : "";
  const needsStream = Boolean(!busy && latest && latest.role === "agent" && !completedRef.current.has(latestKey));

  useEffect(() => {
    forceScrollRef.current = true;
  }, [scrollToken]);

  useEffect(() => {
    if (!contextualStep || !contextualKey) {
      setAnchoredStep(null);
      return;
    }
    // Anchor after the opening stream so the form does not vanish again while busy/saving.
    if (!needsStream) setAnchoredStep(contextualKey);
  }, [contextualStep, contextualKey, needsStream]);

  const showContextual = Boolean(contextualStep) && Boolean(contextualKey) && anchoredStep === contextualKey;

  useEffect(() => {
    const box = messagesRef.current;
    if (!box) return;
    if (forceScrollRef.current || nearBottomRef.current) {
      endRef.current?.scrollIntoView({ block: "end" });
      forceScrollRef.current = false;
      setAwayFromLatest(false);
      nearBottomRef.current = true;
    } else {
      setAwayFromLatest(true);
    }
  }, [messages, busy, needsStream, pendingAction, showContextual]);

  useEffect(() => {
    if (!showContextual) return;
    contextualRef.current?.scrollIntoView({ block: "nearest" });
  }, [showContextual, contextualKey]);

  function onScroll() {
    const box = messagesRef.current;
    if (!box) return;
    const near = box.scrollHeight - box.scrollTop - box.clientHeight < 80;
    nearBottomRef.current = near;
    setAwayFromLatest(!near);
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!value.trim() || busy) return;
    forceScrollRef.current = true;
    onSend(value.trim());
    setValue("");
  }

  function jumpLatest() {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    setAwayFromLatest(false);
    nearBottomRef.current = true;
  }

  function finishStream(key: string) {
    completedRef.current.add(key);
    setStreamTick((value) => value + 1);
    forceScrollRef.current = true;
  }

  const activity = activityLabel(pendingAction, hindi);
  const latestAgent = [...messages].reverse().find((message) => message.role === "agent");

  return (
    <section className="chat" aria-labelledby="assistant-title">
      <div className="chat-head">
        <CivicSevakAvatar size="header" state={avatarState} />
        <div>
          <span id="assistant-title">{hindi ? "सिविक सेवक से बातचीत" : "Civic Sevak conversation"}</span>
          <strong>{hindi ? "सिविक सेवक" : "Civic Sevak"}</strong>
        </div>
        <span className="chat-status">
          {busy ? (hindi ? "काम कर रहा है" : "Working") : hindi ? "तैयार" : "Ready"}
        </span>
      </div>

      <div className="messages" ref={messagesRef} onScroll={onScroll}>
        {messages.map((message, index) => {
          const key = messageKey(message, index);
          const localized = message.role === "citizen" ? message.text : localizeAgentText(message.text, hindi);
          const shouldStream = needsStream && key === latestKey;
          return (
            <div key={key} className={`bubble ${message.role}`}>
              {message.role === "agent" && <CivicSevakAvatar size="message" state="idle" />}
              <div className="bubble-body">
                <strong>
                  {message.role === "citizen"
                    ? hindi
                      ? "आप"
                      : "You"
                    : hindi
                      ? "सिविक सेवक"
                      : "Civic Sevak"}
                </strong>
                {message.media_id && (
                  <img
                    className="chat-image"
                    src={mediaUrl(message.media_id)}
                    alt={hindi ? "अपलोड की गई समस्या की तस्वीर" : "Uploaded civic issue"}
                  />
                )}
                {shouldStream ? (
                  <StreamingAgentText text={localized} messageKey={key} onComplete={() => finishStream(key)} />
                ) : (
                  <span>{localized}</span>
                )}
              </div>
            </div>
          );
        })}

        {busy && (
          <div className="bubble agent typing">
            <CivicSevakAvatar size="message" state="processing" />
            <div className="bubble-body">
              <strong>{hindi ? "सिविक सेवक" : "Civic Sevak"}</strong>
              <span className="typing-line" aria-hidden="true">
                <i />
                <i />
                <i />
                <em>{activity}</em>
              </span>
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>

      <div className="sr-live" aria-live="polite">
        {busy ? activity : latestAgent && !needsStream ? localizeAgentText(latestAgent.text, hindi) : ""}
      </div>

      {awayFromLatest && (
        <button type="button" className="jump-latest" onClick={jumpLatest}>
          {hindi ? "नवीनतम संदेश" : "Jump to latest"}
        </button>
      )}

      {showContextual && (
        <div className="chat-contextual" ref={contextualRef}>
          {contextualStep}
        </div>
      )}

      {showSuggestions && (
        <div className="chips" aria-label={hindi ? "सुझाए गए मुद्दे" : "Suggested issues"}>
          {SUGGESTIONS.map((item) => (
            <button
              key={item.label}
              type="button"
              disabled={busy}
              onClick={() => {
                forceScrollRef.current = true;
                onSend(hindi ? item.textHi : item.text);
              }}
            >
              {hindi ? item.hi : item.label}
            </button>
          ))}
        </div>
      )}

      {composerEnabled && (
        <form onSubmit={submit} className="composer">
          <label htmlFor="message">{hindi ? "शिकायत लिखें" : "Describe the issue"}</label>
          <div>
            <input
              id="message"
              value={value}
              onChange={(event) => setValue(event.target.value)}
              disabled={busy}
              maxLength={4000}
              placeholder={
                hindi ? "उदाहरण: सड़क पर गड्ढा है" : "Example: There is a pothole on my street"
              }
            />
            <button type="submit" className="primary" disabled={busy || !value.trim()}>
              {hindi ? "भेजें" : "Send"}
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
