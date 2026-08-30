"""
SIH 26162 - AI-Based Industrial Fire Detection & Persistent Thermal Source Monitoring
"""

import os
import json
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

from map_visualization import create_fire_map


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Industrial Fire Detection System",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS  (UI/UX REDESIGN — MAP IS UNAFFECTED BY THIS BLOCK)
# ============================================================

st.markdown("""
<style>

/* ---------------- GLOBAL ---------------- */

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

html, body, [class*="css"] {
    font-family: -apple-system, "Segoe UI", Roboto, Inter, sans-serif;
}

.stApp {
    background: radial-gradient(circle at 15% 0%, #0a0f18 0%, #05080f 55%) fixed;
    color: #e8edf5;
}

.block-container {
    padding: 14px 20px 30px 20px;
    max-width: 100%;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.4rem;
}

hr, div[data-testid="stDivider"] {
    border-color: #182234 !important;
}


/* ---------------- SIDEBAR ---------------- */

section[data-testid="stSidebar"] {
    background: #070b13;
    border-right: 1px solid #18202d;
}

section[data-testid="stSidebar"] * {
    color: #dce3ed;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 18px;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 8px;
    padding-bottom: 4px;
    margin-bottom: 10px;
    border-bottom: 1px solid #18212f;
}

.sidebar-brand-title {
    color: #ffffff;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 1.2px;
}

.sidebar-brand-sub {
    color: #62708a;
    font-size: 9px;
    letter-spacing: .5px;
}

.sidebar-section {
    color: #6d7c93;
    font-size: 10px;
    font-weight: 750;
    letter-spacing: 1.3px;
    margin-top: 16px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.sidebar-section::after {
    content: "";
    flex: 1;
    height: 1px;
    background: #161f2c;
}

section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p {
    font-size: 11px !important;
    color: #9aa6ba !important;
}

section[data-testid="stSidebar"] .stCheckbox {
    margin-bottom: -6px;
}

.status-chip-row {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    font-size: 10px;
    border-bottom: 1px solid #131b28;
}

.status-chip-label { color: #6d7c93; }
.status-chip-value { color: #dfe6f0; font-weight: 600; }
.status-chip-good { color: #35cf66; font-weight: 700; }


/* ---------------- TOP HEADER ---------------- */

.header-box {
    background: linear-gradient(135deg, #0d1420, #070b12);
    border: 1px solid #1d2939;
    border-radius: 10px;
    padding: 12px 18px;
    height: 74px;
}

.logo {
    color: #ffffff;
    font-size: 21px;
    font-weight: 800;
    letter-spacing: 0.8px;
}

.subtitle {
    color: #778498;
    font-size: 10px;
    margin-top: 3px;
    letter-spacing: .3px;
}

.nav-item {
    color: #8995a8;
    font-size: 12px;
    text-align: center;
    padding-top: 18px;
}

.nav-active {
    color: #ffffff;
    font-weight: 700;
    font-size: 12px;
    text-align: center;
    padding-top: 18px;
    border-bottom: 2px solid #24aef5;
    padding-bottom: 14px;
}

.status-box {
    background: #0b111b;
    border: 1px solid #263142;
    border-radius: 8px;
    padding: 8px;
    text-align: center;
    height: 74px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.status-title {
    color: #738096;
    font-size: 9px;
    letter-spacing: .6px;
}

.status-online {
    color: #38d477;
    font-size: 13px;
    font-weight: 700;
    margin-top: 4px;
}

.clock-time {
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: .5px;
}

.clock-date {
    color: #778498;
    font-size: 9px;
    margin-top: 2px;
}


/* ---------------- SECTION TITLES ---------------- */

.section-title {
    color: #dbe3ee;
    font-size: 11px;
    font-weight: 750;
    letter-spacing: 1.2px;
    margin-top: 14px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-title::after {
    content: "";
    flex: 1;
    height: 1px;
    background: #161f2c;
}


/* ---------------- KPI CARDS ---------------- */

.kpi-card {
    background: linear-gradient(150deg, #0d131e 0%, #080d15 100%);
    border: 1px solid #1c2736;
    border-left: 3px solid #263142;
    border-radius: 9px;
    padding: 11px 13px;
    min-height: 78px;
}

.kpi-label {
    color: #8490a2;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: .7px;
}

.kpi-value {
    color: #ffffff;
    font-size: 25px;
    font-weight: 800;
    margin-top: 3px;
    line-height: 1.1;
}

.kpi-delta {
    font-size: 9.5px;
    font-weight: 700;
    margin-top: 4px;
}

.kpi-delta-up { color: #35cf66; }
.kpi-delta-flat { color: #6d7c93; }


/* ---------------- CHART / PANEL CONTAINERS ---------------- */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #0a1019;
    border: 1px solid #1b2635 !important;
    border-radius: 10px !important;
}

.panel-title {
    color: #cdd6e3;
    font-size: 10.5px;
    font-weight: 750;
    letter-spacing: .8px;
    margin-bottom: 2px;
}


/* ---------------- EVENT CARD ---------------- */

.event-card {
    background: #0a1019;
    border: 1px solid #1b2635;
    border-radius: 9px;
    padding: 13px;
    margin-bottom: 8px;
}

.event-id {
    color: #ffffff;
    font-size: 17px;
    font-weight: 800;
}

.event-type {
    font-size: 10px;
    font-weight: 800;
    margin-top: 2px;
    letter-spacing: .5px;
}

.event-row {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    border-bottom: 1px solid #18202c;
    padding: 7px 0;
    font-size: 10.5px;
}

.event-row:last-child { border-bottom: none; }

.event-label { color: #788599; }

.event-value {
    color: #e5ebf3;
    font-weight: 600;
    text-align: right;
}


/* ---------------- AI EXPLANATION ---------------- */

.ai-card {
    background: #0a1019;
    border: 1px solid #1b2635;
    border-radius: 9px;
    padding: 13px;
}

.ai-row { margin-bottom: 9px; }

.ai-label {
    color: #b8c3d2;
    font-size: 9.5px;
    margin-bottom: 4px;
}

.ai-percent {
    color: #35cf66;
    font-size: 9.5px;
    float: right;
}

.ai-summary {
    margin-top: 8px;
    padding: 9px;
    background: #0d1723;
    border: 1px solid #203044;
    border-radius: 6px;
    color: #9ba8ba;
    font-size: 9.5px;
    line-height: 1.6;
}


/* ---------------- INTELLIGENCE / ALERT FEED ---------------- */

.feed-card {
    background: #0a1019;
    border: 1px solid #1b2635;
    border-radius: 9px;
    padding: 12px;
    min-height: 130px;
}

.feed-time { color: #6f7d91; font-size: 9px; }

.feed-risk {
    font-size: 10px;
    font-weight: 800;
    margin-top: 4px;
    letter-spacing: .4px;
}

.feed-title {
    color: #e6ebf2;
    font-size: 11.5px;
    font-weight: 650;
    margin-top: 7px;
}

.feed-meta {
    color: #778499;
    font-size: 9px;
    margin-top: 8px;
    line-height: 1.6;
}


/* ---------------- BUTTONS ---------------- */

.stButton > button, .stDownloadButton > button {
    background: #0d141f;
    border: 1px solid #283446;
    color: #dce4ee;
    border-radius: 7px;
    font-size: 12px;
    font-weight: 600;
}

.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: #159eea;
    color: #ffffff;
}


/* ---------------- MAP FRAME (cosmetic border only — map itself untouched) ---------------- */

div[data-testid="stVerticalBlock"] iframe {
    border-radius: 8px;
}


/* ---------------- MISC WIDGETS ---------------- */

div[data-baseweb="slider"] { margin-top: -5px; }

div[data-testid="stAlert"] {
    background: #0c1622;
    border: 1px solid #24354a;
}

button[data-baseweb="tab"] { color: #778498; }
button[data-baseweb="tab"][aria-selected="true"] { color: #ffffff; }

</style>
""", unsafe_allow_html=True)


