import type { Evidence } from "../../lib/types";
import { localizeAgentText } from "../../lib/i18n";

export function EvidencePanel({
  onChoose,
  onUpload,
  busy,
  evidence,
  hindi,
  rejectedReason,
}: {
  onChoose: (hasImage: boolean) => void;
  onUpload: (file: File) => void;
  busy: boolean;
  evidence?: Evidence;
  hindi: boolean;
  /** Shown when the last upload was kept in history but rejected as irrelevant. */
  rejectedReason?: string | null;
}) {
  if (evidence?.relevant) {
    return (
      <div className="chat-step evidence-result">
        <h3>{hindi ? "तस्वीर का विश्लेषण" : "Image analysis"}</h3>
        <p>{localizeAgentText(evidence.reason, hindi)}</p>
        {evidence.summary && <p>{localizeAgentText(evidence.summary, hindi)}</p>}
        {evidence.details.length > 0 && (
          <ul>
            {evidence.details.map((detail) => (
              <li key={`${detail.label}-${detail.value}`}>
                <strong>{detail.label}:</strong> {detail.value} ({Math.round(detail.confidence * 100)}%)
              </li>
            ))}
          </ul>
        )}
        <p className="hint">
          {hindi
            ? "सुझाए गए मान समीक्षा में बदले जा सकते हैं।"
            : "You can change any suggested values during review."}
        </p>
      </div>
    );
  }

  return (
    <div className="chat-step image-choice">
      {rejectedReason ? (
        <>
          <h3>{hindi ? "तस्वीर इस शिकायत के लिए उपयुक्त नहीं है" : "This photo is not relevant"}</h3>
          <p>{localizeAgentText(rejectedReason, hindi)}</p>
          <p>
            {hindi
              ? "कृपया समस्या की सही तस्वीर अपलोड करें, या बिना तस्वीर जारी रखें।"
              : "Please upload a correct photo of the issue, or continue without an image."}
          </p>
        </>
      ) : (
        <>
          <h3>{hindi ? "क्या आपके पास तस्वीर है?" : "Do you have a photo of the issue?"}</h3>
          <p>
            {hindi
              ? "तस्वीर से केवल स्पष्ट और भरोसेमंद जानकारी भरी जाएगी। आप बाद में समीक्षा में बदल सकते हैं।"
              : "I will use only clear, confident details from the image. You can change them later during review."}
          </p>
        </>
      )}
      <div className="step-actions">
        <label className="upload-button">
          {rejectedReason ? (hindi ? "सही तस्वीर अपलोड करें" : "Upload correct image") : hindi ? "तस्वीर जोड़ें" : "Add image"}
          <input
            type="file"
            accept="image/jpeg,image/png"
            disabled={busy}
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) {
                onChoose(true);
                onUpload(file);
              }
              event.currentTarget.value = "";
            }}
          />
        </label>
        <button type="button" onClick={() => onChoose(false)} disabled={busy}>
          {hindi ? "कोई तस्वीर नहीं" : "No image"}
        </button>
      </div>
    </div>
  );
}
