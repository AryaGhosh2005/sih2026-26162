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
import { Maximize2, MapPin, Satellite, Flame, Activity } from "lucide-react";
import {
  MAP_CLASS_COLORS,
  CLASS_NAMES,
  riskColor,
} from "../constants";
import { explainEvent } from "../utils";

const { BaseLayer, Overlay } = LayersControl;

/* =========================================================
   THERMAL MARKER
   ========================================================= */

function thermalIcon(color) {
  return L.divIcon({
    className: "",
    html: `
      <div class="thermal-marker" style="--marker-color:${color};">
        <div class="thermal-pulse"></div>
        <div class="thermal-core"></div>
      </div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  });
}

/* =========================================================
   HEATMAP LAYER
   ========================================================= */

function HeatLayer({ points, visible }) {
  const map = useMap();
  const layerRef = useRef(null);

  useEffect(() => {
    if (!visible || !points.length) return undefined;

    const layer = L.heatLayer(points, {
      minOpacity: 0.25,
      radius: 25,
      blur: 18,
      maxZoom: 8,
    });

    layerRef.current = layer;
    layer.addTo(map);

    return () => {
      map.removeLayer(layer);
    };
  }, [visible, points, map]);

  return null;
}

/* =========================================================
   FULLSCREEN BUTTON
   ========================================================= */

function FullscreenButton() {
  const map = useMap();

  const toggle = () => {
    const el = map.getContainer();

    if (!document.fullscreenElement) {
      el.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
  };

  return (
    <button
      onClick={toggle}
      title="Fullscreen"
      className="
        absolute top-[10px] right-[50px] z-[1000]
        w-[30px] h-[30px]
        flex items-center justify-center
        bg-[#07111d]/90
        border border-cyan-400/30
        text-[#dce4ee]
        rounded-md
        backdrop-blur-md
        hover:bg-cyan-400/10
        hover:border-cyan-400/60
        transition-all
      "
    >
      <Maximize2 size={14} />
    </button>
  );
}

/* =========================================================
   HEATMAP BUTTON
   ========================================================= */

function HeatToggleButton({ visible, setVisible }) {
  return (
    <button
      onClick={() => setVisible((v) => !v)}
      title="Toggle thermal intensity heatmap"
      className={`
        absolute top-[10px] right-[90px] z-[1000]
        px-2 h-[30px]
        flex items-center gap-1.5
        text-[10px] font-semibold
        rounded-md
        border
        backdrop-blur-md
        transition-all
        ${
          visible
            ? "bg-orange-500/20 border-orange-400 text-white shadow-[0_0_15px_rgba(255,140,0,0.25)]"
            : "bg-[#07111d]/90 border-cyan-400/20 text-[#dce4ee] hover:border-cyan-400/50"
        }
      `}
    >
      🌡 Heatmap
    </button>
  );
}

/* =========================================================
   MAP LEGEND
   ========================================================= */

function Legend() {
  const items = [
    ["#FF0000", "Industrial Fire"],
    ["#FF8C00", "Wildfire"],
    ["#00CC00", "Thermal Source"],
    ["#0066CC", "Unknown"],
  ];

  return (
    <div
      className="
        absolute bottom-[15px] right-[15px] z-[1000]
        bg-[rgba(5,11,19,0.90)]
        backdrop-blur-xl
        text-white
        px-4 py-3
        rounded-xl
        border border-cyan-400/20
        shadow-[0_0_25px_rgba(0,180,255,0.08)]
        text-[11px]
        min-w-[165px]
      "
    >
      <div className="font-bold text-xs mb-2 tracking-wide">
        THERMAL CLASSIFICATION
      </div>

      {items.map(([color, label]) => (
        <div
          key={label}
          className="flex items-center gap-2 my-1.5 text-slate-300"
        >
          <span
            className="inline-block w-[9px] h-[9px] rounded-full shadow-sm"
            style={{
              background: color,
              boxShadow: `0 0 7px ${color}`,
            }}
          />

          {label}
        </div>
      ))}
    </div>
  );
}

/* =========================================================
   EVENT POPUP
   ========================================================= */

function PopupContent({ event }) {
  const classification = event.classification || "UNKNOWN";

  const label =
    CLASS_NAMES[classification] || "Unknown";

  const color =
    MAP_CLASS_COLORS[classification] ||
    MAP_CLASS_COLORS.UNKNOWN;

  const score = Math.round(
    Number(event.risk_score) || 0
  );

  const level = String(
    event.risk_level || "LOW"
  ).toUpperCase();

  const levelColor = riskColor(level);

  const breakdown = explainEvent(event);

  /* Coordinates */
  const latitude = Number(event.latitude);
  const longitude = Number(event.longitude);

  const formattedLatitude = Number.isFinite(latitude)
    ? latitude.toFixed(5)
    : "N/A";

  const formattedLongitude = Number.isFinite(longitude)
    ? longitude.toFixed(5)
    : "N/A";

  /* Other values */
  const confidence =
    event.confidence !== undefined &&
    event.confidence !== null
      ? event.confidence
      : "N/A";

  const brightness =
    event.brightness !== undefined &&
    event.brightness !== null
      ? event.brightness
      : "N/A";

  const distance =
    event.distance_to_industry !== undefined &&
    event.distance_to_industry !== null
      ? event.distance_to_industry
      : "N/A";

  const satellite =
    event.satellite ?? "N/A";

  return (
    <div
      style={{
        width: "300px",
        background:
          "linear-gradient(145deg, rgba(7,16,27,0.98), rgba(3,9,17,0.98))",
        border: `1px solid ${color}66`,
        borderRadius: "16px",
        padding: "0",
        fontFamily: "Segoe UI, sans-serif",
        color: "#e8edf5",
        overflow: "hidden",
        boxShadow: `
          0 0 0 1px rgba(0,200,255,0.04),
          0 15px 45px rgba(0,0,0,0.55),
          0 0 25px ${color}18
        `,
      }}
    >

      {/* =====================================================
          TOP ACCENT
         ===================================================== */}

      <div
        style={{
          height: "3px",
          background: `linear-gradient(90deg, ${color}, ${color}55, transparent)`,
        }}
      />

      <div style={{ padding: "15px 15px 13px" }}>

        {/* ===================================================
            HEADER
           =================================================== */}

        <div
          style={{
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            gap: "10px",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "9px",
            }}
          >
            <div
              style={{
                width: "34px",
                height: "34px",
                borderRadius: "9px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: `${color}16`,
                border: `1px solid ${color}44`,
                boxShadow: `0 0 15px ${color}15`,
              }}
            >
              <Flame
                size={17}
                color={color}
              />
            </div>

            <div>
              <div
                style={{
                  fontSize: "9px",
                  color: "#8490a2",
                  letterSpacing: "1.5px",
                  fontWeight: 700,
                  marginBottom: "3px",
                }}
              >
                THERMAL EVENT
              </div>

              <div
                style={{
                  fontSize: "14px",
                  fontWeight: 900,
                  color: "#f5f7fa",
                  letterSpacing: "0.3px",
                }}
              >
                {label.toUpperCase()}
              </div>
            </div>
          </div>

          {/* Risk badge */}
          <div
            style={{
              padding: "4px 8px",
              borderRadius: "5px",
              fontSize: "9px",
              fontWeight: 800,
              letterSpacing: "0.7px",
              color: levelColor,
              background: `${levelColor}14`,
              border: `1px solid ${levelColor}55`,
            }}
          >
            {level}
          </div>
        </div>

        {/* ===================================================
            RISK SCORE
           =================================================== */}

        <div
          style={{
            marginTop: "14px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div>
            <div
              style={{
                fontSize: "9px",
                color: "#718096",
                textTransform: "uppercase",
                letterSpacing: "1px",
              }}
            >
              Risk Score
            </div>

            <div
              style={{
                fontSize: "25px",
                lineHeight: "28px",
                fontWeight: 900,
                color: levelColor,
                marginTop: "2px",
              }}
            >
              {score}
              <span
                style={{
                  fontSize: "11px",
                  color: "#687588",
                  fontWeight: 600,
                }}
              >
                /100
              </span>
            </div>
          </div>

          <div
            style={{
              width: "105px",
              height: "6px",
              borderRadius: "10px",
              background: "#162333",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${Math.min(score, 100)}%`,
                height: "100%",
                borderRadius: "10px",
                background: levelColor,
                boxShadow: `0 0 10px ${levelColor}`,
              }}
            />
          </div>
        </div>

        {/* ===================================================
            EVENT DETAILS
           =================================================== */}

        <div
          style={{
            marginTop: "13px",
            padding: "10px 11px",
            background: "rgba(10,20,32,0.65)",
            border: "1px solid rgba(100,140,180,0.12)",
            borderRadius: "9px",
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              columnGap: "15px",
              rowGap: "9px",
            }}
          >
            <DetailItem
              label="Confidence"
              value={`${confidence}%`}
            />

            <DetailItem
              label="Brightness"
              value={`${brightness} K`}
            />

            <DetailItem
              label="Distance"
              value={`${distance} km`}
            />

            <DetailItem
              label="Satellite"
              value={satellite}
            />
          </div>
        </div>

        {/* ===================================================
            COORDINATES
           =================================================== */}

        <div
          style={{
            marginTop: "9px",
            padding: "10px 11px",
            borderRadius: "9px",
            background:
              "linear-gradient(90deg, rgba(0,190,255,0.08), rgba(0,190,255,0.025))",
            border: "1px solid rgba(0,200,255,0.20)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              marginBottom: "7px",
            }}
          >
            <MapPin
              size={12}
              color="#22d3ee"
            />

            <span
              style={{
                fontSize: "9px",
                color: "#22d3ee",
                fontWeight: 800,
                letterSpacing: "1px",
              }}
            >
              DETECTION COORDINATES
            </span>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "8px",
            }}
          >
            <CoordinateItem
              label="LATITUDE"
              value={formattedLatitude}
            />

            <CoordinateItem
              label="LONGITUDE"
              value={formattedLongitude}
            />
          </div>
        </div>

        {/* ===================================================
            SIGNAL BREAKDOWN
           =================================================== */}

        <div
          style={{
            marginTop: "13px",
            paddingTop: "11px",
            borderTop: "1px solid #172333",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              marginBottom: "9px",
            }}
          >
            <Activity
              size={12}
              color="#22d3ee"
            />

            <span
              style={{
                fontSize: "9px",
                color: "#8fa0b4",
                fontWeight: 800,
                letterSpacing: "1px",
              }}
            >
              SIGNAL ANALYSIS
            </span>
          </div>

          {breakdown.map((row) => (
            <div
              key={row.label}
              style={{
                marginBottom: "8px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  fontSize: "9px",
                  color: "#aeb9c8",
                  marginBottom: "4px",
                }}
              >
                <span>{row.label}</span>

                <span
                  style={{
                    color: "#35cf66",
                    fontWeight: 700,
                  }}
                >
                  {row.value}%
                </span>
              </div>

              <div
                style={{
                  height: "4px",
                  background: "#162333",
                  borderRadius: "5px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    width: `${Math.min(
                      Math.max(row.value, 0),
                      100
                    )}%`,
                    height: "100%",
                    background:
                      "linear-gradient(90deg, #16a34a, #35cf66)",
                    borderRadius: "5px",
                    boxShadow:
                      "0 0 7px rgba(53,207,102,0.35)",
                  }}
                />
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}

/* =========================================================
   SMALL DETAIL COMPONENT
   ========================================================= */

function DetailItem({ label, value }) {
  return (
    <div>
      <div
        style={{
          fontSize: "8px",
          color: "#627187",
          textTransform: "uppercase",
          letterSpacing: "0.7px",
          marginBottom: "3px",
        }}
      >
        {label}
      </div>

      <div
        style={{
          fontSize: "10.5px",
          color: "#e1e7ef",
          fontWeight: 600,
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
      >
        {value}
      </div>
    </div>
  );
}

/* =========================================================
   COORDINATE ITEM
   ========================================================= */

function CoordinateItem({ label, value }) {
  return (
    <div>
      <div
        style={{
          fontSize: "7.5px",
          color: "#527083",
          letterSpacing: "0.8px",
          marginBottom: "3px",
        }}
      >
        {label}
      </div>

      <div
        style={{
          fontSize: "10px",
          color: "#d9f8ff",
          fontWeight: 700,
          fontFamily: "Consolas, monospace",
          letterSpacing: "0.2px",
        }}
      >
        {value}
      </div>
    </div>
  );
}

/* =========================================================
   MAP CLICK HANDLER
   ========================================================= */

function ClickHandler({ fires, onSelect }) {
  const map = useMap();

  useEffect(() => {
    if (!fires.length) return undefined;

    const handler = (e) => {
      const { lat, lng } = e.latlng;

      let nearest = null;
      let best = Infinity;

      for (const f of fires) {
        const fireLat = Number(f.latitude);
        const fireLng = Number(f.longitude);

        if (!Number.isFinite(fireLat) || !Number.isFinite(fireLng)) {
          continue;
        }

        const d =
          (fireLat - lat) ** 2 +
          (fireLng - lng) ** 2;

        if (d < best) {
          best = d;
          nearest = f;
        }
      }

      if (nearest) {
        onSelect(nearest);
      }
    };

    map.on("click", handler);

    return () => {
      map.off("click", handler);
    };
  }, [fires, map, onSelect]);

  return null;
}

/* =========================================================
   MAIN FIRE MAP
   ========================================================= */

export default function FireMap({
  fires,
  industries,
  onSelectEvent,
}) {
  const [heatVisible, setHeatVisible] =
    useState(false);

  /* =======================================================
     MAP CENTER
     ======================================================= */

  const center = useMemo(() => {
    if (fires.length) {
      const validFires = fires.filter(
        (f) =>
          Number.isFinite(Number(f.latitude)) &&
          Number.isFinite(Number(f.longitude))
      );

      if (validFires.length) {
        const lat =
          validFires.reduce(
            (s, f) =>
              s + Number(f.latitude),
            0
          ) / validFires.length;

        const lon =
          validFires.reduce(
            (s, f) =>
              s + Number(f.longitude),
            0
          ) / validFires.length;

        return [lat, lon];
      }
    }

    return [20.5937, 78.9629];
  }, [fires]);

  /* =======================================================
     HEATMAP POINTS
     ======================================================= */

  const heatPoints = useMemo(
    () =>
      fires
        .filter(
          (f) =>
            Number.isFinite(Number(f.latitude)) &&
            Number.isFinite(Number(f.longitude))
        )
        .map((f) => {
          const b = Number(f.brightness);

          const intensity = Number.isFinite(b)
            ? Math.max(
                0.2,
                Math.min(1.0, (b - 280) / 100)
              )
            : 0.5;

          return [
            Number(f.latitude),
            Number(f.longitude),
            intensity,
          ];
        }),
    [fires]
  );

  /* =======================================================
     RENDER
     ======================================================= */

  return (
    <div className="relative h-full w-full overflow-hidden">

      <MapContainer
        center={center}
        zoom={5}
        scrollWheelZoom
        style={{
          height: "100%",
          width: "100%",
        }}
      >

        {/* =================================================
            BASE MAPS
           ================================================= */}

        <LayersControl position="topright">

          <BaseLayer
            checked
            name="Satellite"
          >
            <TileLayer
              attribution="Esri"
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            />
          </BaseLayer>

          <BaseLayer name="Street Map">
            <TileLayer
              attribution="&copy; OpenStreetMap contributors"
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
          </BaseLayer>

          {/* ===============================================
              INDUSTRIAL FACILITIES
             =============================================== */}

          <Overlay
            checked
            name="Industrial Facilities"
          >
            <>
              {industries.map((ind, i) => (
                <CircleMarker
                  key={ind.id ?? i}
                  center={[
                    Number(ind.latitude),
                    Number(ind.longitude),
                  ]}
                  radius={4}
                  pathOptions={{
                    color: "#FFFFFF",
                    weight: 1,
                    fillColor: "#444444",
                    fillOpacity: 0.75,
                  }}
                >
                  <Popup maxWidth={240}>
                    <div
                      style={{
                        fontFamily:
                          "Segoe UI, sans-serif",
                        minWidth: 190,
                      }}
                    >
                      <div
                        style={{
                          fontSize: 13,
                          fontWeight: 700,
                          marginBottom: 6,
                        }}
                      >
                        INDUSTRIAL FACILITY
                      </div>

                      <div
                        style={{
                          fontSize: 11,
                        }}
                      >
                        <b>Name:</b>{" "}
                        {ind.name ?? "Facility"}

                        <br />

                        <b>Type:</b>{" "}
                        {ind.type ??
                          "Industrial Facility"}
                      </div>
                    </div>
                  </Popup>
                </CircleMarker>
              ))}
            </>
          </Overlay>

          {/* ===============================================
              THERMAL EVENTS
             =============================================== */}

          <Overlay
            checked
            name="Thermal Anomalies"
          >
            <>
              {fires.map((f, i) => {
                const color =
                  MAP_CLASS_COLORS[
                    f.classification
                  ] ||
                  MAP_CLASS_COLORS.UNKNOWN;

                return (
                  <Marker
                    key={f.id ?? i}
                    position={[
                      Number(f.latitude),
                      Number(f.longitude),
                    ]}
                    icon={thermalIcon(color)}
                    eventHandlers={{
                      click: () =>
                        onSelectEvent(f),
                    }}
                  >
                    <Popup
                      maxWidth={330}
                      className="fire-event-popup"
                      closeButton={true}
                    >
                      <PopupContent event={f} />
                    </Popup>
                  </Marker>
                );
              })}
            </>
          </Overlay>

        </LayersControl>

        {/* =================================================
            HEATMAP
           ================================================= */}

        <HeatLayer
          points={heatPoints}
          visible={heatVisible}
        />

        {/* =================================================
            MAP CLICK
           ================================================= */}

        <ClickHandler
          fires={fires}
          onSelect={onSelectEvent}
        />

        {/* =================================================
            FULLSCREEN
           ================================================= */}

        <FullscreenButton />

      </MapContainer>

      {/* ===================================================
          MAP FLOATING CONTROLS
         =================================================== */}

      <HeatToggleButton
        visible={heatVisible}
        setVisible={setHeatVisible}
      />

      <Legend />

    </div>
  );
}