import { FormEvent, useState } from "react";
import type { TrackingView } from "../../lib/types";
import { CivicApiError, api } from "../../lib/api";
import { fieldLabel } from "../../lib/fieldLabels";
import { CredentialRow } from "../receipt/CredentialRow";
import { EmailAckForm } from "../receipt/EmailAckForm";

export function TrackPage({ hindi, initialSrId = "" }: { hindi: boolean; initialSrId?: string }) {
  const [srId, setSrId] = useState(initialSrId);
  const [accessKey, setAccessKey] = useState("");
  const [verifiedKey, setVerifiedKey] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [record, setRecord] = useState<TrackingView | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setRecord(null);
    setVerifiedKey("");
    try {
      const tracked = await api.track(srId, accessKey);
      setRecord(tracked);
      setVerifiedKey(accessKey.trim().toUpperCase().replace(/\s+/g, ""));
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
      {record && <TrackingResult record={record} accessKey={verifiedKey} hindi={hindi} />}
    </>
  );
}

function TrackingResult({
  record,
  accessKey,
  hindi,
}: {
  record: TrackingView;
  accessKey: string;
  hindi: boolean;
}) {
  const nearby = record.nearby ?? [];
  const typeCounts = record.type_counts ?? [];
  const timeline = record.timeline ?? [];
  const maxCount = Math.max(1, ...typeCounts.map((item) => item.count));

  return (
    <section className="receipt">
      <div className="ack-banner">{hindi ? "स्थिति" : "Status"}</div>
      <h2>{hindi ? "ट्रैकिंग विवरण" : "Tracking details"}</h2>
      <CredentialRow
        label={hindi ? "सेवा अनुरोध क्रमांक" : "Service request ID"}
        value={record.sr_id}
        copyLabel={hindi ? "कॉपी" : "Copy"}
      />
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
      {timeline.length > 0 && (
        <ol className="track-timeline">
          {timeline.map((step) => (
            <li key={step.id} className={step.done ? "done" : "pending"}>
              <strong>{timelineTitle(step.id, step.title, hindi)}</strong>
              <span>{timelineDetail(step.id, step.detail, hindi)}</span>
              {step.at && <em>{new Date(step.at).toLocaleString("en-IN")}</em>}
            </li>
          ))}
        </ol>
      )}
      {typeCounts.length > 0 && (
        <div className="neighbourhood">
          <h3>{hindi ? "आस-पास की शिकायतें" : "Nearby reports"}</h3>
          <p className="neighbourhood-note">
            {hindi
              ? "डेमो आस-पड़ोस चित्र। गिनती में सिंथेटिक नमूने और इस डेमो में दर्ज अन्य टिकट शामिल हैं। यह लाइव नगरपालिका डेटा नहीं है।"
              : record.neighbourhood_note ||
                "Demonstration neighbourhood picture. Counts mix synthetic nearby samples with other tickets filed in this demo. Not live municipal data."}
          </p>
          <ul className="type-bars">
            {typeCounts.map((item) => (
              <li key={item.service_id}>
                <span>{item.label}</span>
                <div className="type-bar-track" aria-hidden="true">
                  <div className="type-bar-fill" style={{ width: `${Math.round((item.count / maxCount) * 100)}%` }} />
                </div>
                <strong>{item.count}</strong>
              </li>
            ))}
          </ul>
          {nearby.length > 0 && (
            <ul className="nearby-list">
              {nearby.map((item, index) => (
                <li key={`${item.service_id}-${item.source}-${index}`}>
                  <strong>{item.label}</strong>
                  <span>
                    {item.distance_km.toFixed(2)} km · {item.status} ·{" "}
                    {item.source === "filed"
                      ? hindi
                        ? "इस डेमो में दर्ज"
                        : "filed in this demo"
                      : hindi
                        ? "सिंथेटिक नमूना"
                        : "demonstration sample"}
                    {item.count > 1 ? ` ×${item.count}` : ""}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
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
                <th>{fieldLabel(field.id, hindi)}</th>
                <td>{formatValue(field.value)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {accessKey && <EmailAckForm srId={record.sr_id} accessKey={accessKey} hindi={hindi} />}
      <p className="disclaimer">
        {hindi
          ? "डेमो ट्रैकिंग। किसी सरकारी विभाग को यह आवेदन नहीं भेजा गया।"
          : "Demo tracking only. This application was not sent to a live government department."}
      </p>
    </section>
  );
}

function timelineTitle(id: string, fallback: string, hindi: boolean): string {
  if (!hindi) return fallback;
  if (id === "received") return "प्राप्त";
  if (id === "logged") return "डेमो नागरिक प्रकोष्ठ में दर्ज";
  if (id === "ward") return "वार्ड आवंटन की प्रतीक्षा";
  return fallback;
}

function timelineDetail(id: string, fallback: string, hindi: boolean): string {
  if (!hindi) return fallback;
  if (id === "received") return "इस प्रदर्शन नागरिक प्रकोष्ठ के लिए पावती बनाई गई।";
  if (id === "logged") return "दर्ज विवरण ट्रैकिंग के लिए संग्रहीत हैं। किसी लाइव विभाग को सूचना नहीं गई।";
  if (id === "ward") return "प्रोटोटाइप में यह चरण लंबित रहता है। उत्पादन में यहाँ ULB API होता।";
  return fallback;
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
