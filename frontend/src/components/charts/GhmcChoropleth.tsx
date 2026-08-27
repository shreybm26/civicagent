import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

type WardProps = {
  name?: string;
  ward_id?: string;
  ward_name?: string;
  total?: number;
  pending?: number;
  in_progress?: number;
  completed?: number;
  open_ratio?: number;
};

export type WardGeoJson = GeoJSON.FeatureCollection<GeoJSON.Geometry, WardProps>;

const CHART_SCALES = ["#138808", "#c9a227", "#ff9933", "#c45c00", "#922d2d"];
const NO_DATA_FILL = "#d8e0ea";

function colorForOpenRatio(ratio: number, total: number): string {
  if (total <= 0) return NO_DATA_FILL;
  if (ratio <= 0) return CHART_SCALES[0];
  if (ratio < 0.25) return CHART_SCALES[1];
  if (ratio < 0.45) return CHART_SCALES[2];
  if (ratio < 0.65) return CHART_SCALES[3];
  return CHART_SCALES[4];
}

function wardLabel(props: WardProps): string {
  if (props.ward_id && props.ward_name) return `Ward ${props.ward_id} — ${props.ward_name}`;
  if (typeof props.name === "string") return props.name;
  return "Ward";
}

function wardTooltip(props: WardProps): string {
  const open = (props.pending ?? 0) + (props.in_progress ?? 0);
  const total = props.total ?? 0;
  const cleared = total ? Math.round(((props.completed ?? 0) / total) * 100) : 0;
  if (total <= 0) return `${wardLabel(props)} · no reports in this demo`;
  return `${wardLabel(props)} · ${open} open · ${props.completed ?? 0} resolved · ${cleared}% cleared`;
}

function frameWardLayer(map: L.Map, layer: L.GeoJSON) {
  const bounds = layer.getBounds();
  if (!bounds.isValid()) return;
  map.fitBounds(bounds, { padding: [16, 16], animate: false });
  const fittedZoom = map.getZoom();
  map.setMinZoom(fittedZoom);
  map.setMaxZoom(fittedZoom + 2);
  map.setMaxBounds(bounds.pad(0.005));
  map.options.maxBoundsViscosity = 1;
}

export function GhmcChoropleth({
  data,
  hindi = false,
}: {
  data: WardGeoJson | null;
  hindi?: boolean;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const layerRef = useRef<L.GeoJSON | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: [17.385, 78.4867],
      zoom: 11,
      scrollWheelZoom: true,
      zoomControl: true,
      attributionControl: false,
    });

    mapRef.current = map;
    const observer = new ResizeObserver(() => {
      map.invalidateSize({ animate: false });
      if (layerRef.current) frameWardLayer(map, layerRef.current);
    });
    observer.observe(containerRef.current);

    return () => {
      observer.disconnect();
      map.remove();
      mapRef.current = null;
      layerRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !data?.features?.length) return;

    if (layerRef.current) {
      layerRef.current.remove();
      layerRef.current = null;
    }

    const layer = L.geoJSON(data as GeoJSON.GeoJsonObject, {
      style(feature) {
        const props = (feature?.properties ?? {}) as WardProps;
        return {
          color: "#ffffff",
          weight: 1.25,
          opacity: 1,
          fillColor: colorForOpenRatio(props.open_ratio ?? 0, props.total ?? 0),
          fillOpacity: 0.92,
        };
      },
      onEachFeature(feature, pathLayer) {
        const props = (feature.properties ?? {}) as WardProps;
        pathLayer.bindTooltip(wardTooltip(props), { sticky: true, direction: "top" });
        pathLayer.on({
          mouseover: (event) => {
            const target = event.target;
            target.setStyle({ weight: 2.5, color: "#0b3a6e", fillOpacity: 0.98 });
            target.bringToFront();
          },
          mouseout: (event) => {
            layer.resetStyle(event.target);
          },
        });
      },
    }).addTo(map);

    layerRef.current = layer;
    frameWardLayer(map, layer);
  }, [data]);

  function resetView() {
    const map = mapRef.current;
    const layer = layerRef.current;
    if (!map || !layer) return;
    frameWardLayer(map, layer);
  }

  if (!data) {
    return (
      <div className="dashboard-hero dashboard-hero--loading">
        <p>{hindi ? "नक्शा लोड हो रहा है…" : "Loading ward map…"}</p>
      </div>
    );
  }

  return (
    <div className="dashboard-hero dashboard-hero--outline">
      <div className="dashboard-map-toolbar">
        <span>
          {hindi
            ? "केवल GHMC वार्ड सीमाएँ — कोई बाहरी नक्शा नहीं"
            : "GHMC ward boundaries only — no surrounding map"}
        </span>
        <button type="button" onClick={resetView}>
          {hindi ? "रीसेट" : "Reset view"}
        </button>
      </div>
      <div
        ref={containerRef}
        className="dashboard-hero-map"
        role="img"
        aria-label={hindi ? "हैदराबाद वार्ड नक्शा" : "Hyderabad ward map"}
      />
      <div className="dashboard-legend" aria-hidden="true">
        <span>{hindi ? "कोई रिपोर्ट नहीं" : "No reports"}</span>
        <i className="dashboard-legend-swatch" style={{ background: NO_DATA_FILL }} />
        <span>{hindi ? "कम खुले" : "Low open"}</span>
        <div className="dashboard-legend-bar">
          {CHART_SCALES.map((color) => (
            <i key={color} style={{ background: color }} />
          ))}
        </div>
        <span>{hindi ? "अधिक खुले" : "High open"}</span>
      </div>
    </div>
  );
}
