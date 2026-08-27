import type { Evidence } from "../../lib/types";
import { localizeAgentText } from "../../lib/i18n";

export function EvidencePanel({
  onChoose,
  onUpload,
  busy,
  evidence,
  hindi,
}: {
  onChoose: (hasImage: boolean) => void;
  onUpload: (file: File) => void;
  busy: boolean;
  evidence?: Evidence;
  hindi: boolean;
}) {
  if (evidence) {
    return (
      <div className="chat-step evidence-result">
        <h3>
          {evidence.relevant
            ? hindi
              ? "तस्वीर का विश्लेषण"
              : "Image analysis"
            : hindi
              ? "तस्वीर फ़ॉर्म के लिए उपयोग नहीं हुई"
              : "Image not used for form fields"}
        </h3>
        <p>{localizeAgentText(evidence.reason, hindi)}</p>
        {evidence.relevant && evidence.summary && <p>{localizeAgentText(evidence.summary, hindi)}</p>}
        {evidence.relevant && evidence.details.length > 0 && (
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
            ? "सुझाए गए मान आवेदन सार में बदले जा सकते हैं।"
            : "You can change any suggested values in the application summary."}
        </p>
      </div>
    );
  }

  return (
    <div className="chat-step image-choice">
      <h3>{hindi ? "क्या आपके पास तस्वीर है?" : "Do you have a photo of the issue?"}</h3>
      <p>
        {hindi
          ? "तस्वीर से केवल स्पष्ट और भरोसेमंद जानकारी भरी जाएगी। आप बाद में सार में बदल सकते हैं।"
          : "I will use only clear, confident details from the image. You can change them later in the summary."}
      </p>
      <div className="step-actions">
        <label className="upload-button">
          {hindi ? "तस्वीर जोड़ें" : "Add image"}
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
