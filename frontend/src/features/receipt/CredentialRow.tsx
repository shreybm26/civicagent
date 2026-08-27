import { useState } from "react";

export function CredentialRow({
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
      <div className="credential-row">
        <p className="reference">{value}</p>
        <button type="button" onClick={() => void copy()}>
          {copied ? (copyLabel === "कॉपी" ? "कॉपी हो गया" : "Copied") : copyLabel}
        </button>
      </div>
      {warn && <small>{warn}</small>}
    </div>
  );
}
