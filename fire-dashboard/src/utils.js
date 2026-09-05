import { RISK_OPTIONS } from "./constants";

export function toDateOnly(d) {
  if (!d) return null;
  const dt = d instanceof Date ? d : new Date(d);
  if (isNaN(dt)) return null;
  return dt.toISOString().slice(0, 10); // YYYY-MM-DD, calendar-date compare
}

export function isSameOrAfter(dateOnly, startOnly) {
  return dateOnly >= startOnly;
}

/** Count rows whose acquisition_date falls on today's calendar date. */
export function countToday(rows) {
  const today = toDateOnly(new Date());
  return rows.filter((r) => toDateOnly(r.acquisition_date) === today).length;
}

const riskLabelToKey = Object.fromEntries(RISK_OPTIONS.map((o) => [o.label, o.key]));
export { riskLabelToKey };

/** Applies every sidebar filter, mirroring app.py's FILTER DATA block. */
export function applyFilters(fires, filters) {
  const {
    startDate,
    endDate,
    selectedRiskKeys,
    selectedSources,
    selectedSatellites,
    minConfidence,
    minBrightness,
    maxDistance,
  } = filters;

  if (!selectedSources.length || !selectedRiskKeys.length) return [];

  return fires.filter((r) => {
    const day = toDateOnly(r.acquisition_date);
    if (!day || day < startDate || day > endDate) return false;
    if (!selectedSources.includes(r.classification_label)) return false;
    if (selectedSatellites.length && !selectedSatellites.includes(String(r.satellite))) {
      return false;
    }
    if (Number(r.confidence) < minConfidence) return false;
    if (Number(r.brightness) < minBrightness) return false;
    if (Number(r.distance_to_industry) > maxDistance) return false;
    if (!selectedRiskKeys.includes(r.risk_level)) return false;
    return true;
  });
}

/** Illustrative breakdown for the Event Intelligence / map-popup panels
 * only — NOT a second risk score. It never feeds risk_level/risk_score
 * anywhere, matching the note in app.py. */
export function explainEvent(event) {
  const confidence = Number(event.confidence) || 0;
  const distance = event.distance_to_industry !== undefined && event.distance_to_industry !== null
    ? Number(event.distance_to_industry)
    : 999;
  const brightness = Number(event.brightness) || 280;

  let proximity;
  if (distance <= 2) proximity = 96;
  else if (distance <= 5) proximity = 80;
  else if (distance <= 8) proximity = 60;
  else if (distance <= 15) proximity = 35;
  else proximity = 15;

  const thermal = Math.round(Math.max(0, Math.min(100, ((brightness - 280) / 100) * 100)));
  const persistence = event.classification === "THERMAL_SOURCE" ? 88 : 45;

  return [
    { label: "Industrial Proximity", value: proximity },
    { label: "Thermal Intensity", value: thermal },
    { label: "Persistence", value: persistence },
    { label: "Detection Confidence", value: Math.round(confidence) },
    { label: "Land-cover Context", value: 94 },
  ].map((row) => ({ ...row, value: Math.max(0, Math.min(100, row.value)) }));
}

function csvEscape(value) {
  if (value === null || value === undefined) return "";
  const s = String(value);
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

export function toCsv(rows) {
  if (!rows.length) return "";
  const columns = Object.keys(rows[0]);
  const lines = [columns.join(",")];
  for (const row of rows) {
    lines.push(columns.map((c) => csvEscape(row[c])).join(","));
  }
  return lines.join("\n");
}

export function toGeoJson(rows) {
  const features = [];
  for (const row of rows) {
    const lat = Number(row.latitude);
    const lon = Number(row.longitude);
    if (Number.isNaN(lat) || Number.isNaN(lon)) continue;

    const properties = {};
    for (const [k, v] of Object.entries(row)) {
      properties[k] = v instanceof Date ? v.toISOString() : v;
    }

    features.push({
      type: "Feature",
      properties,
      geometry: { type: "Point", coordinates: [lon, lat] },
    });
  }
  return { type: "FeatureCollection", features };
}

export function downloadFile(content, filename, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
