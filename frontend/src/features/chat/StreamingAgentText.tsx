import { useEffect, useRef, useState } from "react";

function prefersReducedMotion(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/** Prefer slow character reveal so replies feel spoken, not flashed. */
function tokenize(text: string): string[] {
  return Array.from(text);
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
    let timer = 0;
    setVisible("");
    setStreaming(true);

    const tick = () => {
      if (cancelled) return;
      index += 1;
      setVisible(tokens.slice(0, index).join(""));
      if (index >= tokens.length) {
        setStreaming(false);
        onCompleteRef.current?.();
        return;
      }
      const just = tokens[index - 1] ?? "";
      // Slightly paced character reveal with short punctuation breaths.
      let pause = 28;
      if (/[.!?…]/.test(just)) pause = 300;
      else if (/[,;:]/.test(just)) pause = 150;
      else if (just === " " && /[.!?…]/.test(tokens[index - 2] ?? "")) pause = 100;
      else if (just === " ") pause = 38;
      timer = window.setTimeout(tick, pause);
    };
    timer = window.setTimeout(tick, 36);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [messageKey, text]);

  return (
    <span className={streaming ? "streaming-text" : undefined}>
      {visible}
      {streaming && <span className="stream-caret" aria-hidden="true" />}
    </span>
  );
}
