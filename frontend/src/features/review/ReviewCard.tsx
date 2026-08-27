import { useEffect, useState } from "react";
import type { Field } from "../../lib/types";
import { fieldHint, fieldLabel } from "../../lib/fieldLabels";

const FIELD_OPTIONS: Record<string, string[]> = {
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

const text = (field: Field) => (field.value == null ? "" : String(field.value));

export function ReviewCard({
  fields,
  department,
  onEdit,
  onSubmit,
  busy,
  hindi,
  photoAdded,
}: {
  fields: Field[];
  department?: string;
  onEdit: (id: string, value: string) => Promise<void>;
  onSubmit: () => void;
  busy: boolean;
  hindi: boolean;
  photoAdded: boolean;
}) {
  const [drafts, setDrafts] = useState<Record<string, string>>(() =>
    Object.fromEntries(fields.map((field) => [field.id, text(field)])),
  );
  const [saving, setSaving] = useState<string | null>(null);

  useEffect(() => {
    setDrafts((current) => {
      const next = { ...current };
      for (const field of fields) if (saving !== field.id) next[field.id] = text(field);
      return next;
    });
  }, [fields, saving]);

  async function save(field: Field) {
    const value = drafts[field.id] ?? "";
    if (field.required && !value.trim()) return;
    setSaving(field.id);
    try {
      await onEdit(field.id, value);
    } finally {
      setSaving(null);
    }
  }

  return (
    <section className="review">
      <div className="panel-head">
        <span>{hindi ? "समीक्षा और पुष्टि" : "Review and confirmation"}</span>
        <strong>{department || (hindi ? "संबंधित विभाग" : "Assigned department")}</strong>
      </div>
      <div className="review-scroll">
        <p>
          {hindi
            ? "प्रस्तुत करने से पहले विवरण जाँचें। आप कोई भी मान बदल सकते हैं।"
            : "Check and edit every field before submitting. You can change any suggested value."}
        </p>
        {fields.map((field) => {
          const value = drafts[field.id] ?? "";
          const unchanged = value === text(field);
          const options = FIELD_OPTIONS[field.id];
          const hint = fieldHint(field.id, hindi);
          return (
            <div className="review-row" key={field.id}>
              <label htmlFor={`review-${field.id}`}>
                <span>
                  {fieldLabel(field.id, hindi)}
                  {field.required ? " *" : ""}
                </span>
                {field.id === "photo" ? (
                  <output id={`review-${field.id}`} className="attachment-status">
                    {photoAdded
                      ? hindi
                        ? "तस्वीर जुड़ी है"
                        : "Image attached"
                      : hindi
                        ? "कोई तस्वीर नहीं"
                        : "No image attached"}
                  </output>
                ) : options ? (
                  <span className="choice-bubbles" id={`review-${field.id}`}>
                    {options.map((option) => (
                      <button
                        type="button"
                        className={value === option ? "choice-bubble selected" : "choice-bubble"}
                        key={option}
                        disabled={busy || saving !== null}
                        onClick={() => setDrafts((current) => ({ ...current, [field.id]: option }))}
                      >
                        {hindi
                          ? OPTION_LABELS[option]?.hi || option
                          : OPTION_LABELS[option]?.en || option.replaceAll("_", " ")}
                      </button>
                    ))}
                  </span>
                ) : field.id === "additional_details" ? (
                  <textarea
                    id={`review-${field.id}`}
                    value={value}
                    disabled={busy || saving !== null}
                    placeholder={hint}
                    onChange={(event) =>
                      setDrafts((current) => ({ ...current, [field.id]: event.target.value }))
                    }
                  />
                ) : (
                  <input
                    id={`review-${field.id}`}
                    value={value}
                    disabled={busy || saving !== null}
                    placeholder={hint}
                    onChange={(event) =>
                      setDrafts((current) => ({ ...current, [field.id]: event.target.value }))
                    }
                  />
                )}
              </label>
              {field.id !== "photo" && (
                <button
                  type="button"
                  onClick={() => void save(field)}
                  disabled={busy || saving !== null || unchanged || (field.required && !value.trim())}
                >
                  {saving === field.id
                    ? hindi
                      ? "सहेजा जा रहा है…"
                      : "Saving…"
                    : hindi
                      ? "सहेजें"
                      : "Save"}
                </button>
              )}
            </div>
          );
        })}
      </div>
      <div className="review-actions">
        <button type="button" className="primary" onClick={onSubmit} disabled={busy || saving !== null}>
          {hindi ? "शिकायत प्रस्तुत करें" : "Submit grievance"}
        </button>
        <small>
          {hindi
            ? "यह डेमो रसीद है। कोई सरकारी प्रणाली संपर्क में नहीं है।"
            : "This is a demo acknowledgement. No live government system is contacted."}
        </small>
      </div>
    </section>
  );
}
