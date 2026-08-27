import { FormEvent, useState } from "react";
import type { TrackingView } from "../../lib/types";
import { CivicApiError, api } from "../../lib/api";

export function TrackPage({ hindi, initialSrId = "" }: { hindi: boolean; initialSrId?: string }) {
  const [srId, setSrId] = useState(initialSrId);
  const [accessKey, setAccessKey] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [record, setRecord] = useState<TrackingView | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setRecord(null);
    try {
      setRecord(await api.track(srId, accessKey));
    } catch (caught) {
      if (caught instanceof CivicApiError) {
        setError(caught.message);
      } else {
        setError(hindi ? "आवेदन नहीं मिला। विवरण जाँचें।" : "That application could not be opened. Check the details and try again.");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <p className="breadcrumb">
        {hindi ? "मुख्य पृष्ठ" : "Home"} / {hindi ? "नागरिक सेवाएँ" : "Citizen services"} /{" "}
        <strong>{hindi ? "आवेदन ट्रैक करें" : "Track application"}</strong>
      </p>
      <header className="page-title">
        <div>
          <h1>{hindi ? "आवेदन की स्थिति" : "Track a service request"}</h1>
          <p>
            {hindi
              ? "रसीद पर दिया गया सेवा अनुरोध क्रमांक और प्रवेश कुंजी दर्ज करें। यह डेमो लॉगिन है, सरकारी पोर्टल नहीं।"
              : "Enter the service request ID and access key from your acknowledgement. This is a demonstration lookup, not a government login."}
          </p>
        </div>
      </header>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      <section className="track">
        <div className="panel-head">
          <span>{hindi ? "ट्रैकिंग लॉगिन" : "Tracking login"}</span>
          <strong>{hindi ? "केवल डेमो" : "Demo only"}</strong>
        </div>
        <form onSubmit={submit} className="track-form">
          <label htmlFor="sr-id">{hindi ? "सेवा अनुरोध क्रमांक" : "Service request ID"}</label>
          <input
            id="sr-id"
            value={srId}
            onChange={(event) => setSrId(event.target.value)}
            autoComplete="off"
            spellCheck={false}
            placeholder="CIV-20260827-0001-K7M2"
            disabled={busy}
          />
          <label htmlFor="access-key">{hindi ? "प्रवेश कुंजी" : "Access key"}</label>
          <input
            id="access-key"
            value={accessKey}
            onChange={(event) => setAccessKey(event.target.value)}
            autoComplete="off"
            spellCheck={false}
            placeholder="XXXX-XXXX-XXXX"
            disabled={busy}
          />
          <button className="primary" disabled={busy || !srId.trim() || !accessKey.trim()}>
            {hindi ? "स्थिति देखें" : "View status"}
          </button>
        </form>
      </section>
      {record && <TrackingResult record={record} hindi={hindi} />}
    </>
  );
}

function TrackingResult({ record, hindi }: { record: TrackingView; hindi: boolean }) {
  return (
    <section className="receipt">
      <div className="ack-banner">{hindi ? "स्थिति" : "Status"}</div>
      <h2>{record.sr_id}</h2>
      <dl>
        <dt>{hindi ? "वर्तमान स्थिति" : "Current status"}</dt>
        <dd>{record.status}</dd>
        <dt>{hindi ? "विभाग" : "Department"}</dt>
        <dd>{record.department || (hindi ? "नागरिक सेवाएँ" : "Civic services")}</dd>
        <dt>{hindi ? "दर्ज समय" : "Submitted"}</dt>
        <dd>{new Date(record.submitted_at).toLocaleString("en-IN")}</dd>
        {record.location && (
          <>
            <dt>{hindi ? "स्थान" : "Location"}</dt>
            <dd>{record.location}</dd>
          </>
        )}
      </dl>
      <ol className="track-timeline">
        <li className="done">
          <strong>{hindi ? "प्राप्त" : "Received"}</strong>
          <span>{hindi ? "डेमो नागरिक प्रकोष्ठ में दर्ज।" : "Logged with the demonstration civic cell."}</span>
        </li>
        <li>
          <strong>{hindi ? "विभागीय समीक्षा" : "Department review"}</strong>
          <span>{hindi ? "लाइव विभाग से नहीं जोड़ा गया।" : "Not connected to a live department in this prototype."}</span>
        </li>
      </ol>
      {record.fields.length > 0 && (
        <table className="form-table">
          <thead>
            <tr>
              <th>{hindi ? "फ़ील्ड" : "Field"}</th>
              <th>{hindi ? "मान" : "Value"}</th>
            </tr>
          </thead>
          <tbody>
            {record.fields.map((field) => (
              <tr key={field.id}>
                <th>{field.id}</th>
                <td>{formatValue(field.value)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <p className="disclaimer">
        {hindi
          ? "डेमो ट्रैकिंग। किसी सरकारी विभाग को यह आवेदन नहीं भेजा गया।"
          : "Demo tracking only. This application was not sent to a live government department."}
      </p>
    </section>
  );
}

function formatValue(value: unknown): string {
  if (value == null || value === "") return "—";
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
  try {
    return JSON.stringify(value);
  } catch {
    return "—";
  }
}
