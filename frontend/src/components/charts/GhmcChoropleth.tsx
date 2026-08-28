import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { PublicTicketPin, TicketStatus } from "../../lib/types";

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

type WardPathLayer = L.Path & {
  feature?: GeoJSON.Feature<GeoJSON.Geometry, WardProps>;
  getBounds(): L.LatLngBounds;
};

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

function pinIcon(status: TicketStatus): L.DivIcon {
  return L.divIcon({
    className: "",
    html: `<span class="dashboard-ticket-pin dashboard-ticket-pin--${status}" aria-hidden="true"></span>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });
}

function pinPopup(pin: PublicTicketPin): string {
  const status =
    pin.status === "pending" ? "Pending" : pin.status === "in_progress" ? "In progress" : "Completed";
  return `<strong>${pin.ref_masked}</strong><br>${pin.service_label}<br>Ward ${pin.ward_id} — ${pin.ward_name}<br>${status}`;
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
  const baseZoom = fittedZoom + 0.05;
  baseZoomRef.current = baseZoom;
  map.setView(bounds.getCenter(), baseZoom, { animate: false });
  map.setMinZoom(baseZoom);
  map.setMaxZoom(baseZoom + 3);
  map.options.maxBoundsViscosity = 0.85;
  updatePanBounds(map, bounds, baseZoom, baseZoom);
}

function styleForWard(props: WardProps, selectedWardId: string | null): L.PathOptions {
  const wardId = props.ward_id ?? "";
  const isSelected = Boolean(selectedWardId && wardId === selectedWardId);
  const isDimmed = Boolean(selectedWardId && wardId !== selectedWardId);
  return {
    color: isSelected ? "#0b3a6e" : "#ffffff",
    weight: isSelected ? 3 : 1.25,
    opacity: 1,
    fillColor: colorForOpenRatio(props.open_ratio ?? 0, props.total ?? 0),
    fillOpacity: isDimmed ? 0.28 : isSelected ? 1 : 0.92,
  };
}

export function GhmcChoropleth({
  data,
  pins = [],
  hindi = false,
  selectedWardId = null,
  onWardSelect,
}: {
  data: WardGeoJson | null;
  pins?: PublicTicketPin[];
  hindi?: boolean;
  selectedWardId?: string | null;
  onWardSelect?: (ward: { wardId: string; wardName: string } | null) => void;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const layerRef = useRef<L.GeoJSON | null>(null);
  const markersRef = useRef<L.LayerGroup | null>(null);
  const tilesRef = useRef<L.TileLayer | null>(null);
  const pathsRef = useRef<Map<string, WardPathLayer>>(new Map());
  const baseZoomRef = useRef(11);
  const boundsRef = useRef<L.LatLngBounds | null>(null);
  const onWardSelectRef = useRef(onWardSelect);
  const selectedWardIdRef = useRef(selectedWardId);

  useEffect(() => {
    onWardSelectRef.current = onWardSelect;
  }, [onWardSelect]);

  useEffect(() => {
    selectedWardIdRef.current = selectedWardId;
  }, [selectedWardId]);

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

    const syncDetailMode = () => {
      const detail = map.getZoom() > baseZoomRef.current + 0.35;
      tilesRef.current?.setOpacity(detail ? 0.92 : 0);
      pathsRef.current.forEach((path) => {
        const props = (path.feature?.properties ?? {}) as WardProps;
        const styled = styleForWard(props, selectedWardIdRef.current);
        path.setStyle({
          ...styled,
          fillOpacity: detail ? Math.min(styled.fillOpacity ?? 0.92, 0.22) : styled.fillOpacity,
        });
      });
    };

    const onZoomEnd = () => {
      if (map.getZoom() < baseZoomRef.current) {
        map.setZoom(baseZoomRef.current);
        return;
      }
      if (boundsRef.current) {
        updatePanBounds(map, boundsRef.current, baseZoomRef.current, map.getZoom());
      }
      syncDetailMode();
    };

    containerRef.current.addEventListener("wheel", onWheel, { passive: false });
    map.on("zoomend", onZoomEnd);

    mapRef.current = map;
    markersRef.current = L.layerGroup().addTo(map);
    tilesRef.current = L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
      attribution: "&copy; OpenStreetMap &copy; CARTO",
      maxZoom: 19,
      opacity: 0,
    }).addTo(map);

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
      markersRef.current = null;
      tilesRef.current = null;
      pathsRef.current.clear();
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
    pathsRef.current.clear();

    const layer = L.geoJSON(data as GeoJSON.GeoJsonObject, {
      style(feature) {
        const props = (feature?.properties ?? {}) as WardProps;
        return styleForWard(props, selectedWardIdRef.current);
      },
      onEachFeature(feature, pathLayer) {
        const props = (feature.properties ?? {}) as WardProps;
        const wardId = props.ward_id;
        const layer = pathLayer as WardPathLayer;
        layer.feature = feature as GeoJSON.Feature<GeoJSON.Geometry, WardProps>;
        if (wardId) pathsRef.current.set(wardId, layer);
        layer.bindTooltip(wardTooltip(props), { sticky: true, direction: "top" });
        layer.on({
          mouseover: (event) => {
            const target = event.target as WardPathLayer;
            const hoverProps = (target.feature?.properties ?? {}) as WardProps;
            target.setStyle({
              ...styleForWard(hoverProps, selectedWardIdRef.current),
              weight: 2.5,
              fillOpacity: 0.98,
            });
            target.bringToFront();
          },
          mouseout: (event) => {
            const target = event.target as WardPathLayer;
            const hoverProps = (target.feature?.properties ?? {}) as WardProps;
            target.setStyle(styleForWard(hoverProps, selectedWardIdRef.current));
          },
          click: () => {
            if (!wardId) return;
            const wardName = props.ward_name ?? wardLabel(props);
            const current = selectedWardIdRef.current;
            onWardSelectRef.current?.(
              current === wardId ? null : { wardId, wardName },
            );
          },
        });
      },
    }).addTo(map);

    layerRef.current = layer;
    frameWardLayer(map, layer, baseZoomRef, boundsRef);
  }, [data]);

  useEffect(() => {
    const group = markersRef.current;
    if (!group) return;
    group.clearLayers();
    for (const pin of pins) {
      L.marker([pin.lat, pin.lng], { icon: pinIcon(pin.status) })
        .bindPopup(pinPopup(pin))
        .addTo(group);
    }
  }, [pins]);

  useEffect(() => {
    pathsRef.current.forEach((path) => {
      const props = (path.feature?.properties ?? {}) as WardProps;
      path.setStyle(styleForWard(props, selectedWardId));
    });
    if (!selectedWardId) return;
    const map = mapRef.current;
    const path = pathsRef.current.get(selectedWardId);
    if (!map || !path) return;
    const bounds = path.getBounds();
    if (!bounds.isValid()) return;
    map.fitBounds(bounds, {
      padding: [28, 28],
      animate: true,
      maxZoom: Math.min(baseZoomRef.current + 2, map.getMaxZoom()),
    });
  }, [selectedWardId]);

  function resetView() {
    const map = mapRef.current;
    const layer = layerRef.current;
    if (!map || !layer) return;
    onWardSelectRef.current?.(null);
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
        {selectedWardId ? (
          <span>
            {hindi ? "वार्ड चयनित — शिकायतें फ़िल्टर हो रही हैं" : "Ward selected — tickets filtered"}
          </span>
        ) : pins.length > 0 ? (
          <span>
            {hindi
              ? `${pins.length} शिकायतें नक्शे पर — ज़ूम इन करके विवरण देखें`
              : `${pins.length} issue${pins.length === 1 ? "" : "s"} on map — zoom in for detail`}
          </span>
        ) : (
          <span>{hindi ? "वार्ड नक्शा" : "Ward map"}</span>
        )}
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