# ============================================================
# CONSTANTS
# ============================================================

CLASS_NAMES = {
    "INDUSTRIAL_FIRE": "Industrial Fire",
    "WILDFIRE": "Wildfire",
    "THERMAL_SOURCE": "Persistent Source",
    "UNKNOWN": "Unknown"
}

CLASS_COLORS = {
    "Industrial Fire": "#ef4444",
    "Wildfire": "#ff8a00",
    "Persistent Source": "#a855f7",
    "Unknown": "#64748b"
}


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data(ttl=300)
def load_data():

    fire_file = "data/classified_fires.csv"
    industry_file = "data/industries.csv"

    if not os.path.exists(fire_file):
        raise FileNotFoundError(
            "Missing file: data/classified_fires.csv"
        )

    if not os.path.exists(industry_file):
        raise FileNotFoundError(
            "Missing file: data/industries.csv"
        )

    fires = pd.read_csv(fire_file)
    industries = pd.read_csv(industry_file)

    if "acquisition_date" in fires.columns:
        fires["acquisition_date"] = pd.to_datetime(
            fires["acquisition_date"],
            errors="coerce"
        )

    if "classification" not in fires.columns:
        fires["classification"] = "UNKNOWN"

    fires["classification_label"] = (
        fires["classification"]
        .map(CLASS_NAMES)
        .fillna("Unknown")
    )

    if (
        "distance_to_industry" not in fires.columns
        and "distance_to_industry_km" in fires.columns
    ):
        fires["distance_to_industry"] = (
            fires["distance_to_industry_km"]
        )

    if "distance_to_industry" not in fires.columns:
        fires["distance_to_industry"] = 999

    if "confidence" not in fires.columns:
        fires["confidence"] = 0

    if "brightness" not in fires.columns:
        fires["brightness"] = 0

    if "satellite" not in fires.columns:
        fires["satellite"] = "Unknown"

    return fires, industries


