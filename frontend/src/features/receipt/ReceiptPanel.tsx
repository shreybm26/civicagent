import type { Receipt } from "../../lib/types";

export function ReceiptPanel({
  receipt,
  onReset,
  hindi,
}: {
  receipt: Receipt;
  onReset: () => void;
  hindi: boolean;
}) {
  return (
    <section className="receipt">
      <div className="ack-banner">{hindi ? "पावती" : "Acknowledgement"}</div>
      <h2>{hindi ? "शिकायत दर्ज हो गई है" : "Grievance registered"}</h2>
      <p className="reference">{receipt.reference}</p>
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
          ? "डेमो रसीद। किसी सरकारी विभाग को यह आवेदन नहीं भेजा गया।"
          : "Demo receipt only. This application was not sent to a live government department."}
      </p>
      <button onClick={onReset}>{hindi ? "नई शिकायत दर्ज करें" : "Lodge another grievance"}</button>
    </section>
  );
}
