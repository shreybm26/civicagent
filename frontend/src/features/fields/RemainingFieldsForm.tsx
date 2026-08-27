import { useEffect, useState } from "react";
import type { Field } from "../../lib/types";

const OPTIONS: Record<string, string[]> = {
  severity: ["low", "medium", "high"],
  leak_type: ["pipe", "tap", "supply", "unknown"],
  issue_type: ["sewage", "drain", "public_hygiene", "other"],
};

const OPTION_LABELS: Record<string, { en: string; hi: string }> = {
  low: { en: "low", hi: "कम" },
  medium: { en: "medium", hi: "मध्यम" },
  high: { en: "high", hi: "अधिक" },
  pipe: { en: "pipe", hi: "पाइप" },
  tap: { en: "tap", hi: "नल" },
  supply: { en: "supply", hi: "आपूर्ति" },
  unknown: { en: "unknown", hi: "अज्ञात" },
  sewage: { en: "sewage", hi: "सीवेज" },
  drain: { en: "drain", hi: "नाली" },
  public_hygiene: { en: "public hygiene", hi: "सार्वजनिक स्वच्छता" },
  other: { en: "other", hi: "अन्य" },
};

export function RemainingFieldsForm({
  fields,
  onSave,
  busy,
  hindi = false,
}: {
  fields: Field[];
  onSave: (id: string, value: string) => void;
  busy: boolean;
  hindi?: boolean;
}) {
  const missing = fields.filter((field) => field.required && (field.value == null || field.value === ""));
  const field = missing[0];
  const [value, setValue] = useState("");

  useEffect(() => {
    setValue("");
  }, [field?.id]);

  if (!field) return null;

  const options = OPTIONS[field.id];
  const inputId = `remaining-${field.id}`;

  return (
    <div className="chat-step remaining-fields">
      <h3>{hindi ? "एक विवरण और" : "One more detail"}</h3>
      <p>
        {hindi
          ? "कृपया यह आवश्यक विवरण दें। आप बाद में समीक्षा में बदल सकते हैं।"
          : "Please provide this required detail. You can change it later during review."}
      </p>
      <div className="remaining-field">
        {options ? (
          <span className="remaining-label" id={`${field.id}-label`}>
            {field.id.replaceAll("_", " ")}
          </span>
        ) : (
          <label htmlFor={inputId}>{field.id.replaceAll("_", " ")}</label>
        )}
        <div
          className={options ? "choice-bubbles" : "remaining-input"}
          role={options ? "group" : undefined}
          aria-labelledby={options ? `${field.id}-label` : undefined}
        >
          {options ? (
            options.map((option) => (
              <button
                type="button"
                className={value === option ? "choice-bubble selected" : "choice-bubble"}
                key={option}
                onClick={() => setValue(option)}
                disabled={busy}
              >
                {hindi ? OPTION_LABELS[option]?.hi || option : OPTION_LABELS[option]?.en || option}
              </button>
            ))
          ) : (
            <input
              id={inputId}
              value={value}
              onChange={(event) => setValue(event.target.value)}
              disabled={busy}
            />
          )}
          <button
            type="button"
            className="save-field"
            onClick={() => onSave(field.id, value)}
            disabled={busy || !value.trim()}
          >
            {hindi ? "सहेजें" : "Save"}
          </button>
        </div>
      </div>
    </div>
  );
}
