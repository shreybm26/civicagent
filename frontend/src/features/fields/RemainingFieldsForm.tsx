import { useState } from "react";
import type { Field } from "../../lib/types";

export function RemainingFieldsForm({ fields, onSave, busy }: { fields: Field[]; onSave: (id: string, value: string) => void; busy: boolean }) {
  const missing = fields.filter((field) => field.required && (field.value == null || field.value === ""));
  const [values, setValues] = useState<Record<string, string>>({});
  if (!missing.length) return null;
  return <div className="chat-step remaining-fields"><h3>Complete the remaining details</h3><p>The image did not confidently provide these required fields.</p>{missing.map((field) => <label key={field.id}>{field.id.replaceAll("_", " ")}<div><input value={values[field.id] ?? ""} onChange={(event) => setValues((current) => ({ ...current, [field.id]: event.target.value }))}/><button type="button" onClick={() => onSave(field.id, values[field.id] ?? "")} disabled={busy || !(values[field.id] ?? "").trim()}>Save</button></div></label>)}</div>;
}
