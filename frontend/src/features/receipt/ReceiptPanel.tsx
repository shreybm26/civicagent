import { useEffect, useRef, useState } from "react";
import type { Field, Receipt } from "../../lib/types";
import { downloadReceiptPdf } from "../../lib/receiptPdf";
import { CredentialRow } from "./CredentialRow";
import { EmailAckForm } from "./EmailAckForm";

export function ReceiptPanel({
  receipt,
  serviceName,
  fields,
  onReset,
  onTrack,
  hindi,
}: {
  receipt: Receipt;
  serviceName?: string | null;
  fields?: Field[];
  onReset: () => void;
  onTrack: () => void;
  hindi: boolean;
}) {
  const [pdfDownloaded, setPdfDownloaded] = useState(false);
  const pdfTimerRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (pdfTimerRef.current) window.clearTimeout(pdfTimerRef.current);
    };
  }, []);

  function handleDownloadPdf() {
    try {
      downloadReceiptPdf({ receipt, serviceName, fields });
      setPdfDownloaded(true);
      if (pdfTimerRef.current) window.clearTimeout(pdfTimerRef.current);
      pdfTimerRef.current = window.setTimeout(() => setPdfDownloaded(false), 2000);
    } catch {
      window.alert(
        hindi ? "PDF डाउनलोड नहीं हो सका। कृपया पुनः प्रयास करें।" : "PDF download failed. Please try again.",
      );
    }
  }

  return (
    <section className="receipt">
      <div className="ack-banner">{hindi ? "पावती" : "Acknowledgement"}</div>
      <h2>{hindi ? "शिकायत दर्ज हो गई है" : "Grievance registered"}</h2>
      <CredentialRow
        label={hindi ? "सेवा अनुरोध क्रमांक" : "Service request ID"}
        value={receipt.reference}
        copyLabel={hindi ? "कॉपी" : "Copy"}
      />
      {receipt.access_key && (
        <CredentialRow
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
      {receipt.access_key && (
        <EmailAckForm srId={receipt.reference} accessKey={receipt.access_key} hindi={hindi} />
      )}
      <p className="disclaimer">
        {hindi
          ? "डेमो रसीद। किसी सरकारी विभाग को यह आवेदन नहीं भेजा गया। आवेदन ट्रैक करने के लिए ऊपर दी गई कुंजी का उपयोग करें।"
          : "Demo receipt only. This application was not sent to a live government department. Use the access key above to track this request."}
      </p>
      <div className="receipt-actions">
        <button
          type="button"
          className={`primary${pdfDownloaded ? " success" : ""}`}
          onClick={handleDownloadPdf}
        >
          {pdfDownloaded
            ? hindi
              ? "PDF डाउनलोड हो गया"
              : "PDF downloaded"
            : hindi
              ? "PDF डाउनलोड"
              : "Download PDF"}
        </button>
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