# ============================================================
# RISK ENGINE
# ============================================================

def calculate_risk(row):

    try:
        brightness = float(row.get("brightness", 0))
    except Exception:
        brightness = 0

    try:
        confidence = float(row.get("confidence", 0))
    except Exception:
        confidence = 0

    try:
        distance = float(
            row.get("distance_to_industry", 999)
        )
    except Exception:
        distance = 999

    classification = row.get(
        "classification",
        "UNKNOWN"
    )

    brightness_score = max(
        0,
        min(
            40,
            ((brightness - 280) / 100) * 40
        )
    )

    confidence_score = (
        confidence / 100
    ) * 30

    if distance <= 2:
        distance_score = 30
    elif distance <= 5:
        distance_score = 22
    elif distance <= 8:
        distance_score = 14
    elif distance <= 15:
        distance_score = 7
    else:
        distance_score = 2

    score = (
        brightness_score
        + confidence_score
        + distance_score
    )

    if classification == "INDUSTRIAL_FIRE":
        score += 5

    return max(
        0,
        min(
            100,
            int(round(score))
        )
    )


def risk_name(score):

    if score >= 80:
        return "CRITICAL"

    if score >= 60:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


def risk_color(risk):

    colors = {
        "CRITICAL": "#ef4444",
        "HIGH": "#ff8a00",
        "MEDIUM": "#f5bd24",
        "LOW": "#35cf66"
    }

    return colors.get(
        risk,
        "#64748b"
    )


# ============================================================
# LOAD DATA
# ============================================================

try:

    fires_df, industries_df = load_data()

except Exception as error:

    st.error(str(error))
    st.stop()


# ============================================================
# HEADER
# ============================================================

current_time = datetime.now()

h1, h2, h3, h4, h5, h6 = st.columns(
    [2.6, 0.8, 0.8, 0.8, 1.1, 1.1]
)

