import type { Receipt } from "../../lib/types";
import { useState } from "react";

export function ReceiptPanel({
  receipt,
  onReset,
  onTrack,
  hindi,
}: {
  receipt: Receipt;
  onReset: () => void;
  onTrack: () => void;
  hindi: boolean;
}) {
  return (
    <section className="receipt">
      <div className="ack-banner">{hindi ? "पावती" : "Acknowledgement"}</div>
      <h2>{hindi ? "शिकायत दर्ज हो गई है" : "Grievance registered"}</h2>
      <Credential
        label={hindi ? "सेवा अनुरोध क्रमांक" : "Service request ID"}
        value={receipt.reference}
        copyLabel={hindi ? "कॉपी" : "Copy"}
      />
      {receipt.access_key && (
        <Credential
          label={hindi ? "प्रवेश कुंजी" : "Access key"}
          value={receipt.access_key}
          copyLabel={hindi ? "कॉपी" : "Copy"}
          warn={
            hindi
              ? "यह कुंजी केवल एक बार दिखाई गई है। इसे सुरक्षित रखें।"
              : "This key is shown once. Save it to track this request later."
          }
        />
      )}
      <dl>
        <dt>{hindi ? "स्थिति" : "Status"}</dt>
        <dd>{receipt.status}</dd>
        <dt>{hindi ? "विभाग" : "Department"}</dt>
        <dd>{receipt.department || (hindi ? "नागरिक सेवाएँ" : "Civic services")}</dd>
        <dt>{hindi ? "समय" : "Time"}</dt>
        <dd>{new Date(receipt.timestamp).toLocaleString("en-IN")}</dd>
      </dl>
      <p className="disclaimer">
        {hindi
          ? "डेमो रसीद। किसी सरकारी विभाग को यह आवेदन नहीं भेजा गया। आवेदन ट्रैक करने के लिए ऊपर दी गई कुंजी का उपयोग करें।"
          : "Demo receipt only. This application was not sent to a live government department. Use the access key above to track this request."}
      </p>
      <div className="receipt-actions">
        <button type="button" className="primary" onClick={onTrack}>
          {hindi ? "यह आवेदन ट्रैक करें" : "Track this request"}
        </button>
        <button type="button" onClick={onReset}>
          {hindi ? "नई शिकायत दर्ज करें" : "Lodge another grievance"}
        </button>
      </div>
    </section>
  );
}

function Credential({
  label,
  value,
  copyLabel,
  warn,
}: {
  label: string;
  value: string;
  copyLabel: string;
  warn?: string;
}) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(value);
    } catch {
      const field = document.createElement("textarea");
      field.value = value;
      document.body.appendChild(field);
      field.select();
      document.execCommand("copy");
      field.remove();
    }
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <div className="credential">
      <p className="credential-label">{label}</p>
      <p className="reference">{value}</p>
      <button type="button" onClick={() => void copy()}>
        {copied ? "Copied" : copyLabel}
      </button>
      {warn && <small>{warn}</small>}
    </div>
  );
}
