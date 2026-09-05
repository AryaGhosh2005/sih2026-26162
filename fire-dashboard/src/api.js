import { CLASS_NAMES } from "./constants";

// Ported from app.py's API_BASE / FIRES_ENDPOINT / INDUSTRIES_ENDPOINT.
// Override via a .env file (see .env.example) — Vite exposes it as
// import.meta.env.VITE_FIRE_API_BASE.
const API_BASE = import.meta.env.VITE_FIRE_API_BASE || "http://localhost:8000";
export const FIRES_ENDPOINT = `${API_BASE}/api/fires`;
export const INDUSTRIES_ENDPOINT = `${API_BASE}/api/industries`;

async function fetchJson(url, label) {
  let res;
  try {
    res = await fetch(url, { signal: AbortSignal.timeout(60000) });
  } catch (err) {
    throw new Error(`Could not reach ${label} endpoint (${url}): ${err.message}`);
  }
  if (!res.ok) {
    throw new Error(`Could not reach ${label} endpoint (${url}): HTTP ${res.status}`);
  }
  const payload = await res.json();
  // Support the response formats returned by the FastAPI backend:
  // {"fires": [...]} and {"industries": [...]}
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.fires)) return payload.fires;
  if (Array.isArray(payload?.industries)) return payload.industries;

  return [];
}

/**
 * Pulls fire + industry records from the FastAPI backend. risk_score and
 * risk_level are expected to arrive already computed by risk_engine.py on
 * the backend — this function must not touch or recompute them, mirroring
 * load_data() in app.py.
 */
export async function loadData() {
  const [firesRaw, industries] = await Promise.all([
    fetchJson(FIRES_ENDPOINT, "fires"),
    fetchJson(INDUSTRIES_ENDPOINT, "industries"),
  ]);

  const fires = firesRaw.map((row) => {
    const r = { ...row };

    r.acquisition_date = r.acquisition_date ? new Date(r.acquisition_date) : null;
    if (!r.classification) r.classification = "UNKNOWN";
    if (!r.classification_label) {
      r.classification_label = CLASS_NAMES[r.classification] || "Unknown";
    }
    if (r.distance_to_industry === undefined || r.distance_to_industry === null) {
      r.distance_to_industry = 999;
    }
    if (r.confidence === undefined || r.confidence === null) r.confidence = 0;
    if (r.brightness === undefined || r.brightness === null) r.brightness = 0;
    if (!r.satellite) r.satellite = "Unknown";

    return r;
  });

  // risk_score / risk_level must already be present from the API — surface
  // the problem instead of silently fabricating them (see app.py's note).
  const missing = [];
  if (fires.length && fires[0].risk_score === undefined) missing.push("risk_score");
  if (fires.length && fires[0].risk_level === undefined) missing.push("risk_level");
  if (missing.length) {
    throw new Error(
      `Fires endpoint response is missing ${JSON.stringify(missing)}. ` +
        "risk_score/risk_level must come from the backend (risk_engine.py) — " +
        "check the /api/fires response shape."
    );
  }

  return { fires, industries };
}
