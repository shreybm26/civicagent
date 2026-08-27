import type { Field } from "../../lib/types";

export function ReviewCard({
  fields,
  department,
  onEdit,
  onSubmit,
  busy,
  hindi,
}: {
  fields: Field[];
  department?: string;
  onEdit: (id: string, value: string) => void;
  onSubmit: () => void;
  busy: boolean;
  hindi: boolean;
}) {
  return (
    <section className="review">
      <div className="panel-head">
        <span>{hindi ? "समीक्षा और पुष्टि" : "Review and confirmation"}</span>
        <strong>{department || (hindi ? "संबंधित विभाग" : "Assigned department")}</strong>
      </div>
      <p>{hindi ? "प्रस्तुत करने से पहले विवरण जाँचें। बिना पुष्टि के कुछ नहीं भेजा जाता।" : "Check every field before submitting. Nothing is sent until you confirm."}</p>
      {fields.map((field) => (
        <div className="review-row" key={field.id}>
          <label>
            {field.id.replaceAll("_", " ")}
            <input value={String(field.value ?? "")} onChange={(event) => onEdit(field.id, event.target.value)} />
          </label>
        </div>
      ))}
      <button className="primary" onClick={onSubmit} disabled={busy}>
        {hindi ? "शिकायत प्रस्तुत करें" : "Submit grievance"}
      </button>
      <small>{hindi ? "यह डेमो रसीद है। कोई सरकारी प्रणाली संपर्क में नहीं है।" : "This is a demo acknowledgement. No live government system is contacted."}</small>
    </section>
  );
}