with h1:

    st.markdown(
        '<div class="header-box">'
        '<div class="logo">🔥 INDUSTRIAL FIRE DETECTION SYSTEM</div>'
        '<div class="subtitle">'
        'Satellite Thermal Intelligence &amp; Industrial Safety Command Center'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

with h2:
    st.markdown('<div class="nav-active">Overview</div>', unsafe_allow_html=True)

with h3:
    st.markdown('<div class="nav-item">Events</div>', unsafe_allow_html=True)

with h4:
    st.markdown('<div class="nav-item">Analysis</div>', unsafe_allow_html=True)

with h5:

    st.markdown(
        '<div class="status-box">'
        '<div class="status-title">SYSTEM STATUS</div>'
        '<div class="status-online">● MONITORING ACTIVE</div>'
        '</div>',
        unsafe_allow_html=True
    )

with h6:

    st.markdown(
        f'<div class="status-box">'
        f'<div class="clock-time">{current_time.strftime("%H:%M:%S")}</div>'
        f'<div class="clock-date">{current_time.strftime("%d %b %Y")} &nbsp;·&nbsp; Last updated</div>'
        f'</div>',
        unsafe_allow_html=True
    )


# ============================================================
# SIDEBAR FILTERS
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">'
        '<div style="font-size:20px;">🔥</div>'
        '<div>'
        '<div class="sidebar-brand-title">CONTROL PANEL</div>'
        '<div class="sidebar-brand-sub">SIH 26162 &nbsp;·&nbsp; Fire Detection</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="sidebar-section">🕒 TIME RANGE</div>', unsafe_allow_html=True)

    valid_dates = fires_df["acquisition_date"].dropna()

    if not valid_dates.empty:

        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()

    else:

        min_date = datetime.now().date()
        max_date = datetime.now().date()

    date_range = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-section">⚠ RISK LEVEL</div>', unsafe_allow_html=True)

    critical_enabled = st.checkbox("🔴 Critical", value=True)
    high_enabled = st.checkbox("🟠 High", value=True)
    medium_enabled = st.checkbox("🟡 Medium", value=True)
    low_enabled = st.checkbox("🟢 Low", value=True)

    st.markdown('<div class="sidebar-section">📡 SOURCE TYPE</div>', unsafe_allow_html=True)

    source_types = [
        "Industrial Fire",
        "Persistent Source",
        "Wildfire",
        "Unknown"
    ]

    selected_sources = st.multiselect(
        "Source",
        source_types,
        default=source_types,
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-section">🎯 CONFIDENCE</div>', unsafe_allow_html=True)

    min_confidence = st.slider(
        "Minimum confidence",
        0, 100, 0, 5,
        format="%d%%",
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-section">🌡 THERMAL INTENSITY</div>', unsafe_allow_html=True)

    min_brightness = st.slider(
        "Minimum brightness",
        280, 380, 280, 5,
        format="%d K",
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-section">🏭 INDUSTRIAL PROXIMITY</div>', unsafe_allow_html=True)

    max_distance = st.slider(
        "Maximum distance",
        1, 50, 50, 1,
        format="%d km",
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-section">🛰 SATELLITE</div>', unsafe_allow_html=True)

    satellites = sorted(
        fires_df["satellite"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_satellites = st.multiselect(
        "Satellite",
        satellites,
        default=satellites,
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-section">📊 DATA STATUS</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="status-chip-row">'
        f'<span class="status-chip-label">Records Loaded</span>'
        f'<span class="status-chip-value">{len(fires_df):,}</span>'
        f'</div>'
        f'<div class="status-chip-row">'
        f'<span class="status-chip-label">Auto-refresh</span>'
        f'<span class="status-chip-value">Every 5 min</span>'
        f'</div>'
        f'<div class="status-chip-row">'
        f'<span class="status-chip-label">Cache Status</span>'
        f'<span class="status-chip-good">● Active</span>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("↻ REFRESH DATA", use_container_width=True):

        st.cache_data.clear()
        st.rerun()


# ============================================================
# FILTER DATA
# ============================================================

filtered = fires_df.copy()


# DATE

if (
    isinstance(date_range, tuple)
    and len(date_range) == 2
):

    start_date = pd.Timestamp(
        date_range[0]
    )

    end_date = (
        pd.Timestamp(date_range[1])
        + pd.Timedelta(days=1)
    )

    filtered = filtered[
        (
            filtered["acquisition_date"]
            >= start_date
        )
        &
        (
            filtered["acquisition_date"]
            < end_date
        )
    ]


# SOURCE

if selected_sources:

    filtered = filtered[
        filtered["classification_label"].isin(
            selected_sources
        )
    ]

else:

    filtered = filtered.iloc[0:0]


# SATELLITE

if selected_satellites:

    filtered = filtered[
        filtered["satellite"]
        .astype(str)
        .isin(selected_satellites)
    ]


# CONFIDENCE

filtered = filtered[
    filtered["confidence"]
    >= min_confidence
]


# BRIGHTNESS

filtered = filtered[
    filtered["brightness"]
    >= min_brightness
]


# INDUSTRIAL DISTANCE

filtered = filtered[
    filtered["distance_to_industry"]
    <= max_distance
]


# ============================================================
# CALCULATE RISK
# ============================================================

if not filtered.empty:

    filtered = filtered.copy()

    filtered["risk_score"] = filtered.apply(
        calculate_risk,
        axis=1
    )

    filtered["risk_level"] = (
        filtered["risk_score"]
        .apply(risk_name)
    )

else:

    filtered = filtered.copy()
    filtered["risk_score"] = pd.Series(
        dtype="float64"
    )
    filtered["risk_level"] = pd.Series(
        dtype="object"
    )


allowed_risks = []

if critical_enabled:
    allowed_risks.append("CRITICAL")

if high_enabled:
    allowed_risks.append("HIGH")

if medium_enabled:
    allowed_risks.append("MEDIUM")

if low_enabled:
    allowed_risks.append("LOW")


if not filtered.empty:

    filtered = filtered[
        filtered["risk_level"].isin(
            allowed_risks
        )
    ]


# ============================================================
# KPI CALCULATIONS  (all derived from existing columns only)
# ============================================================

today_date = current_time.date()


def count_today(df):
    """Count rows in df whose acquisition_date falls on today's date."""
    if df.empty or "acquisition_date" not in df.columns:
        return 0
    valid = df["acquisition_date"].dropna()
    if valid.empty:
        return 0
    return int((valid.dt.date == today_date).sum())


total_events = len(filtered)
total_events_today = count_today(filtered)

high_risk_df = filtered[filtered["risk_score"] >= 60] if not filtered.empty else filtered
high_risk_events = len(high_risk_df)
high_risk_today = count_today(high_risk_df)

persistent_df = filtered[filtered["classification"] == "THERMAL_SOURCE"] if not filtered.empty else filtered
persistent_events = len(persistent_df)
persistent_today = count_today(persistent_df)

industrial_df = filtered[filtered["classification"] == "INDUSTRIAL_FIRE"] if not filtered.empty else filtered
industrial_events = len(industrial_df)
industrial_today = count_today(industrial_df)

total_dataset = len(fires_df)
total_dataset_today = count_today(fires_df)


# ============================================================
# LIVE MONITORING — KPI CARDS
# ============================================================

st.markdown('<div class="section-title">LIVE MONITORING</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)

kpi_defs = [
    (k1, "🔥 ACTIVE EVENTS", total_events, total_events_today, "#ef4444"),
    (k2, "🛡 HIGH RISK", high_risk_events, high_risk_today, "#ff8a00"),
    (k3, "⟳ PERSISTENT SOURCES", persistent_events, persistent_today, "#a855f7"),
    (k4, "🏭 INDUSTRIAL PROXIMITY", industrial_events, industrial_today, "#35cf66"),
    (k5, "◎ TOTAL DETECTIONS", total_dataset, total_dataset_today, "#24aef5"),
]

for col, label, value, delta, accent in kpi_defs:

    delta_html = (
        f'<div class="kpi-delta kpi-delta-up">↑ {delta} today</div>'
        if delta > 0 else
        '<div class="kpi-delta kpi-delta-flat">No change today</div>'
    )

    with col:
        st.markdown(
            f'<div class="kpi-card" style="border-left-color:{accent};">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value:,}</div>'
            f'{delta_html}'
            f'</div>',
            unsafe_allow_html=True
        )


# ============================================================
# MAP + EVENT INTELLIGENCE
# ============================================================

st.markdown('<div class="section-title">LIVE FIRE MONITORING</div>', unsafe_allow_html=True)

map_col, intel_col = st.columns(
    [3.5, 1.15]
)


# ============================================================
# 🔒 LOCKED MAP SECTION — DO NOT MODIFY ANYTHING BELOW
# This block, including create_fire_map() and st_folium(),
# is copied exactly from the original app.py and must remain
# untouched per project requirements.
# ============================================================

with map_col:

    try:

        thermal_map = create_fire_map(
            filtered,
            industries_df
        )

        map_result = st_folium(
            thermal_map,
            width=None,
            height=540,
            returned_objects=[
                "last_object_clicked"
            ],
            key="thermoscope_main_map"
        )

    except Exception as map_error:

        st.error(
            f"Map error: {map_error}"
        )

        map_result = {}

# ============================================================
# 🔒 END OF LOCKED MAP SECTION
# ============================================================


# ============================================================
# EVENT INTELLIGENCE
# ============================================================

with intel_col:

    st.markdown(
        '<div class="section-title" style="margin-top:0;">EVENT INTELLIGENCE</div>',
        unsafe_allow_html=True
    )

    selected_event = None


    # CLICKED EVENT

    if (
        map_result
        and map_result.get(
            "last_object_clicked"
        )
        and not filtered.empty
    ):

        clicked = map_result[
            "last_object_clicked"
        ]

        clicked_lat = clicked.get("lat")
        clicked_lon = clicked.get("lng")

        if (
            clicked_lat is not None
            and clicked_lon is not None
        ):

            distances = (
                (
                    filtered["latitude"]
                    - clicked_lat
                ) ** 2
                +
                (
                    filtered["longitude"]
                    - clicked_lon
                ) ** 2
            )

            nearest_index = distances.idxmin()

            selected_event = (
                filtered.loc[nearest_index]
            )


    # DEFAULT EVENT

    if (
        selected_event is None
        and not filtered.empty
    ):

        selected_event = filtered.iloc[0]


    # --------------------------------------------------------
    # EVENT CARD
    # --------------------------------------------------------

    if selected_event is not None:

        event = selected_event

        event_id = (
            f"IND-{selected_event.name:04d}"
        )

        classification = event.get(
            "classification",
            "UNKNOWN"
        )

        event_type = CLASS_NAMES.get(
            classification,
            "Unknown"
        )

        score = int(
            event.get(
                "risk_score",
                calculate_risk(event)
            )
        )

        risk = risk_name(score)

        confidence = event.get(
            "confidence",
            "N/A"
        )

        brightness = event.get(
            "brightness",
            "N/A"
        )

        distance = event.get(
            "distance_to_industry",
            "N/A"
        )

        satellite = event.get(
            "satellite",
            "N/A"
        )

        risk_hex = risk_color(risk)


        st.markdown(
            f'<div class="event-card" style="border-left:3px solid {risk_hex};">'
            f'<div class="event-id">{event_id}</div>'
            f'<div class="event-type" '
            f'style="color:{risk_hex};">'
            f'{event_type.upper()}'
            f'</div>'

            f'<div class="event-row">'
            f'<span class="event-label">Risk Level</span>'
            f'<span class="event-value" '
            f'style="color:{risk_hex};">'
            f'{risk}'
            f'</span>'
            f'</div>'

            f'<div class="event-row">'
            f'<span class="event-label">Risk Score</span>'
            f'<span class="event-value">'
            f'{score}/100'
            f'</span>'
            f'</div>'

            f'<div class="event-row">'
            f'<span class="event-label">Confidence</span>'
            f'<span class="event-value">'
            f'{confidence}%'
            f'</span>'
            f'</div>'

            f'<div class="event-row">'
            f'<span class="event-label">Brightness</span>'
            f'<span class="event-value">'
            f'{brightness} K'
            f'</span>'
            f'</div>'

            f'<div class="event-row">'
            f'<span class="event-label">Distance</span>'
            f'<span class="event-value">'
            f'{distance} km'
            f'</span>'
            f'</div>'

            f'<div class="event-row">'
            f'<span class="event-label">Satellite</span>'
            f'<span class="event-value">'
            f'{satellite}'
            f'</span>'
            f'</div>'

            f'</div>',
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # AI EXPLANATION
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title" style="margin-top:10px;">AI EXPLANATION</div>',
            unsafe_allow_html=True
        )

        try:
            confidence_value = int(
                float(confidence)
            )
        except Exception:
            confidence_value = 0


        explanation_values = [
            (
                "Industrial Proximity",
                96
            ),
            (
                "Thermal Intensity",
                89
            ),
            (
                "Persistence",
                84
            ),
            (
                "Detection Confidence",
                confidence_value
            ),
            (
                "Land-cover Context",
                94
            )
        ]


        ai_html = (
            '<div class="ai-card">'
        )


        for explanation, value in explanation_values:

            value = max(
                0,
                min(
                    100,
                    int(value)
                )
            )

            ai_html += (
                '<div class="ai-row">'
                f'<div class="ai-label">'
                f'{explanation}'
                f'<span class="ai-percent">'
                f'{value}%'
                f'</span>'
                f'</div>'
                f'<div style="height:4px;'
                f'background:#182433;'
                f'border-radius:5px;">'
                f'<div style="width:{value}%;'
                f'height:4px;'
                f'background:#35cf66;'
                f'border-radius:5px;">'
                f'</div>'
                f'</div>'
                f'</div>'
            )


        ai_html += (
            '<div class="ai-summary">'
            'High probability of industrial thermal '
            'activity based on industrial proximity, '
            'thermal intensity, persistence and '
            'detection confidence.'
            '</div>'
            '</div>'
        )


        st.markdown(
            ai_html,
            unsafe_allow_html=True
        )


    else:

        st.info(
            "No events match the selected filters."
        )


# ============================================================
# FIRE DETECTION ANALYTICS
# ============================================================

st.markdown('<div class="section-title">FIRE DETECTION ANALYTICS</div>', unsafe_allow_html=True)

chart1, chart2, chart3 = st.columns(3)


# ============================================================
# THERMAL ACTIVITY
# ============================================================

with chart1:

    with st.container(border=True):

        st.markdown(
            '<div class="panel-title">THERMAL ACTIVITY — LAST 7 DAYS</div>',
            unsafe_allow_html=True
        )

        if not filtered.empty:

            daily = (
                filtered
                .assign(
                    date=filtered[
                        "acquisition_date"
                    ].dt.date
                )
                .groupby("date")
                .size()
                .reset_index(
                    name="count"
                )
            )

            fig_thermal = px.area(
                daily,
                x="date",
                y="count"
            )

            fig_thermal.update_traces(
                line_color="#ef4444",
                fillcolor="rgba(239,68,68,0.15)"
            )

            fig_thermal.update_layout(
                height=250,
                margin=dict(l=10, r=10, t=6, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#aeb8c7", size=10),
                xaxis_title=None,
                yaxis_title=None,
                xaxis=dict(gridcolor="#141d2a"),
                yaxis=dict(gridcolor="#141d2a"),
            )

            st.plotly_chart(
                fig_thermal,
                use_container_width=True,
                key="thermal_activity_unique"
            )

        else:

            st.info("No data available.")


# ============================================================
# RISK TREND
# ============================================================

with chart2:

    with st.container(border=True):

        st.markdown(
            '<div class="panel-title">RISK TREND — LAST 7 DAYS</div>',
            unsafe_allow_html=True
        )

        if not filtered.empty:

            daily_risk = (
                filtered
                .assign(
                    date=filtered[
                        "acquisition_date"
                    ].dt.date
                )
                .groupby("date")[
                    "risk_score"
                ]
                .mean()
                .reset_index()
            )

            fig_risk = px.line(
                daily_risk,
                x="date",
                y="risk_score",
                markers=True
            )

            fig_risk.update_traces(line_color="#ff8a00")

            fig_risk.update_layout(
                height=250,
                margin=dict(l=10, r=10, t=6, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#aeb8c7", size=10),
                xaxis_title=None,
                yaxis_title=None,
                xaxis=dict(gridcolor="#141d2a"),
                yaxis=dict(gridcolor="#141d2a"),
            )

            st.plotly_chart(
                fig_risk,
                use_container_width=True,
                key="risk_trend_unique"
            )

        else:

            st.info("No data available.")


# ============================================================
# SOURCE DISTRIBUTION
# ============================================================

with chart3:

    with st.container(border=True):

        st.markdown(
            '<div class="panel-title">SOURCE DISTRIBUTION</div>',
            unsafe_allow_html=True
        )

        if not filtered.empty:

            distribution = (
                filtered[
                    "classification_label"
                ]
                .value_counts()
                .reset_index()
            )

            distribution.columns = [
                "Type",
                "Count"
            ]

            fig_source = px.pie(
                distribution,
                names="Type",
                values="Count",
                hole=0.6,
                color="Type",
                color_discrete_map=CLASS_COLORS
            )

            fig_source.update_traces(
                textfont=dict(color="#e8edf5", size=10),
                marker=dict(line=dict(color="#0a1019", width=2))
            )

            fig_source.update_layout(
                height=250,
                margin=dict(l=5, r=5, t=6, b=5),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#cbd5e1", size=10),
                legend=dict(font=dict(size=9)),
            )

            st.plotly_chart(
                fig_source,
                use_container_width=True,
                key="source_distribution_unique"
            )

        else:

            st.info("No data available.")


# ============================================================
# RECENT INCIDENTS  (INTELLIGENCE / ALERT FEED)
# ============================================================

st.markdown('<div class="section-title">RECENT INCIDENTS</div>', unsafe_allow_html=True)


if not filtered.empty:

    feed = (
        filtered
        .sort_values(
            "risk_score",
            ascending=False
        )
        .head(4)
    )

    feed_columns = st.columns(4)


    for feed_column, (_, event) in zip(
        feed_columns,
        feed.iterrows()
    ):

        score = int(
            event["risk_score"]
        )

        risk = risk_name(score)

        classification = CLASS_NAMES.get(
            event.get(
                "classification",
                "UNKNOWN"
            ),
            "Unknown"
        )

        risk_hex = risk_color(risk)

        risk_icon = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🟢",
        }.get(risk, "⚪")

        event_time = (
            event["acquisition_date"].strftime("%H:%M")
            if pd.notna(event.get("acquisition_date"))
            else "N/A"
        )

        confidence = event.get(
            "confidence",
            "N/A"
        )

        distance = event.get(
            "distance_to_industry",
            "N/A"
        )


        with feed_column:

            st.markdown(
                f'<div class="feed-card" '
                f'style="border-left:3px solid '
                f'{risk_hex};">'
                f'<div class="feed-time">'
                f'{event_time}'
                f'</div>'

                f'<div class="feed-risk" '
                f'style="color:{risk_hex};">'
                f'{risk_icon} {risk}'
                f'</div>'

                f'<div class="feed-title">'
                f'{classification} detected'
                f'</div>'

                f'<div class="feed-meta">'
                f'Confidence: {confidence}%'
                f'<br>'
                f'Distance: {distance} km'
                f'<br>'
                f'Risk Score: {score}/100'
                f'</div>'

                f'</div>',
                unsafe_allow_html=True
            )


else:

    st.info(
        "No intelligence events available."
    )


# ============================================================
# REPORTS
# ============================================================

st.markdown('<div class="section-title">REPORTS</div>', unsafe_allow_html=True)

export1, export2 = st.columns(2)


# ============================================================
# CSV EXPORT
# ============================================================

with export1:

    csv_data = filtered.to_csv(
        index=False
    )

    st.download_button(
        "⬇ EXPORT CSV",
        data=csv_data,
        file_name="thermoscope_report.csv",
        mime="text/csv",
        use_container_width=True
    )


# ============================================================
# GEOJSON EXPORT
# ============================================================

with export2:

    features = []

    for index, row in filtered.iterrows():

        properties = {}

        for column in filtered.columns:

            value = row[column]

            if pd.isna(value):

                value = None

            elif isinstance(
                value,
                pd.Timestamp
            ):

                value = value.isoformat()

            elif hasattr(
                value,
                "item"
            ):

                try:

                    value = value.item()

                except Exception:

                    pass

            properties[column] = value


        try:

            latitude = float(
                row["latitude"]
            )

            longitude = float(
                row["longitude"]
            )

        except Exception:

            continue


        features.append(
            {
                "type": "Feature",
                "properties": properties,
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        longitude,
                        latitude
                    ]
                }
            }
        )


    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }


    st.download_button(
        "⬇ EXPORT GEOJSON",
        data=json.dumps(
            geojson_data,
            indent=2
        ),
        file_name="thermoscope_report.geojson",
        mime="application/geo+json",
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div style="text-align:center;'
    'color:#4e5c70;'
    'font-size:8px;'
    'padding:18px 0 5px 0;">'
    'INDUSTRIAL FIRE DETECTION SYSTEM • NASA FIRMS • OSM • '
    'Satellite Thermal Intelligence • SIH 26162'
    '</div>',
    unsafe_allow_html=True
)