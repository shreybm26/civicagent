import { useEffect, useRef, useState } from "react";

function prefersReducedMotion(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function tokenize(text: string): string[] {
  return text.split(/(\s+)/).filter((part) => part.length > 0);
}

export function StreamingAgentText({
  text,
  messageKey,
  onComplete,
}: {
  text: string;
  messageKey: string;
  onComplete?: () => void;
}) {
  const [visible, setVisible] = useState("");
  const [streaming, setStreaming] = useState(true);
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  useEffect(() => {
    let cancelled = false;

    if (prefersReducedMotion() || !text) {
      setVisible(text);
      setStreaming(false);
      onCompleteRef.current?.();
      return;
    }

    const tokens = tokenize(text);
    let index = 0;
    setVisible("");
    setStreaming(true);

    const timer = window.setInterval(() => {
      if (cancelled) return;
      index += 1;
      setVisible(tokens.slice(0, index).join(""));
      if (index >= tokens.length) {
        window.clearInterval(timer);
        setStreaming(false);
        onCompleteRef.current?.();
      }
    }, 28);

    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [messageKey, text]);

  return (
    <span className={streaming ? "streaming-text" : undefined}>
      {visible}
      {streaming && <span className="stream-caret" aria-hidden="true" />}
    </span>
  );
}
