import type { Field } from "../../lib/types";

function displayValue(field: Field): string {
  if (field.value == null || field.value === "") return field.required ? "Pending" : "Not provided";
  return String(field.value);
}

export function FieldPanel({
  service,
  fields,
  hindi,
  stateLabel,
}: {
  service?: string;
  fields: Field[];
  hindi: boolean;
  stateLabel: string;
}) {
  return (
    <aside className="fields">
      <div className="panel-head">
        <span>{hindi ? "आवेदन सार" : "Application summary"}</span>
        <strong>{service || (hindi ? "सेवा चयनित नहीं" : "Service not identified")}</strong>
      </div>
      <p className="status-line">
        {hindi ? "स्थिति" : "Status"}: <strong>{stateLabel}</strong>
      </p>
      {fields.length === 0 ? (
        <p className="empty">
          {hindi ? "बातचीत के साथ विवरण यहाँ भरेंगे।" : "Details will appear here as the assistant collects them."}
        </p>
      ) : (
        <table className="form-table">
          <thead>
            <tr>
              <th>{hindi ? "क्षेत्र" : "Field"}</th>
              <th>{hindi ? "मान" : "Value"}</th>
              <th>{hindi ? "स्रोत" : "Source"}</th>
            </tr>
          </thead>
          <tbody>
            {fields.map((field) => (
              <tr key={field.id} className={field.status === "missing" ? "missing" : undefined}>
                <td>
                  {field.id.replaceAll("_", " ")}
                  {field.required ? " *" : ""}
                </td>
                <td>{displayValue(field)}</td>
                <td>{field.source || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </aside>
  );
}
