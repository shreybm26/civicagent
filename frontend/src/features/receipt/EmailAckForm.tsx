import { FormEvent, useState } from "react";
import { CivicApiError, api } from "../../lib/api";

export function EmailAckForm({
  srId,
  accessKey,
  hindi,
}: {
  srId: string;
  accessKey: string;
  hindi: boolean;
}) {
  const [email, setEmail] = useState("");
  const [confirmSend, setConfirmSend] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [sentTo, setSentTo] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const result = await api.sendTrackEmail(srId, accessKey, email, confirmSend);
      setSentTo(result.to);
    } catch (caught) {
      if (caught instanceof CivicApiError) {
        setError(caught.message);
      } else {
        setError(hindi ? "ईमेल नहीं भेजा जा सका।" : "The acknowledgement email could not be sent.");
      }
    } finally {
      setBusy(false);
    }
  }

  if (sentTo) {
    return (
      <div className="email-ack email-ack-sent" role="status">
        <strong>{hindi ? "ईमेल भेज दिया गया" : "Email sent"}</strong>
        <p>
          {hindi
            ? `पावती ${sentTo} पर भेज दी गई है। सेवा अनुरोध क्रमांक और प्रवेश कुंजी उस संदेश में हैं।`
            : `Acknowledgement sent to ${sentTo}. The service request ID and access key are in that message.`}
        </p>
      </div>
    );
  }

  return (
    <form className="email-ack" onSubmit={submit}>
      <h3>{hindi ? "पावती ईमेल भेजें" : "Email this acknowledgement"}</h3>
      <p>
        {hindi
          ? "संदेश में सेवा अनुरोध क्रमांक, प्रवेश कुंजी और ट्रैकिंग लिंक होगा। पता जाँच लें — गलत पते पर कुंजी चली जाएगी। यह सरकारी मेल नहीं है। Resend टेस्ट सेंडर केवल उसी खाते के इनबॉक्स पर भेजता है जिसने API कुंजी बनाई।"
          : "The message includes the service request ID, access key, and a tracking link. Check the address — a typo sends the key to the wrong inbox. This is not official government mail. The Resend test sender only delivers to the account that created the API key."}
      </p>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      <label htmlFor={`ack-email-${srId}`}>{hindi ? "ईमेल पता" : "Email address"}</label>
      <input
        id={`ack-email-${srId}`}
        type="email"
        inputMode="email"
        autoComplete="email"
        value={email}
        onChange={(event) => {
          setEmail(event.target.value);
          setConfirmSend(false);
        }}
        placeholder="you@example.com"
        disabled={busy}
        required
      />
      <label className="email-confirm">
        <input
          type="checkbox"
          checked={confirmSend}
          onChange={(event) => setConfirmSend(event.target.checked)}
          disabled={busy || !email.trim()}
        />
        {hindi
          ? "मैंने पता जाँच लिया है। इस इनबॉक्स पर प्रवेश कुंजी भेजें।"
          : "I checked the address. Send the access key to this inbox."}
      </label>
      <button className="primary" disabled={busy || !email.trim() || !confirmSend}>
        {busy ? (hindi ? "भेजा जा रहा है…" : "Sending…") : hindi ? "ईमेल भेजें" : "Send email"}
      </button>
    </form>
  );
}
