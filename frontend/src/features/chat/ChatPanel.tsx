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
  /** Stable id for the current step so the widget stays mounted across busy/stream. */
  contextualKey?: string;
  composerEnabled?: boolean;
  mediaUrl: (mediaId: string) => string;
  pendingAction?: PendingAction;
  avatarState?: AvatarState;
};

function messageKey(message: Message, index: number): string {
  return `${message.role}-${message.timestamp}-${message.media_id ?? ""}-${index}`;
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
}: Props) {
  const [value, setValue] = useState("");
  const [awayFromLatest, setAwayFromLatest] = useState(false);
  const [pendingCitizen, setPendingCitizen] = useState<string | null>(null);
  const [, setStreamTick] = useState(0);
  const [stepReady, setStepReady] = useState(false);
  const endRef = useRef<HTMLDivElement | null>(null);
  const messagesRef = useRef<HTMLDivElement | null>(null);
  const nearBottomRef = useRef(true);
  const completedRef = useRef<Set<string>>(new Set());

  const displayMessages =
    pendingCitizen && !messages.some((message) => message.role === "citizen" && message.text === pendingCitizen)
      ? [
          ...messages,
          {
            role: "citizen" as const,
            text: pendingCitizen,
            timestamp: "pending-citizen",
            media_id: null,
          },
        ]
      : messages;

  useEffect(() => {
    if (busy || !pendingCitizen) return;
    setPendingCitizen(null);
  }, [busy, pendingCitizen, messages]);

  const latestIndex = displayMessages.length - 1;
  const latest = latestIndex >= 0 ? displayMessages[latestIndex] : null;
  const latestKey = latest ? messageKey(latest, latestIndex) : "";
  const needsStream = Boolean(
    !busy && !pendingCitizen && latest && latest.role === "agent" && !completedRef.current.has(latestKey),
  );

  // Never show location/photo/review widgets until the latest agent reply finishes streaming.
  useEffect(() => {
    setStepReady(false);
  }, [contextualKey]);

  useEffect(() => {
    if (!contextualStep || !contextualKey || busy || needsStream) return;
    setStepReady(true);
  }, [contextualStep, contextualKey, busy, needsStream]);

  const showContextual = Boolean(contextualStep) && Boolean(contextualKey) && stepReady;

  function stickMessagesToBottom() {
    const box = messagesRef.current;
    if (!box || !nearBottomRef.current) return;
    // Scroll only the chat transcript — never the whole page (scrollIntoView was yanking to the top).
    box.scrollTop = box.scrollHeight;
  }

  useEffect(() => {
    if (!nearBottomRef.current) {
      setAwayFromLatest(true);
      return;
    }
    stickMessagesToBottom();
    setAwayFromLatest(false);
  }, [displayMessages.length, busy, needsStream, showContextual, pendingAction, pendingCitizen]);

  // Keep the transcript pinned while the agent is typing characters.
  useEffect(() => {
    if (!needsStream || !nearBottomRef.current) return;
    const id = window.setInterval(() => stickMessagesToBottom(), 120);
    return () => window.clearInterval(id);
  }, [needsStream]);

  function onScroll() {
    const box = messagesRef.current;
    if (!box) return;
    const near = box.scrollHeight - box.scrollTop - box.clientHeight < 120;
    nearBottomRef.current = near;
    setAwayFromLatest(!near);
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!value.trim() || busy) return;
    const text = value.trim();
    nearBottomRef.current = true;
    setPendingCitizen(text);
    setValue("");
    onSend(text);
  }

  function jumpLatest() {
    nearBottomRef.current = true;
    stickMessagesToBottom();
    setAwayFromLatest(false);
  }

  function finishStream(key: string) {
    completedRef.current.add(key);
    setStreamTick((tick) => tick + 1);
    if (nearBottomRef.current) stickMessagesToBottom();
  }

  const activity = activityLabel(pendingAction, hindi);
  const latestAgent = [...displayMessages].reverse().find((message) => message.role === "agent");

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
        {displayMessages.map((message, index) => {
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

        {showContextual && (
          <div className="chat-inline-step" data-step={contextualKey}>
            {contextualStep}
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

      {showSuggestions && (
        <div className="chips" aria-label={hindi ? "सुझाए गए मुद्दे" : "Suggested issues"}>
          {SUGGESTIONS.map((item) => (
            <button
              key={item.label}
              type="button"
              disabled={busy}
              onClick={() => {
                nearBottomRef.current = true;
                setPendingCitizen(hindi ? item.textHi : item.text);
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
