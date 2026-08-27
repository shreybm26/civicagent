import { useEffect, useState } from "react";
import type { Field } from "../../lib/types";

const FIELD_OPTIONS: Record<string, string[]> = { severity: ["low", "medium", "high"], leak_type: ["pipe", "tap", "supply", "unknown"], issue_type: ["sewage", "drain", "public_hygiene", "other"] };
const text = (field: Field) => field.value == null ? "" : String(field.value);

export function ReviewCard({ fields, department, onEdit, onSubmit, busy, hindi, photoAdded }: { fields: Field[]; department?: string; onEdit: (id: string, value: string) => Promise<void>; onSubmit: () => void; busy: boolean; hindi: boolean; photoAdded: boolean }) {
  const [drafts, setDrafts] = useState<Record<string, string>>(() => Object.fromEntries(fields.map((field) => [field.id, text(field)])));
  const [saving, setSaving] = useState<string | null>(null);
  useEffect(() => { setDrafts((current) => { const next = { ...current }; for (const field of fields) if (saving !== field.id) next[field.id] = text(field); return next; }); }, [fields, saving]);
  async function save(field: Field) { const value = drafts[field.id] ?? ""; if (field.required && !value.trim()) return; setSaving(field.id); try { await onEdit(field.id, value); } finally { setSaving(null); } }
  return <section className="review">
    <div className="panel-head"><span>{hindi ? "समीक्षा और पुष्टि" : "Review and confirmation"}</span><strong>{department || (hindi ? "संबंधित विभाग" : "Assigned department")}</strong></div>
    <p>{hindi ? "प्रस्तुत करने से पहले विवरण जाँचें।" : "Check and edit every field before submitting."}</p>
    {fields.map((field) => { const value = drafts[field.id] ?? ""; const unchanged = value === text(field); const options = FIELD_OPTIONS[field.id]; return <div className="review-row" key={field.id}>
      <label htmlFor={`review-${field.id}`}><span>{field.id.replaceAll("_", " ")}{field.required ? " *" : ""}</span>
        {field.id === "photo" ? <output id={`review-${field.id}`} className="attachment-status">{photoAdded ? "Image attached" : "No image attached"}</output> : options ? <select id={`review-${field.id}`} value={value} disabled={busy || saving !== null} onChange={(event) => setDrafts((current) => ({ ...current, [field.id]: event.target.value }))}><option value="">Select</option>{options.map((option) => <option key={option} value={option}>{option.replaceAll("_", " ")}</option>)}</select> : field.id === "additional_details" ? <textarea id={`review-${field.id}`} value={value} disabled={busy || saving !== null} onChange={(event) => setDrafts((current) => ({ ...current, [field.id]: event.target.value }))} /> : <input id={`review-${field.id}`} value={value} disabled={busy || saving !== null} onChange={(event) => setDrafts((current) => ({ ...current, [field.id]: event.target.value }))} />}
      </label>{field.id !== "photo" && <button type="button" onClick={() => void save(field)} disabled={busy || saving !== null || unchanged || (field.required && !value.trim())}>{saving === field.id ? "Saving..." : "Save"}</button>}
    </div>; })}
    <button type="button" className="primary" onClick={onSubmit} disabled={busy || saving !== null}>{hindi ? "शिकायत प्रस्तुत करें" : "Submit grievance"}</button>
    <small>{hindi ? "यह डेमो रसीद है। कोई सरकारी प्रणाली संपर्क में नहीं है।" : "This is a demo acknowledgement. No live government system is contacted."}</small>
  </section>;
}
