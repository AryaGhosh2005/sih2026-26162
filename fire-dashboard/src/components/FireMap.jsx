import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  MapContainer,
  TileLayer,
  LayersControl,
  CircleMarker,
  Marker,
  Popup,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet.heat";
import { Maximize2 } from "lucide-react";
import { MAP_CLASS_COLORS, CLASS_NAMES, riskColor } from "../constants";
import { explainEvent } from "../utils";

const { BaseLayer, Overlay } = LayersControl;

function thermalIcon(color) {
  return L.divIcon({
    className: "",
    html: `
      <div class="thermal-marker" style="--marker-color:${color};">
        <div class="thermal-pulse"></div>
        <div class="thermal-core"></div>
      </div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  });
}

/** Adds/removes a leaflet.heat layer as `visible` toggles — not shown by
 * default, matching map_visualization.py's FeatureGroup(show=False). */
function HeatLayer({ points, visible }) {
  const map = useMap();
  const layerRef = useRef(null);

  useEffect(() => {
    if (!visible || !points.length) return undefined;
    const layer = L.heatLayer(points, { minOpacity: 0.25, radius: 25, blur: 18, maxZoom: 8 });
    layerRef.current = layer;
    layer.addTo(map);
    return () => map.removeLayer(layer);
  }, [visible, points, map]);

  return null;
}

function FullscreenButton() {
  const map = useMap();
  const toggle = () => {
    const el = map.getContainer();
    if (!document.fullscreenElement) el.requestFullscreen?.();
    else document.exitFullscreen?.();
  };
  return (
    <button
      onClick={toggle}
      title="Fullscreen"
      className="absolute top-[10px] right-[50px] z-[1000] w-[30px] h-[30px] flex items-center justify-center bg-[#0d141f] border border-[#283446] text-[#dce4ee] rounded"
    >
      <Maximize2 size={14} />
    </button>
  );
}

function HeatToggleButton({ visible, setVisible }) {
  return (
    <button
      onClick={() => setVisible((v) => !v)}
      title="Toggle thermal intensity heatmap"
      className={`absolute top-[10px] right-[90px] z-[1000] px-2 h-[30px] flex items-center gap-1.5 text-[10px] font-semibold rounded border transition-colors ${
        visible
          ? "bg-[#ff6b00]/20 border-[#ff6b00] text-white"
          : "bg-[#0d141f] border-[#283446] text-[#dce4ee]"
      }`}
    >
      🌡 Heatmap
    </button>
  );
}

function Legend() {
  const items = [
    ["#FF0000", "Industrial Fire"],
    ["#FF8C00", "Wildfire"],
    ["#00CC00", "Thermal Source"],
    ["#0066CC", "Unknown"],
  ];
  return (
    <div className="absolute bottom-[15px] right-[15px] z-[1000] bg-[rgba(10,10,18,0.88)] backdrop-blur-md text-white px-4 py-3 rounded-[10px] border border-white/15 shadow-lg text-[11px] min-w-[150px]">
      <div className="font-bold text-xs mb-2">THERMAL CLASSIFICATION</div>
      {items.map(([color, label]) => (
        <div key={label} className="flex items-center gap-1.5 my-1">
          <span className="inline-block w-[9px] h-[9px] rounded-full" style={{ background: color }} />
          {label}
        </div>
      ))}
    </div>
  );
}

function PopupContent({ event }) {
  const classification = event.classification || "UNKNOWN";
  const label = CLASS_NAMES[classification] || "Unknown";
  const color = MAP_CLASS_COLORS[classification] || MAP_CLASS_COLORS.UNKNOWN;
  const score = Math.round(Number(event.risk_score) || 0);
  const level = String(event.risk_level || "LOW").toUpperCase();
  const levelColor = riskColor(level);
  const breakdown = explainEvent(event);

  return (
    <div
      style={{
        width: 260,
        background: "rgba(8,13,24,0.97)",
        border: `1px solid ${color}55`,
        borderRadius: 14,
        padding: 14,
        fontFamily: "Segoe UI, sans-serif",
        color: "#e8edf5",
      }}
    >
      <div style={{ fontSize: 10, color: "#8490a2", letterSpacing: 1, fontWeight: 700 }}>
        {label.toUpperCase()}
      </div>
      <div style={{ fontSize: 13, fontWeight: 800, color: levelColor, marginTop: 2 }}>
        {level} &middot; {score}/100
      </div>

      <div style={{ marginTop: 8, fontSize: 10.5, color: "#aeb8c7", lineHeight: 1.7 }}>
        <div>Confidence: {event.confidence ?? "N/A"}%</div>
        <div>Brightness: {event.brightness ?? "N/A"} K</div>
        <div>Distance to facility: {event.distance_to_industry ?? "N/A"} km</div>
        <div>Satellite: {event.satellite ?? "N/A"}</div>
      </div>

      <div style={{ height: 1, background: "#1b2635", margin: "9px 0" }} />

      {breakdown.map((row) => (
        <div key={row.label} style={{ marginBottom: 6 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 9.5, color: "#b8c3d2" }}>
            <span>{row.label}</span>
            <span style={{ color: "#35cf66" }}>{row.value}%</span>
          </div>
          <div style={{ height: 4, background: "#182433", borderRadius: 5 }}>
            <div style={{ width: `${row.value}%`, height: 4, background: "#35cf66", borderRadius: 5 }} />
          </div>
        </div>
      ))}
    </div>
  );
}

/** Programmatically picks the nearest fire to a map click, mirroring
 * app.py's map_result["last_object_clicked"] -> nearest-row lookup. */
function ClickHandler({ fires, onSelect }) {
  const map = useMap();
  useEffect(() => {
    if (!fires.length) return undefined;
    const handler = (e) => {
      const { lat, lng } = e.latlng;
      let nearest = null;
      let best = Infinity;
      for (const f of fires) {
        const d = (f.latitude - lat) ** 2 + (f.longitude - lng) ** 2;
        if (d < best) {
          best = d;
          nearest = f;
        }
      }
      if (nearest) onSelect(nearest);
    };
    map.on("click", handler);
    return () => map.off("click", handler);
  }, [fires, map, onSelect]);
  return null;
}

export default function FireMap({ fires, industries, onSelectEvent }) {
  const [heatVisible, setHeatVisible] = useState(false);

  const center = useMemo(() => {
    if (fires.length) {
      const lat = fires.reduce((s, f) => s + Number(f.latitude || 0), 0) / fires.length;
      const lon = fires.reduce((s, f) => s + Number(f.longitude || 0), 0) / fires.length;
      return [lat, lon];
    }
    return [20.5937, 78.9629];
  }, [fires]);

  const heatPoints = useMemo(
    () =>
      fires.map((f) => {
        const b = Number(f.brightness);
        const intensity = Number.isFinite(b) ? Math.max(0.2, Math.min(1.0, (b - 280) / 100)) : 0.5;
        return [Number(f.latitude), Number(f.longitude), intensity];
      }),
    [fires]
  );

  return (
    <div className="relative h-[540px] rounded-lg overflow-hidden border border-[#1b2635]">
      <MapContainer center={center} zoom={5} scrollWheelZoom style={{ height: "100%", width: "100%" }}>
        <LayersControl position="topright">
          <BaseLayer checked name="Satellite">
            <TileLayer
              attribution="Esri"
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            />
          </BaseLayer>
          <BaseLayer name="Street Map">
            <TileLayer
              attribution='&copy; OpenStreetMap contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
          </BaseLayer>

          <Overlay checked name="Industrial Facilities">
            <>
              {industries.map((ind, i) => (
                <CircleMarker
                  key={ind.id ?? i}
                  center={[Number(ind.latitude), Number(ind.longitude)]}
                  radius={4}
                  pathOptions={{ color: "#FFFFFF", weight: 1, fillColor: "#444444", fillOpacity: 0.75 }}
                >
                  <Popup maxWidth={240}>
                    <div style={{ fontFamily: "Segoe UI, sans-serif", minWidth: 190 }}>
                      <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 6 }}>
                        INDUSTRIAL FACILITY
                      </div>
                      <div style={{ fontSize: 11 }}>
                        <b>Name:</b> {ind.name ?? "Facility"}
                        <br />
                        <b>Type:</b> {ind.type ?? "Industrial Facility"}
                      </div>
                    </div>
                  </Popup>
                </CircleMarker>
              ))}
            </>
          </Overlay>

          <Overlay checked name="Thermal Anomalies">
            <>
              {fires.map((f, i) => {
                const color = MAP_CLASS_COLORS[f.classification] || MAP_CLASS_COLORS.UNKNOWN;
                return (
                  <Marker
                    key={f.id ?? i}
                    position={[Number(f.latitude), Number(f.longitude)]}
                    icon={thermalIcon(color)}
                    eventHandlers={{ click: () => onSelectEvent(f) }}
                  >
                    <Popup maxWidth={300}>
                      <PopupContent event={f} />
                    </Popup>
                  </Marker>
                );
              })}
            </>
          </Overlay>

        </LayersControl>

        <HeatLayer points={heatPoints} visible={heatVisible} />
        <ClickHandler fires={fires} onSelect={onSelectEvent} />
        <FullscreenButton />
      </MapContainer>
      <HeatToggleButton visible={heatVisible} setVisible={setHeatVisible} />
      <Legend />
    </div>
  );
}
