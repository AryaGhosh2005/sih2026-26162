import { CLASS_NAMES } from "./constants";

const API_BASE =
  import.meta.env.VITE_FIRE_API_BASE || "http://127.0.0.1:8000";

export const FIRES_ENDPOINT = `${API_BASE}/api/v1/fires`;
export const INDUSTRIES_ENDPOINT = `${API_BASE}/api/v1/industries`;

async function fetchJson(url, label) {
  let res;

  try {
    // Do not use AbortSignal.timeout here.
    // The backend is local and already responds quickly.
    res = await fetch(url);
  } catch (err) {
    throw new Error(
      `Could not reach ${label} endpoint (${url}): ${err.message}`
    );
  }

  if (!res.ok) {
    throw new Error(
      `Could not reach ${label} endpoint (${url}): HTTP ${res.status}`
    );
  }

  let payload;

  try {
    payload = await res.json();
  } catch (err) {
    throw new Error(
      `Invalid JSON returned by ${label} endpoint (${url}): ${err.message}`
    );
  }

  // FastAPI can return a direct array or a wrapped response.
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.fires)) return payload.fires;
  if (Array.isArray(payload?.industries)) return payload.industries;

  return [];
}

export async function loadData() {
  /*
   * Load the two endpoints sequentially instead of using Promise.all().
   * This avoids overlapping requests while the local FastAPI backend
   * is reading the CSV data.
   */
  const firesRaw = await fetchJson(FIRES_ENDPOINT, "fires");
  const industries = await fetchJson(
    INDUSTRIES_ENDPOINT,
    "industries"
  );

  const fires = firesRaw.map((row) => {
    const r = { ...row };

    r.acquisition_date = r.acquisition_date
      ? new Date(r.acquisition_date)
      : null;

    if (!r.classification) {
      r.classification = "UNKNOWN";
    }

    if (!r.classification_label) {
      r.classification_label =
        CLASS_NAMES[r.classification] || "Unknown";
    }

    if (
      r.distance_to_industry === undefined ||
      r.distance_to_industry === null
    ) {
      r.distance_to_industry = 999;
    }

    if (r.confidence === undefined || r.confidence === null) {
      r.confidence = 0;
    }

    if (r.brightness === undefined || r.brightness === null) {
      r.brightness = 0;
    }

    if (!r.satellite) {
      r.satellite = "Unknown";
    }

    return r;
  });

  // The backend must provide these values.
  const missing = [];

  if (
    fires.length &&
    fires[0].risk_score === undefined
  ) {
    missing.push("risk_score");
  }

  if (
    fires.length &&
    fires[0].risk_level === undefined
  ) {
    missing.push("risk_level");
  }

  if (missing.length) {
    throw new Error(
      `Fires endpoint response is missing ${JSON.stringify(
        missing
      )}. risk_score/risk_level must come from the backend.`
    );
  }

  return {
    fires,
    industries,
  };
}