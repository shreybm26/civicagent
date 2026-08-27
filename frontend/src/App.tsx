import { useEffect, useState } from "react";
import { api, isExpiredSession, mediaUrl } from "./lib/api";
import { conversation, STATE_LABEL } from "./lib/conversation";
import type { SessionView } from "./lib/types";
import { ChatPanel } from "./features/chat/ChatPanel";
import { FieldPanel } from "./features/fields/FieldPanel";
import { EvidencePanel } from "./features/evidence/EvidencePanel";
import { ReviewCard } from "./features/review/ReviewCard";
import { ReceiptPanel } from "./features/receipt/ReceiptPanel";
import { LocationConfirmation } from "./features/location/LocationConfirmation";
import { RemainingFieldsForm } from "./features/fields/RemainingFieldsForm";
import { TrackPage } from "./features/track/TrackPage";

const FONT_STEPS = ["15px", "16px", "18px"];

function currentPath(): string {
  return window.location.pathname.replace(/\/$/, "") || "/";
}

export default function App() {
  const [path, setPath] = useState(currentPath);
  const [session, setSession] = useState<SessionView | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [hindi, setHindi] = useState(false);
  const [fontStep, setFontStep] = useState(1);
  const onTrackPage = path === "/track";

  function go(next: string) {
    window.history.pushState({}, "", next);
    setPath(next.replace(/\/$/, "") || "/");
  }

  useEffect(() => {
    function onPop() {
      setPath(currentPath());
    }
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  useEffect(() => {
    if (onTrackPage) return;
    if (session) return;
    api.createSession().then(setSession).catch(() => setError("The grievance cell could not start. Please refresh."));
  }, [onTrackPage, session]);

  useEffect(() => {
    document.documentElement.lang = hindi ? "hi" : "en";
    document.documentElement.style.fontSize = FONT_STEPS[fontStep];
  }, [hindi, fontStep]);

  async function run(task: () => Promise<SessionView>, fallback: string) {
    setBusy(true);
    setError("");
    try {
      setSession(await task());
    } catch (caught) {
      if (isExpiredSession(caught)) {
        try {
          setSession(await api.createSession());
          setError("The previous session expired after a server restart. Send the message again.");
          return;
        } catch {
          setError("The session expired. Refresh the page.");
          return;
        }
      }
      setError(caught instanceof Error && caught.message ? caught.message : fallback);
    } finally {
      setBusy(false);
    }
  }

  async function send(value: string) {
    const sessionId = session?.session_id;
    if (!sessionId) {
      setError("The grievance cell could not start. Please refresh.");
      return;
    }
    await run(async () => {
      try {
        return await api.sendMessage(sessionId, value);
      } catch (caught) {
        if (!isExpiredSession(caught)) throw caught;
        const fresh = await api.createSession();
        return api.sendMessage(fresh.session_id, value);
      }
    }, "That message could not be recorded. Try again.");
  }

  if (!onTrackPage && !session) {
    return (
      <div className="gov-shell">
        <UtilityBar hindi={false} onLanguage={() => undefined} onFont={() => undefined} fontStep={1} />
        <Tricolor />
        <Masthead hindi={false} stateLabel="Starting" onReset={() => undefined} busy />
        <main id="main" className="page">
          <p className="notice-banner">{error || "Opening a secure demonstration session…"}</p>
        </main>
      </div>
    );
  }

  const messages = session ? conversation(session) : [];
  const locationMissing = session?.fields.some((field) => field.id === "location" && (field.status === "missing" || field.value == null || field.value === "")) ?? false;
  const showLocation = session?.state === "LOCATION_REQUIRED" || (session?.state === "COLLECTING" && locationMissing);
  const hasLocation = Boolean(session?.location?.address);
  const latestEvidence = session?.evidence?.at(-1);
  const imageHandled = session?.image_decision === "skipped" || Boolean(latestEvidence);
  const stateLabel = session ? (hindi ? STATE_LABEL[session.state]?.hi : STATE_LABEL[session.state]?.en) : (hindi ? "ट्रैकिंग" : "Tracking");
  let contextualStep = null;
  if (session) {
    if (showLocation) {
      contextualStep = <LocationConfirmation
        onConfirm={(pick) => run(() => api.resolveLocationPin(session.session_id, pick), "Location could not be confirmed.")}
        onResolveText={(text) => run(() => api.resolveLocation(session.session_id, text), "Location could not be verified. Try JNTU Metro or Charminar.")}
        busy={busy}
        hindi={hindi}
      />;
    } else if (hasLocation && !imageHandled) {
      contextualStep = <EvidencePanel
        onChoose={(hasImage) => { if (!hasImage) void run(() => api.decideImage(session.session_id, false), "Image choice could not be saved."); }}
        onUpload={(file) => run(() => api.uploadMedia(session.session_id, file), "Photo upload failed. You can continue without a photo.")}
        busy={busy}
        hindi={hindi}
      />;
    } else if (hasLocation && imageHandled && session.state !== "REVIEWING" && session.state !== "COMPLETED") {
      contextualStep = <>
        {latestEvidence && <EvidencePanel onChoose={() => undefined} onUpload={() => undefined} busy={busy} evidence={latestEvidence} hindi={hindi} />}
        <RemainingFieldsForm fields={session.fields} onSave={(id, value) => run(() => api.editField(session.session_id, id, value), "That detail could not be saved.")} busy={busy} />
      </>;
    } else if (session.state === "REVIEWING") {
      contextualStep = <ReviewCard
        fields={session.fields}
        department={session.service?.department}
        onEdit={async (id, value) => {
          setError("");
          try { setSession(await api.editField(session.session_id, id, value)); }
          catch (caught) { setError(caught instanceof Error ? caught.message : "That correction could not be saved."); throw caught; }
        }}
        onSubmit={() => run(() => api.confirm(session.session_id), "Submission failed. Please review and retry.")}
        busy={busy}
        hindi={hindi}
        photoAdded={session.image_decision === "added"}
      />;
    }
  }

  return (
    <div className="gov-shell">
      <a className="skip" href="#main">
        {hindi ? "मुख्य सामग्री पर जाएँ" : "Skip to main content"}
      </a>
      <UtilityBar hindi={hindi} onLanguage={() => setHindi((value) => !value)} onFont={setFontStep} fontStep={fontStep} />
      <Tricolor />
      <Masthead
        hindi={hindi}
        stateLabel={stateLabel || session?.state || "Tracking"}
        onReset={() => session && run(() => api.reset(session.session_id), "Reset failed.")}
        busy={busy}
        showReset={!onTrackPage}
      />
      <nav className="gov-nav" aria-label="Primary">
        <a href="/" aria-current={onTrackPage ? undefined : "page"} onClick={(event) => { event.preventDefault(); go("/"); }}>{hindi ? "शिकायत दर्ज करें" : "Lodge grievance"}</a>
        <a href="/track" aria-current={onTrackPage ? "page" : undefined} onClick={(event) => { event.preventDefault(); go("/track"); }}>{hindi ? "आवेदन ट्रैक करें" : "Track application"}</a>
        <span>{hindi ? "सेवाएँ" : "Services"}</span>
        <span>{hindi ? "सहायता" : "Helpline"}</span>
      </nav>
      <p className="notice-banner" role="note">
        {hindi
          ? "यह एक प्रोटोटाइप है, सरकारी वेबसाइट नहीं। कोई विभाग या भुगतान प्रणाली इससे जुड़ी नहीं है। सभी डेटा काल्पनिक है।"
          : "Prototype only — not an official government website. No department, payment, Aadhaar, or OTP system is connected. All data is synthetic."}
      </p>
      <main id="main" className="page">
        {onTrackPage ? (
          <TrackPage hindi={hindi} initialSrId={session?.receipt?.reference || ""} />
        ) : session ? (
          <>
            <p className="breadcrumb">
              {hindi ? "मुख्य पृष्ठ" : "Home"} / {hindi ? "नागरिक सेवाएँ" : "Citizen services"} / <strong>{hindi ? "शिकायत दर्ज करें" : "Lodge grievance"}</strong>
            </p>
            <header className="page-title">
              <div>
                <h1>{hindi ? "ऑनलाइन नागरिक शिकायत" : "Online civic grievance"}</h1>
                <p>{hindi ? "सामान्य भाषा में बताएँ। सहायक आवश्यक विवरण एकत्र कर समीक्षा फॉर्म दिखाएगा।" : "Describe the issue in plain language. The assistant fills the statutory fields and asks you to confirm before acknowledgement."}</p>
              </div>
              <dl className="app-meta">
                <div>
                  <dt>{hindi ? "आवेदन संदर्भ" : "Application ref."}</dt>
                  <dd>{session.session_id.slice(0, 8).toUpperCase()}</dd>
                </div>
                <div>
                  <dt>{hindi ? "स्थिति" : "Status"}</dt>
                  <dd>{stateLabel}</dd>
                </div>
              </dl>
            </header>
            {error && <p className="error" role="alert">{error}</p>}
            <div className="workspace">
              <div>
                <ChatPanel
                  messages={messages}
                  onSend={send}
                  busy={busy}
                  hindi={hindi}
                  showSuggestions={session.state === "IDLE"}
                  contextualStep={contextualStep}
                  composerEnabled={!session.service_id}
                  mediaUrl={(mediaId) => mediaUrl(session.session_id, mediaId)}
                />
                {session.state === "COMPLETED" && session.receipt && (
                  <ReceiptPanel
                    receipt={session.receipt}
                    onReset={() => run(() => api.reset(session.session_id), "Reset failed.")}
                    onTrack={() => go("/track")}
                    hindi={hindi}
                  />
                )}
              </div>
              <FieldPanel service={session.service?.name} fields={session.fields} hindi={hindi} stateLabel={stateLabel || session.state} />
            </div>
          </>
        ) : null}
      </main>
      <footer className="gov-footer">
        <div>
          <p><strong>{hindi ? "नगरपालिका नागरिक प्रकोष्ठ" : "Municipal Civic Cell"}</strong></p>
          <p>{hindi ? "नागरिक शिकायत निवारण का डेमो पोर्टल" : "Demonstration portal for civic grievance intake"}</p>
        </div>
        <ul>
          <li>{hindi ? "गोपनीयता नीति" : "Privacy policy"}</li>
          <li>{hindi ? "नियम और शर्तें" : "Terms of use"}</li>
          <li>{hindi ? "सहायता: 1800-000-000 (डेमो)" : "Helpline: 1800-000-000 (demo)"}</li>
        </ul>
        <p className="footer-note">
          CivicAgent · Build What Moves India · {hindi ? "आधिकारिक भारत सरकार पोर्टल नहीं" : "Not an official Government of India website"}
        </p>
      </footer>
    </div>
  );
}

function UtilityBar({
  hindi,
  onLanguage,
  onFont,
  fontStep,
}: {
  hindi: boolean;
  onLanguage: () => void;
  onFont: (step: number) => void;
  fontStep: number;
}) {
  return (
    <div className="utility">
      <span>भारत सरकार | Government of India</span>
      <div className="utility-actions">
        <button type="button" onClick={onLanguage}>{hindi ? "English" : "हिन्दी"}</button>
        <span className="font-controls" aria-label="Text size">
          <button type="button" onClick={() => onFont(Math.max(0, fontStep - 1))} disabled={fontStep === 0}>A-</button>
          <button type="button" onClick={() => onFont(1)}>A</button>
          <button type="button" onClick={() => onFont(Math.min(2, fontStep + 1))} disabled={fontStep === 2}>A+</button>
        </span>
      </div>
    </div>
  );
}

function Tricolor() {
  return (
    <div className="tricolor" aria-hidden="true">
      <i className="saffron" />
      <i className="white" />
      <i className="green" />
    </div>
  );
}

function Masthead({
  hindi,
  stateLabel,
  onReset,
  busy,
  showReset = true,
}: {
  hindi: boolean;
  stateLabel: string;
  onReset: () => void;
  busy: boolean;
  showReset?: boolean;
}) {
  return (
    <header className="masthead">
      <div className="lockup">
        <Seal />
        <div>
          <p className="org-hi">नगरपालिका नागरिक प्रकोष्ठ</p>
          <p className="org-en">Municipal Civic Cell</p>
          <p className="org-sub">{hindi ? "हैदराबाद प्रदर्शन · CivicAgent प्रोटोटाइप" : "Hyderabad demonstration · CivicAgent prototype"}</p>
        </div>
      </div>
      <div className="masthead-actions">
        <p className="live-status">{stateLabel}</p>
        {showReset && <button type="button" onClick={onReset} disabled={busy}>{hindi ? "आवेदन रीसेट" : "Reset application"}</button>}
      </div>
    </header>
  );
}

function Seal() {
  return (
    <svg className="seal" viewBox="0 0 72 72" role="img" aria-label="Municipal Civic Cell">
      <circle cx="36" cy="36" r="34" fill="#0b3a6e" stroke="#c9a227" strokeWidth="3" />
      <circle cx="36" cy="36" r="26" fill="none" stroke="#f4f1e8" strokeWidth="1.5" />
      <path d="M18 46 V28 h8 v6 h8 V28 h8 v18 h-6 V36 h-6 v10 z" fill="#f4f1e8" />
      <rect x="22" y="48" width="28" height="4" fill="#c9a227" />
    </svg>
  );
}
