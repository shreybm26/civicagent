import { useState } from "react";

type Props = {
  address?: string;
  lat?: number;
  lng?: number;
  confidence?: number;
  onResolve: (text: string) => void;
  busy?: boolean;
  hindi?: boolean;
};

export function LocationConfirmation({ address, lat, lng, confidence, onResolve, busy, hindi }: Props) {
  const [text, setText] = useState("");
  const [coords, setCoords] = useState(lat && lng ? { lat, lng } : null as null | { lat: number; lng: number });
  const [error, setError] = useState("");

  function locate() {
    if (!navigator.geolocation) {
      setError(hindi ? "स्थान अनुमति उपलब्ध नहीं है। कोई स्थलचिह्न लिखें।" : "Location permission is unavailable. Type a landmark instead.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setCoords({ lat: position.coords.latitude, lng: position.coords.longitude });
        setError(hindi ? "निर्देशांक चुने गए। सत्यापन के लिए स्थलचिह्न लिखें।" : "Coordinates selected. Add a landmark so the address can be verified.");
      },
      () => setError(hindi ? "स्थान अनुमति अस्वीकृत। कोई क्षेत्र लिखें।" : "Location permission was denied. Type a landmark or area instead."),
      { timeout: 5000 },
    );
  }

  return (
    <section className="location" aria-labelledby="location-title">
      <div className="panel-head">
        <span id="location-title">{hindi ? "स्थान की पुष्टि" : "Confirm location"}</span>
        <strong>{hindi ? "हैदराबाद निर्देशिका" : "Hyderabad directory"}</strong>
      </div>
      {address && (
        <p>
          <strong>{address}</strong>
          {confidence != null && (
            <small>
              {hindi ? "डेमो स्थान सूची से मिलान" : "Matched from the demo location directory"} · {Math.round(confidence * 100)}%
            </small>
          )}
        </p>
      )}
      <div
        className="coordinate-box"
        role="img"
        aria-label={coords ? `Selected coordinates ${coords.lat.toFixed(5)}, ${coords.lng.toFixed(5)}` : "No coordinates selected"}
      >
        {coords ? (
          <>
            <span className="pin">+</span>
            <code>
              {coords.lat.toFixed(5)}, {coords.lng.toFixed(5)}
            </code>
          </>
        ) : (
          <span>{hindi ? "कोई पिन चयनित नहीं" : "No pin selected"}</span>
        )}
      </div>
      <button type="button" onClick={locate} disabled={busy}>
        {hindi ? "वर्तमान स्थान का उपयोग करें" : "Use my current location"}
      </button>
      <label htmlFor="landmark">{hindi ? "landmark, सड़क या क्षेत्र" : "Landmark, street or area"}</label>
      <div className="location-input">
        <input
          id="landmark"
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Near JNTU Metro, Kukatpally"
        />
        <button type="button" className="primary" onClick={() => text.trim() && onResolve(text.trim())} disabled={busy || !text.trim()}>
          {hindi ? "स्थान जाँचें" : "Check location"}
        </button>
      </div>
      {error && <p role="status">{error}</p>}
      <small>{hindi ? "मानचित्र उपलब्ध न हो तो टाइप किया landmark हमेशा काम करता है।" : "A typed landmark always works if maps, network, or location permission are unavailable. Try JNTU Metro, Charminar, or Ameerpet."}</small>
    </section>
  );
}
