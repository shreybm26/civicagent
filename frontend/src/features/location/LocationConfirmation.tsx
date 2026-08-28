import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

type Pick = { lat: number; lng: number; label: string };

const MAP_CENTER: [number, number] = [17.385, 78.4867];
const HYDERABAD_BOUNDS = L.latLngBounds(
  [17.25, 78.2],
  [17.65, 78.65],
);

function isWithinHyderabad(lat: number, lng: number): boolean {
  return HYDERABAD_BOUNDS.contains([lat, lng]);
}

export function LocationConfirmation({
  onConfirm,
  busy,
  hindi,
}: {
  onConfirm: (pick: Pick) => void;
  onResolveText?: (text: string) => void;
  busy?: boolean;
  hindi?: boolean;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);
  const [open, setOpen] = useState(false);
  const [pick, setPick] = useState<Pick | null>(null);
  const [locating, setLocating] = useState(false);
  const [mapError, setMapError] = useState("");

  async function update(next: { lat: number; lng: number }) {
    if (!isWithinHyderabad(next.lat, next.lng)) {
      setPick(null);
      setMapError(
        hindi
          ? "यह डेमो केवल हैदराबाद (GHMC) में स्थान स्वीकार करता है।"
          : "This demo only accepts locations within Hyderabad (GHMC).",
      );
      return;
    }
    setMapError("");
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
    const map = L.map(containerRef.current, {
      center: MAP_CENTER,
      zoom: 13,
      scrollWheelZoom: true,
      maxBounds: HYDERABAD_BOUNDS.pad(0.05),
      maxBoundsViscosity: 1,
    });
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
        if (!isWithinHyderabad(next.lat, next.lng)) {
          setMapError(
            hindi
              ? "आपका वर्तमान स्थान हैदराबाद के बाहर है। मानचित्र पर पिन लगाएँ।"
              : "Your current location is outside Hyderabad. Drop a pin on the map instead.",
          );
          setLocating(false);
          return;
        }
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
        <p className="location-hint">
          {hindi
            ? "नीचे हैदराबाद का स्थान या स्थलचिह्न लिखें, या मानचित्र से चुनें।"
            : "Type a Hyderabad landmark below, or pick it on the map."}
        </p>
        <button type="button" className="primary location-open" disabled={busy} onClick={() => setOpen(true)}>
          {hindi ? "मानचित्र से चुनें" : "Pick on map"}
        </button>
      </div>
    );
  }

  return (
    <div className="chat-step location-step" aria-labelledby="location-step-title">
      <div className="step-actions location-toolbar">
        <h3 id="location-step-title">{hindi ? "मानचित्र से स्थान चुनें" : "Pick location on map"}</h3>
        <button type="button" onClick={() => setOpen(false)} disabled={busy}>
          {hindi ? "बंद करें" : "Close"}
        </button>
      </div>
      <p>
        {hindi
          ? "केवल हैदराबाद (GHMC) — मानचित्र पर टैप करें या पिन खींचें।"
          : "Hyderabad (GHMC) only — click the map or drag the pin, then confirm."}
      </p>
      <div ref={containerRef} className="location-map" aria-label="Draggable location map" />
      {mapError && (
        <p className="error" role="alert">
          {mapError}
        </p>
      )}
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
    </div>
  );
}
