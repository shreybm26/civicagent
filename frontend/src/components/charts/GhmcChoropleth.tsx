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

function updatePanBounds(map: L.Map, bounds: L.LatLngBounds, baseZoom: number, zoom: number) {
  const zoomInSteps = Math.max(0, zoom - baseZoom);
  const pad = 0.05 + zoomInSteps * 0.035;
  map.setMaxBounds(bounds.pad(pad));
}

function frameWardLayer(
  map: L.Map,
  layer: L.GeoJSON,
  baseZoomRef: { current: number },
  boundsRef: { current: L.LatLngBounds | null },
) {
  const bounds = layer.getBounds();
  if (!bounds.isValid()) return;
  boundsRef.current = bounds;
  map.fitBounds(bounds, { padding: [8, 8], animate: false });
  const fittedZoom = map.getZoom();
  const baseZoom = fittedZoom + 0.08;
  baseZoomRef.current = baseZoom;
  map.setView(bounds.getCenter(), baseZoom, { animate: false });
  map.setMinZoom(baseZoom);
  map.setMaxZoom(baseZoom + 3);
  map.options.maxBoundsViscosity = 0.85;
  updatePanBounds(map, bounds, baseZoom, baseZoom);
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
  const baseZoomRef = useRef(11);
  const boundsRef = useRef<L.LatLngBounds | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: [17.385, 78.4867],
      zoom: 11,
      scrollWheelZoom: false,
      zoomControl: true,
      attributionControl: false,
      zoomSnap: 0.25,
      zoomDelta: 0.25,
    });

    const onWheel = (event: WheelEvent) => {
      event.preventDefault();
      if (event.deltaY < 0 && map.getZoom() < map.getMaxZoom()) {
        map.zoomIn();
      }
    };

    const onZoomEnd = () => {
      if (map.getZoom() < baseZoomRef.current) {
        map.setZoom(baseZoomRef.current);
        return;
      }
      if (boundsRef.current) {
        updatePanBounds(map, boundsRef.current, baseZoomRef.current, map.getZoom());
      }
    };

    containerRef.current.addEventListener("wheel", onWheel, { passive: false });
    map.on("zoomend", onZoomEnd);

    mapRef.current = map;
    const observer = new ResizeObserver(() => {
      map.invalidateSize({ animate: false });
      if (layerRef.current) frameWardLayer(map, layerRef.current, baseZoomRef, boundsRef);
    });
    observer.observe(containerRef.current);

    return () => {
      containerRef.current?.removeEventListener("wheel", onWheel);
      map.off("zoomend", onZoomEnd);
      observer.disconnect();
      map.remove();
      mapRef.current = null;
      layerRef.current = null;
      boundsRef.current = null;
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
    frameWardLayer(map, layer, baseZoomRef, boundsRef);
  }, [data]);

  function resetView() {
    const map = mapRef.current;
    const layer = layerRef.current;
    if (!map || !layer) return;
    frameWardLayer(map, layer, baseZoomRef, boundsRef);
  }

  if (!data) {
    return (
      <div className="dashboard-hero dashboard-hero--loading">
        <p>{hindi ? "नक्शा लोड हो रहा है…" : "Loading ward map…"}</p>
      </div>
    );
  }

  return (
    <section className="dashboard-map-block" aria-label={hindi ? "हैदराबाद वार्ड नक्शा" : "Hyderabad ward map"}>
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
        aria-label={hindi ? "GHMC वार्ड कोरोप्लेथ" : "GHMC ward choropleth"}
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
    </section>
  );
}
