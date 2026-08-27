import { useState } from "react";
import type { Field } from "../../lib/types";

const OPTIONS: Record<string, string[]> = { severity: ["low", "medium", "high"], leak_type: ["pipe", "tap", "supply", "unknown"], issue_type: ["sewage", "drain", "public_hygiene", "other"] };

export function RemainingFieldsForm({ fields, onSave, busy }: { fields: Field[]; onSave: (id: string, value: string) => void; busy: boolean }) {
  const missing = fields.filter((field) => field.required && (field.value == null || field.value === ""));
  const [values, setValues] = useState<Record<string, string>>({});
  if (!missing.length) return null;
  return <div className="chat-step remaining-fields"><h3>Complete the remaining details</h3><p>The image did not confidently provide these required fields.</p>{missing.map((field) => { const value = values[field.id] ?? ""; const options = OPTIONS[field.id]; return <label key={field.id}>{field.id.replaceAll("_", " ")}<div className={options ? "choice-bubbles" : undefined}>{options ? options.map((option) => <button type="button" className={value === option ? "choice-bubble selected" : "choice-bubble"} key={option} onClick={() => setValues((current) => ({ ...current, [field.id]: option }))} disabled={busy}>{option}</button>) : <input value={value} onChange={(event) => setValues((current) => ({ ...current, [field.id]: event.target.value }))} />}<button type="button" onClick={() => onSave(field.id, value)} disabled={busy || !value.trim()}>Save</button></div></label>; })}</div>;
}
