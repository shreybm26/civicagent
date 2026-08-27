import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

type Pick = { lat: number; lng: number; label: string };

const MAP_CENTER: [number, number] = [17.385, 78.4867];

export function LocationConfirmation({
  onConfirm,
  onResolveText,
  busy,
  hindi,
}: {
  onConfirm: (pick: Pick) => void;
  onResolveText: (text: string) => void;
  busy?: boolean;
  hindi?: boolean;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);
  const [open, setOpen] = useState(false);
  const [pick, setPick] = useState<Pick | null>(null);
  const [text, setText] = useState("");
  const [locating, setLocating] = useState(false);

  async function update(next: { lat: number; lng: number }) {
    setPick({ ...next, label: `Pinned location (${next.lat.toFixed(5)}, ${next.lng.toFixed(5)})` });
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${next.lat}&lon=${next.lng}`,
        { headers: { Accept: "application/json" } },
      );
      if (!response.ok) return;
      const data = (await response.json()) as { display_name?: string };
      if (data.display_name) setPick({ ...next, label: data.display_name.split(",").slice(0, 4).join(",") });
    } catch {
      /* coordinates remain the fallback */
    }
  }

  useEffect(() => {
    if (!open || !containerRef.current || mapRef.current) return;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
      iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
      shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
    });
    const map = L.map(containerRef.current, { center: MAP_CENTER, zoom: 13, scrollWheelZoom: true });
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);

    map.on("click", (event) => {
      if (!markerRef.current) {
        const marker = L.marker(event.latlng, { draggable: true }).addTo(map);
        marker.on("dragend", () => {
          const point = marker.getLatLng();
          void update(point);
        });
        markerRef.current = marker;
      } else {
        markerRef.current.setLatLng(event.latlng);
      }
      void update(event.latlng);
    });

    mapRef.current = map;
    const observer = new ResizeObserver(() => map.invalidateSize({ animate: false }));
    observer.observe(containerRef.current);
    const timer = window.setTimeout(() => map.invalidateSize({ animate: false }), 100);
    return () => {
      window.clearTimeout(timer);
      observer.disconnect();
      map.remove();
      mapRef.current = null;
      markerRef.current = null;
    };
  }, [open]);

  function locate() {
    if (!navigator.geolocation) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const next = { lat: position.coords.latitude, lng: position.coords.longitude };
        if (!markerRef.current && mapRef.current) {
          const marker = L.marker(next, { draggable: true }).addTo(mapRef.current);
          marker.on("dragend", () => {
            const point = marker.getLatLng();
            void update(point);
          });
          markerRef.current = marker;
        } else {
          markerRef.current?.setLatLng(next);
        }
        mapRef.current?.setView(next, 16);
        void update(next).finally(() => setLocating(false));
      },
      () => setLocating(false),
      { enableHighAccuracy: true, timeout: 10000 },
    );
  }

  if (!open) {
    return (
      <div className="chat-step location-step location-collapsed">
        <button type="button" className="primary location-open" disabled={busy} onClick={() => setOpen(true)}>
          {hindi ? "स्थान" : "Location"}
        </button>
      </div>
    );
  }

  return (
    <div className="chat-step location-step" aria-labelledby="location-step-title">
      <div className="step-actions location-toolbar">
        <h3 id="location-step-title">{hindi ? "स्थान चुनें" : "Select the issue location"}</h3>
        <button type="button" onClick={() => setOpen(false)} disabled={busy}>
          {hindi ? "बंद करें" : "Close"}
        </button>
      </div>
      <p>{hindi ? "मानचित्र पर टैप करें या पिन खींचें।" : "Click the map or drag the pin, then confirm the selected location."}</p>
      <div ref={containerRef} className="location-map" aria-label="Draggable location map" />
      <p className="selected-location">
        <strong>{hindi ? "चयनित:" : "Selected:"}</strong>{" "}
        {pick?.label || (hindi ? "अभी कुछ नहीं चुना" : "None selected yet")}
      </p>
      <div className="step-actions">
        <button type="button" onClick={locate} disabled={busy || locating}>
          {locating
            ? hindi
              ? "स्थान खोजा जा रहा है…"
              : "Finding location..."
            : hindi
              ? "मेरा स्थान उपयोग करें"
              : "Use my location"}
        </button>
        <button
          type="button"
          className="primary"
          onClick={() => pick && onConfirm(pick)}
          disabled={busy || !pick}
        >
          {hindi ? "स्थान की पुष्टि करें" : "Confirm location"}
        </button>
      </div>
      <div className="location-fallback">
        <label htmlFor="landmark">{hindi ? "या स्थलचिह्न लिखें" : "Or type a landmark or area"}</label>
        <div>
          <input
            id="landmark"
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder={hindi ? "स्थलचिह्न या क्षेत्र" : "Landmark or area"}
            disabled={busy}
          />
          <button
            type="button"
            onClick={() => text.trim() && onResolveText(text.trim())}
            disabled={busy || !text.trim()}
          >
            {hindi ? "स्थलचिह्न उपयोग करें" : "Use landmark"}
          </button>
        </div>
      </div>
    </div>
  );
}
