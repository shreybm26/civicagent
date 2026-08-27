export function EvidencePanel({
  onUpload,
  busy,
  result,
  hindi,
}: {
  onUpload: (file: File) => void;
  busy: boolean;
  result?: string;
  hindi: boolean;
}) {
  return (
    <section className="evidence">
      <div className="panel-head">
        <span>{hindi ? "साक्ष्य" : "Supporting evidence"}</span>
        <strong>{hindi ? "JPEG / PNG" : "JPEG or PNG only"}</strong>
      </div>
      <label className="upload">
        {hindi ? "फोटो संलग्न करें" : "Attach a photograph of the issue"}
        <input
          type="file"
          accept="image/jpeg,image/png"
          disabled={busy}
          onChange={(event) => event.target.files?.[0] && onUpload(event.target.files[0])}
        />
      </label>
      {result && <p role="status">{result}</p>}
      <small>{hindi ? "सेल्फी स्वीकार नहीं की जाएगी।" : "Selfies are rejected. The report can continue without a photo."}</small>
    </section>
  );
}
