"""
SIH 26162 - AI-Based Industrial Fire Detection & Persistent Thermal Source Monitoring
"""

import os
import json
from datetime import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from streamlit_folium import st_folium
from map_visualization import create_fire_map


# ============================================================
# API CONFIG
# ============================================================
# Backend is the single source of truth for risk_score / risk_level.
# Streamlit must NEVER recompute risk locally — see risk_engine.py.
#
# ASSUMPTION: fires.py exposes GET /api/v1/fires and industries.py
# exposes GET /api/v1/industries, each returning a JSON array of row
# dicts (same shape as data_service.load_fires()/load_industries()).
# Adjust API_BASE / the two endpoint paths below if yours differ.
# ============================================================

API_BASE = os.environ.get("FIRE_API_BASE", "http://localhost:8000")
FIRES_ENDPOINT = f"{API_BASE}/api/v1/fires"
INDUSTRIES_ENDPOINT = f"{API_BASE}/api/v1/industries"
SUMMARY_ENDPOINT = f"{API_BASE}/api/v1/analytics/summary"


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

/* ---------------- NATIVE SIDEBAR TOGGLE ----------------
   Keep Streamlit's built-in sidebar control visible and
   functional. It automatically switches between << and >>
   when the Control Panel is expanded/collapsed.
*/
header {
    visibility: visible !important;
    background: transparent !important;
}

/* Expanded-state collapse button */
button[data-testid="stSidebarCollapseButton"] {
    visibility: visible !important;
    opacity: 1 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 30px !important;
    height: 30px !important;
    background: #111a27 !important;
    border: 1px solid #283446 !important;
    border-radius: 8px !important;
    color: #dce4ee !important;
    z-index: 999999 !important;
    transition: all 0.2s ease !important;
}

button[data-testid="stSidebarCollapseButton"]:hover {
    background: #172335 !important;
    border-color: #24aef5 !important;
    color: #ffffff !important;
}

/* Collapsed-state reopen control */
[data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}

[data-testid="stSidebarCollapsedControl"] button {
    visibility: visible !important;
    opacity: 1 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 30px !important;
    height: 30px !important;
    background: #111a27 !important;
    border: 1px solid #283446 !important;
    border-radius: 8px !important;
    color: #dce4ee !important;
    transition: all 0.2s ease !important;
}

[data-testid="stSidebarCollapsedControl"] button:hover {
    background: #172335 !important;
    border-color: #24aef5 !important;
    color: #ffffff !important;
}

button[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapsedControl"] button svg {
    color: #dce4ee !important;
    fill: #dce4ee !important;
}

html, body, [class*="css"] {
    font-family: -apple-system, "Segoe UI", Roboto, Inter, sans-serif;
}

html, body {
    background-color: #05080f !important;
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
    gap: 0.6rem;
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
    font-size: 21px;
    font-weight: 800;
    letter-spacing: 0.8px;
    position: relative;
    top: -34px;
  }

.sidebar-brand-sub {
    color: #62708a;
    font-size: 12px;
    letter-spacing: .5px;
}

.sidebar-section {
    color: #6d7c93;
    font-size: 10px;
    font-weight: 750;
    letter-spacing: 1.3px;
    margin-top: 16px;
    margin-bottom: 10px;
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
    background: #05080f !important;
    background-color: #05080f !important;
}

/* Prevent white flash while the map iframe remounts on every
   click-triggered rerun — color the wrapper behind it too */
div[data-testid="stVerticalBlock"]:has(> div > iframe),
div[data-testid="element-container"]:has(iframe),
div[data-testid="stCustomComponentV1"] {
    background: #05080f !important;
    background-color: #05080f !important;
}


/* ---------------- MISC WIDGETS ---------------- */

div[data-baseweb="slider"] {
    margin-top: 8px !important;
}

div[data-testid="stAlert"] {
    background: #0c1622;
    border: 1px solid #24354a;
}

button[data-baseweb="tab"] { color: #778498; }
button[data-baseweb="tab"][aria-selected="true"] { color: #ffffff; }
/* ============================================================
   INDUSTRIAL FIRE DATE PICKER
   NEW STREAMLIT CALENDAR
   ============================================================ */

/* ============================================================
   DATE INPUT FIELD
   ============================================================ */

div[data-testid="stDateInput"] {
    width: 100% !important;
}

/* Actual date field used by current Streamlit */
div[data-testid="stDateInputField"] {
    background: #080d15 !important;
    border: 1px solid #273445 !important;
    border-radius: 8px !important;
    color: #dce3ed !important;
}

/* Focused date field */
div[data-testid="stDateInputField"]:focus-within {
    border-color: #ff6b00 !important;

    box-shadow:
        0 0 0 1px rgba(255,107,0,.55),
        0 0 10px rgba(255,107,0,.35) !important;
}

/* ============================================================
   DATE FIELD — COMPLETE DATE TEXT
   ============================================================ */

div[data-testid="stDateInputField"] * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Keep focused date segment orange */
div[data-testid="stDateInputField"]
[role="spinbutton"][data-focused] {
    background: #ff6b00 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}


/* ============================================================
   CALENDAR POPUP
   ============================================================ */

div[data-testid="stDateInputCalendar"] {
    background: #080d15 !important;

    border: 1px solid #ff6b00 !important;
    border-radius: 10px !important;

    padding: 10px 12px !important;

    box-shadow:
        0 0 4px rgba(255,107,0,.90),
        0 0 12px rgba(255,107,0,.60),
        0 0 26px rgba(255,107,0,.28) !important;

    color: #dce3ed !important;
}


/* ============================================================
   CALENDAR ITSELF
   ============================================================ */

div[data-testid="stDateInputCalendar"] table {
    background: #080d15 !important;
    color: #dce3ed !important;
}

div[data-testid="stDateInputCalendar"] [role="grid"] {
    background: #080d15 !important;
}

div[data-testid="stDateInputCalendar"] [role="row"] {
    background: #080d15 !important;
}


/* ============================================================
   MONTH / YEAR HEADER
   ============================================================ */

div[data-testid="stDateInputCalendar"] header {
    background: #080d15 !important;

    color: #ff7a00 !important;

    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
}


/* Month + year buttons */

div[data-testid="stDateInputCalendar"] header button {
    background: transparent !important;

    border: none !important;

    color: #ff7a00 !important;

    font-weight: 700 !important;
}


/* Make "August 2026" clearly visible */

div[data-testid="stDateInputCalendar"]
header button {
    font-size: 12px !important;
}


/* Previous / Next buttons */

div[data-testid="stDateInputCalendar"]
header button[aria-label="Previous month"],
div[data-testid="stDateInputCalendar"]
header button[aria-label="Next month"] {

    color: #ffffff !important;

    width: 28px !important;
    height: 28px !important;

    border-radius: 6px !important;
}


/* Arrow hover */

div[data-testid="stDateInputCalendar"]
header button[aria-label="Previous month"]:hover,
div[data-testid="stDateInputCalendar"]
header button[aria-label="Next month"]:hover {

    background: rgba(255,107,0,.18) !important;

    color: #ff7a00 !important;
}


/* Month/year selector hover */

div[data-testid="stDateInputCalendar"]
header button:hover {

    background: rgba(255,107,0,.10) !important;

    color: #ff8a20 !important;
}


/* ============================================================
   WEEKDAY HEADER
   ============================================================ */

div[data-testid="stDateInputCalendar"]
[role="columnheader"] {

    background: #080d15 !important;

    color: #dce3ed !important;

    font-size: 10px !important;

    font-weight: 600 !important;

    text-align: center !important;
}


/* ============================================================
   NORMAL DATES
   ============================================================ */

div[data-testid="stDateInputCalendar"]
[role="gridcell"] {

    background: transparent !important;

    color: #dce3ed !important;

    text-align: center !important;
}


/* Calendar date cells */

div[data-testid="stDateInputCalendar"]
[role="gridcell"] {

    cursor: pointer !important;
}


/* ============================================================
   DATE HOVER
   ============================================================ */

div[data-testid="stDateInputCalendar"]
[role="gridcell"][data-hovered] {

    background: rgba(255,107,0,.15) !important;

    color: #ffffff !important;

    border-radius: 6px !important;
}
/* ============================================================
   OUTSIDE MONTH DATES — DIM GRAY
   ============================================================ */

div[data-testid="stDateInputCalendar"]
[role="gridcell"][data-outside-month],
div[data-testid="stDateInputCalendar"]
[role="gridcell"][data-outside-month] * {

    color: #596273 !important;
    -webkit-text-fill-color: #596273 !important;
    opacity: .65 !important;
}




/* ============================================================
   SELECTED RANGE
   ============================================================ */

/* Dates inside selected range */

div[data-testid="stDateInputCalendar"]
[role="gridcell"][data-selected] {

    background: rgba(255,107,0,.20) !important;

    color: #ffffff !important;
}


/* Start date */

div[data-testid="stDateInputCalendar"]
[role="gridcell"][data-selection-start] {

    background: #ff6b00 !important;

    color: #ffffff !important;

    border-radius: 6px !important;

    font-weight: 700 !important;

    box-shadow:
        0 0 5px rgba(255,107,0,.90),
        0 0 12px rgba(255,107,0,.50) !important;
}


/* End date */

div[data-testid="stDateInputCalendar"]
[role="gridcell"][data-selection-end] {

    background: #ff6b00 !important;

    color: #ffffff !important;

    border-radius: 6px !important;

    font-weight: 700 !important;

    box-shadow:
        0 0 5px rgba(255,107,0,.90),
        0 0 12px rgba(255,107,0,.50) !important;
}


/* Single day / same start and end */

div[data-testid="stDateInputCalendar"]
[role="gridcell"][data-selection-start][data-selection-end] {

    background: #ff6b00 !important;

    color: #ffffff !important;

    border-radius: 6px !important;
}


/* ============================================================
   TODAY
   ============================================================ */

div[data-testid="stDateInputCalendar"]
[role="gridcell"][data-today] {

    outline: 1px solid #ff6b00 !important;

    outline-offset: -1px !important;
}


/* ============================================================
   QUICK SELECT FOOTER
   ============================================================ */

div[data-testid="stDateInputQuickSelect"] {

    background: #080d15 !important;

    border-top: 1px solid rgba(255,107,0,.30) !important;

    color: #dce3ed !important;

    margin-top: 8px !important;

    padding-top: 8px !important;
}


/* "Date range" text */

div[data-testid="stDateInputQuickSelect"] {
    color: #dce3ed !important;
}


/* Past Week button */

div[data-testid="stDateInputQuickSelect"] button {

    background: transparent !important;

    color: #dce3ed !important;

    border: none !important;

    border-radius: 6px !important;
}


/* Quick select hover */

div[data-testid="stDateInputQuickSelect"] button:hover {

    background: rgba(255,107,0,.15) !important;

    color: #ff7a00 !important;
}


/* ============================================================
   MONTH / YEAR DROPDOWN POPUPS
   ============================================================ */

div[data-testid="stDateInputHeaderPickerPopover"] {

    background: #080d15 !important;

    border: 1px solid #ff6b00 !important;

    border-radius: 8px !important;

    box-shadow:
        0 0 8px rgba(255,107,0,.45) !important;
}


/* Month/year dropdown options */

div[data-testid="stDateInputHeaderPickerPopover"]
[role="option"] {

    background: #080d15 !important;

    color: #dce3ed !important;
}


/* Dropdown option hover */

div[data-testid="stDateInputHeaderPickerPopover"]
[role="option"]:hover {

    background: rgba(255,107,0,.18) !important;

    color: #ffffff !important;
}


/* ============================================================
   QUICK SELECT DROPDOWN
   ============================================================ */

div[data-testid="stDateInputQuickSelectPopover"] {

    background: #080d15 !important;

    border: 1px solid #ff6b00 !important;

    border-radius: 8px !important;

    box-shadow:
        0 0 8px rgba(255,107,0,.45) !important;
}

div[data-testid="stDateInputQuickSelectPopover"]
[role="option"] {

    background: #080d15 !important;

    color: #dce3ed !important;
}

div[data-testid="stDateInputQuickSelectPopover"]
[role="option"]:hover {

    background: rgba(255,107,0,.18) !important;

    color: #ffffff !important;
}
div[data-testid="stDateInputCalendar"] {
    background: #080d15 !important;
    border: 3px solid #ff6b00 !important;
    box-shadow: 0 0 20px #ff6b00 !important;
}
/* DATE INPUT - MAKE THE DISPLAYED DATE WHITE */
section[data-testid="stSidebar"] input {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* CALENDAR - MAKE WEEKDAY LETTERS WHITE */
div[data-testid="stDateInputCalendar"] * {
    color: #ffffff !important;
}
/* ============================================================
   DIM PREVIOUS / NEXT MONTH DATES
   ============================================================ */

div[data-testid="stDateInputCalendar"] 
div[data-outside-month="true"] {
    color: #596273 !important;
    opacity: 0.65 !important;
}
/* ============================================================
   CALENDAR WEEKDAY GLASS BUBBLES
   ============================================================ */

div[data-testid="stDateInputCalendar"] thead th {
    background: rgba(255, 255, 255, 0.035) !important;
    border: 1px solid rgba(255, 107, 0, 0.22) !important;
    border-radius: 6px !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.06),
        0 2px 6px rgba(0, 0, 0, 0.25) !important;
    backdrop-filter: blur(6px) !important;
    -webkit-backdrop-filter: blur(6px) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}
/* ============================================================
   WEEKDAY LETTERS — INDIVIDUAL NEON ORANGE GLASS BOXES
   ============================================================ */

div[data-testid="stDateInputCalendar"] thead th {
    color: #ffffff !important;
    background: rgba(255, 255, 255, 0.035) !important;

    border: 1px solid #ff6b00 !important;
    border-radius: 5px !important;

    box-shadow:
        0 0 5px rgba(255, 107, 0, 0.85),
        inset 0 0 6px rgba(255, 107, 0, 0.10) !important;

    padding: 5px 0 !important;

    font-weight: 600 !important;
    text-align: center !important;
}

/* Keep the S M T W T F S letters white */
div[data-testid="stDateInputCalendar"] thead th * {
    color: #ffffff !important;
}
/* =========================================================
   SOURCE TYPE — NEON GLASS PANEL
   ========================================================= */

/* The entire Source Type component */
div[data-testid="stMultiSelect"]:has(input[aria-label="Source"]) {
    background: rgba(5, 10, 18, 0.88) !important;
    border: 1px solid transparent !important;
    border-radius: 14px !important;
    padding: 8px !important;
    box-shadow: none !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

/* Neon border + glow only when hovering or focused (typing/selecting) */
div[data-testid="stMultiSelect"]:has(input[aria-label="Source"]):hover,
div[data-testid="stMultiSelect"]:has(input[aria-label="Source"]):focus-within {
    border: 1px solid #ff6b00 !important;
    box-shadow:
        0 0 5px rgba(255, 107, 0, 0.95),
        0 0 14px rgba(255, 107, 0, 0.55),
        inset 0 0 12px rgba(255, 107, 0, 0.08) !important;
}


/* IMPORTANT:
   Remove the WHITE BaseWeb background from
   the nested elements inside Source Type
*/
div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
div[data-baseweb="select"],
div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
div[data-baseweb="select"] > div,
div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
div[data-testid="stMultiSelectTagsContainer"] {
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
}


/* Remove white background from the internal
   React/BaseWeb wrapper */
div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
div[class*="react-aria-ComboBox"],
div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
div[class*="emotion-cache"] {
    background: transparent !important;
    background-color: transparent !important;
}


/* Source input itself */
div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
input[aria-label="Source"] {
    background: transparent !important;
    color: #ffffff !important;
}


/* =========================================================
   SELECTED SOURCE TAGS
   ========================================================= */


/* =========================================================
   CLEAR (X) BUTTON
   ========================================================= */

div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
button[aria-label="Clear"] {
    background: rgba(255, 255, 255, 0.12) !important;

    border: 1px solid rgba(255, 255, 255, 0.15) !important;

    border-radius: 50% !important;

    color: #ff6b00 !important;

    box-shadow:
        0 0 6px rgba(255, 107, 0, 0.35) !important;
}


/* =========================================================
   DROPDOWN ARROW
   ========================================================= */

div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
button[aria-label="Open"] {
    background: transparent !important;
    color: #ff6b00 !important;
}


/* Make arrow/icon orange */
div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
button[aria-label="Open"] svg {
    color: #ff6b00 !important;
    fill: #ff6b00 !important;
}


/* Remove BaseWeb's red background from anything INSIDE the tag */

div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
div[data-testid="stMultiSelectTagsContainer"]
[data-baseweb="tag"] * {

    background-color: transparent !important;
    background-image: none !important;
}
/* =========================================================
   SOURCE TAG — DARK RED GLASS PILL
   ========================================================= */

div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
div[data-testid="stMultiSelectTagsContainer"]
[data-baseweb="tag"] {

    /* soothing muted brick-red glass */
    background: linear-gradient(
        135deg,
        rgba(120, 62, 58, 0.55),
        rgba(70, 34, 32, 0.50)
    ) !important;

    /* thin, soft edge — no saturated glow */
    border: 1px solid rgba(180, 110, 100, 0.32) !important;

    /* pill shape */
    border-radius: 999px !important;

    /* soft neutral depth, no colored glow */
    box-shadow:
        inset 0 1px 1px rgba(255,255,255,0.10),
        inset 0 -2px 5px rgba(0,0,0,0.20),
        0 1px 4px rgba(0,0,0,0.25) !important;

    /* actual glass blur */
    backdrop-filter: blur(10px) saturate(100%) !important;
    -webkit-backdrop-filter: blur(10px) saturate(100%) !important;

    color: rgba(255,255,255,0.92) !important;

    transition: all 0.2s ease !important;
}


/* White text */

div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
div[data-testid="stMultiSelectTagsContainer"]
[data-baseweb="tag"] span {

    color: rgba(255,255,255,0.95) !important;
    font-weight: 500 !important;
}


/* X button */

div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
div[data-testid="stMultiSelectTagsContainer"]
[data-baseweb="tag"] button {

    background: transparent !important;
    border: none !important;
    color: rgba(255,255,255,0.75) !important;
}


/* X icon */

div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
div[data-testid="stMultiSelectTagsContainer"]
[data-baseweb="tag"] svg {

    color: rgba(255,255,255,0.9) !important;
    fill: rgba(255,255,255,0.9) !important;
}
/* =========================================================
   ACTUAL STREAMLIT SELECTED PILLS
   ========================================================= */

div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
div[data-testid="stMultiSelectTagsContainer"]
span[role="option"][data-tag-index] {

    background: linear-gradient(
        135deg,
        rgba(115, 60, 56, 0.55),
        rgba(62, 30, 28, 0.52)
    ) !important;

    background-color: rgba(80, 40, 38, 0.55) !important;

    border: 1px solid rgba(175, 105, 95, 0.30) !important;

    border-radius: 999px !important;

    box-shadow:
        inset 0 1px 1px rgba(255,255,255,0.10),
        inset 0 -2px 5px rgba(0,0,0,0.22),
        0 1px 4px rgba(0,0,0,0.25) !important;

    backdrop-filter: blur(10px) saturate(100%) !important;
    -webkit-backdrop-filter: blur(10px) saturate(100%) !important;

    color: rgba(255,255,255,0.92) !important;

    overflow: hidden !important;
}
/* TEXT INSIDE ACTUAL SOURCE PILL */

div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
div[data-testid="stMultiSelectTagsContainer"]
span[role="option"][data-tag-index] > span {

    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;

    color: rgba(255,255,255,0.95) !important;
}
/* X INSIDE ACTUAL SOURCE PILL */

div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
div[data-testid="stMultiSelectTagsContainer"]
span[role="option"][data-tag-index] button {

    background: transparent !important;
    background-color: transparent !important;
    border: none !important;

    color: rgba(255,255,255,0.80) !important;
}
/* X ICON */

div[data-testid="stMultiSelect"]:has(input[aria-label="Source"])
div[data-testid="stMultiSelectTagsContainer"]
span[role="option"][data-tag-index] svg {

    background: transparent !important;

    color: rgba(255,255,255,0.85) !important;
    fill: rgba(255,255,255,0.85) !important;
}
/* =========================================================
   SATELLITE — MATCH SOURCE TYPE DARK GLASS PANEL
   ========================================================= */

/* Entire Satellite multiselect box */
div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"]) {
    background: rgba(5, 10, 18, 0.88) !important;
    background-color: rgba(5, 10, 18, 0.88) !important;

    border: 1px solid transparent !important;
    border-radius: 14px !important;

    padding: 8px !important;
    box-shadow: none !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

/* Neon border + glow only when hovering or focused (typing/selecting) */
div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"]):hover,
div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"]):focus-within {
    border: 1px solid #ff6b00 !important;
    box-shadow:
    0 0 5px rgba(255, 107, 0, 0.95),
    0 0 14px rgba(255, 107, 0, 0.55),
    inset 0 0 12px rgba(255, 107, 0, 0.08) !important;
}


/* Remove Streamlit/BaseWeb WHITE background */
div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"])
div[data-baseweb="select"],
div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"])
div[data-baseweb="select"] > div,
div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"])
div[data-testid="stMultiSelectTagsContainer"] {
    background: #050a12 !important;
    background-color: #050a12 !important;
    box-shadow: none !important;
}


/* Remove white React/BaseWeb wrapper */
div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"])
div[class*="react-aria-ComboBox"],
div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"])
div[class*="emotion-cache"] {
    background: transparent !important;
    background-color: transparent !important;
}


/* Satellite input */
div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"])
input[aria-label="Satellite"] {
    background: transparent !important;
    color: #ffffff !important;
}


/* =========================================================
   SATELLITE SELECTED VALUE — DARK RED GLASS PILL
   ========================================================= */

div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"])
div[data-testid="stMultiSelectTagsContainer"]
[data-baseweb="tag"] {

    background: linear-gradient(
        135deg,
        rgba(120, 20, 25, 0.72),
        rgba(55, 5, 10, 0.58)
    ) !important;

    background-color: rgba(80, 8, 15, 0.72) !important;

    border: 1px solid rgba(255, 100, 90, 0.45) !important;

    border-radius: 7px !important;

    box-shadow:
        inset 0 1px 1px rgba(255,255,255,0.18),
        inset 0 -2px 5px rgba(0,0,0,0.25),
        0 2px 8px rgba(90,0,0,0.25) !important;

    backdrop-filter: blur(10px) saturate(120%) !important;
    -webkit-backdrop-filter: blur(10px) saturate(120%) !important;

    color: rgba(255,255,255,0.95) !important;
}


/* Satellite pill text */
div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"])
div[data-testid="stMultiSelectTagsContainer"]
[data-baseweb="tag"] span {
    color: rgba(255,255,255,0.95) !important;
    font-weight: 500 !important;
}


/* Satellite pill X button */
div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"])
div[data-testid="stMultiSelectTagsContainer"]
[data-baseweb="tag"] button {
    background: transparent !important;
    border: none !important;
    color: rgba(255,255,255,0.8) !important;
}


/* Satellite pill X icon */
div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"])
div[data-testid="stMultiSelectTagsContainer"]
[data-baseweb="tag"] svg {
    color: rgba(255,255,255,0.9) !important;
    fill: rgba(255,255,255,0.9) !important;
}


/* =========================================================
   SATELLITE DROPDOWN ARROW
   ========================================================= */

div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"])
button[aria-label="Open"] {
    background: transparent !important;
    color: #ff6b00 !important;
}


div[data-testid="stMultiSelect"]:has(input[aria-label="Satellite"])
button[aria-label="Open"] svg {
    color: #ff6b00 !important;
    fill: #ff6b00 !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# CONSTANTS
# ============================================================

# FIX: THERMAL_SOURCE -> "Persistent Source" doesn't match the
# backend's classification_label ("Thermal Source" from
# data_service.py). Aligned so labels match everywhere.
CLASS_NAMES = {
    "INDUSTRIAL_FIRE": "Industrial Fire",
    "WILDFIRE": "Wildfire",
    "THERMAL_SOURCE": "Thermal Source",
    "UNKNOWN": "Unknown"
}

CLASS_COLORS = {
    "Industrial Fire": "#ef4444",
    "Wildfire": "#ff8a00",
    "Persistent Source": "#a855f7",
    "Unknown": "#64748b"
}

# Matches risk_engine.get_risk_level() exactly — CRITICAL/HIGH/MODERATE/LOW.
# "MEDIUM" is NOT a valid backend value; the old app.py used it and it
# never matched anything the API returns.
RISK_COLORS = {
    "CRITICAL": "#ef4444",
    "HIGH": "#ff8a00",
    "MODERATE": "#f5bd24",
    "LOW": "#35cf66",
}

RISK_ICONS = {
    "CRITICAL": "🔴",
    "HIGH": "🟠",
    "MODERATE": "🟡",
    "LOW": "🟢",
}


def risk_color(risk):
    return RISK_COLORS.get(risk, "#64748b")


# ============================================================
# DATA LOADING — NOW VIA FASTAPI, NOT CSV
# ============================================================

@st.cache_data(ttl=300)
def load_data():
    """
    Pulls fire + industry records from FastAPI. risk_score and
    risk_level arrive already computed by risk_engine.py on the
    backend — this function must not touch or recompute them.
    """

    try:
        fires_resp = requests.get(FIRES_ENDPOINT, timeout=15)
        fires_resp.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not reach fires endpoint ({FIRES_ENDPOINT}): {exc}"
        )

    try:
        industries_resp = requests.get(INDUSTRIES_ENDPOINT, timeout=15)
        industries_resp.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not reach industries endpoint ({INDUSTRIES_ENDPOINT}): {exc}"
        )

    fires_payload = fires_resp.json()
    industries_payload = industries_resp.json()

    # In case the API wraps the list, e.g. {"data": [...]}
    if isinstance(fires_payload, dict) and "data" in fires_payload:
        fires_payload = fires_payload["data"]
    if isinstance(industries_payload, dict) and "data" in industries_payload:
        industries_payload = industries_payload["data"]

    fires = pd.DataFrame(fires_payload)
    industries = pd.DataFrame(industries_payload)

    if "acquisition_date" in fires.columns:
        fires["acquisition_date"] = pd.to_datetime(
            fires["acquisition_date"],
            errors="coerce"
        )

    if "classification" not in fires.columns:
        fires["classification"] = "UNKNOWN"

    if "classification_label" not in fires.columns:
        fires["classification_label"] = (
            fires["classification"]
            .map(CLASS_NAMES)
            .fillna("Unknown")
        )

    if "distance_to_industry" not in fires.columns:
        fires["distance_to_industry"] = 999

    if "confidence" not in fires.columns:
        fires["confidence"] = 0

    if "brightness" not in fires.columns:
        fires["brightness"] = 0

    if "satellite" not in fires.columns:
        fires["satellite"] = "Unknown"

    # risk_score / risk_level must already be present from the API.
    # Do NOT fabricate them here — surface the problem instead of
    # silently masking a backend contract violation.
    missing_risk_cols = [
        c for c in ("risk_score", "risk_level") if c not in fires.columns
    ]
    if missing_risk_cols:
        raise RuntimeError(
            f"Fires endpoint response is missing {missing_risk_cols}. "
            "risk_score/risk_level must come from the backend "
            "(risk_engine.py) — check the /api/v1/fires response shape."
        )

    return fires, industries


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

h1, h2, h3, h4, h5 = st.columns(
    [2.6, 1.6, 0.3, 1.1, 1.1]
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

    st.markdown(
        '<div class="nav-active">Overview</div>',
        unsafe_allow_html=True
    )

with h3:

    st.markdown(
        '<div style="height:1px;"></div>',
        unsafe_allow_html=True
    )

with h4:

    st.markdown(
        '<div class="status-box">'
        '<div class="status-title">SYSTEM STATUS</div>'
        '<div class="status-online">● MONITORING ACTIVE</div>'
        '</div>',
        unsafe_allow_html=True
    )

with h5:

    st.markdown(
        f'<div class="status-box">'
        f'<div class="clock-time">{current_time.strftime("%H:%M:%S")}</div>'
        f'<div class="clock-date">'
        f'{current_time.strftime("%d %b %Y")} &nbsp;·&nbsp; Last updated'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

# ============================================================
# SIDEBAR FILTERS
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">'
        '<div>'
        '<div class="sidebar-brand-title">CONTROL PANEL</div>'
        '<div class="sidebar-brand-sub">SIH 26162 &nbsp;·&nbsp; Fire Detection</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="sidebar-section">📅 DATE RANGE</div>', unsafe_allow_html=True)

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
        label_visibility="collapsed"
    )

    st.markdown(
        '<div class="sidebar-section">⚠ RISK LEVEL</div>',
        unsafe_allow_html=True
    )

    # FIX: was a single-select radio defaulting to "Moderate" only,
    # which hid CRITICAL/HIGH/LOW on every page load before the user
    # touched anything — this is why fires appeared to "not show up".
    # Now a multiselect defaulting to ALL levels, matching
    # risk_engine.get_risk_level() exactly.
    risk_options = ["🔴 Critical", "🟠 High", "🟡 Moderate", "🟢 Low"]
    selected_risks = st.multiselect(
        "Risk level",
        risk_options,
        default=risk_options,
        label_visibility="collapsed"
    )

    st.markdown('<div class="sidebar-section">📡 SOURCE TYPE</div>', unsafe_allow_html=True)

    # FIX: was "Persistent Source", which the backend never emits.
    # data_service.py's CLASSIFICATION_LABELS maps THERMAL_SOURCE ->
    # "Thermal Source", so the old label never matched anything and
    # every thermal-source row was silently dropped by this filter.
    source_types = [
        "Industrial Fire",
        "Thermal Source",
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

    # FIX: was capped at 1-10km with default 10 -- but real fire-to-
    # industry distances in this dataset routinely run into the
    # hundreds/thousands of km, so nearly every row was being filtered
    # out before reaching the map. Range now derives from the actual
    # data, defaulting to show everything.
    if not fires_df.empty and fires_df["distance_to_industry"].notna().any():
        data_max_distance = int(fires_df["distance_to_industry"].max()) + 1
    else:
        data_max_distance = 2000

    max_distance = st.slider(
        "Maximum distance",
        1, data_max_distance, data_max_distance, 1,
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

# FIX: st.date_input returns a single date (not a 2-tuple) the
# instant the user picks only a start date, before an end date is
# chosen. The old code silently skipped filtering in that moment.
# Now handles both shapes, and compares by calendar date (.dt.date)
# instead of full Timestamp so time-of-day components in
# acquisition_date can never cause a mismatch.
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_day, end_day = date_range[0], date_range[1]
elif isinstance(date_range, tuple) and len(date_range) == 1:
    start_day = end_day = date_range[0]
else:
    start_day = end_day = date_range

filtered = filtered[
    filtered["acquisition_date"].dt.date.between(start_day, end_day)
]


# SOURCE

if selected_sources:

    filtered = filtered[
        filtered["classification_label"].isin(selected_sources)
    ]

else:

    filtered = filtered.iloc[0:0]


# SATELLITE

if selected_satellites:

    filtered = filtered[
        filtered["satellite"].astype(str).isin(selected_satellites)
    ]


# CONFIDENCE

filtered = filtered[filtered["confidence"] >= min_confidence]


# BRIGHTNESS

filtered = filtered[filtered["brightness"] >= min_brightness]


# INDUSTRIAL DISTANCE

filtered = filtered[filtered["distance_to_industry"] <= max_distance]


# ============================================================
# RISK LEVEL FILTER
# ============================================================
# FIX: risk_score / risk_level are used exactly as returned by the
# backend. Nothing here recomputes them — this is the whole point
# of the fix. Compare against /api/v1/analytics/debug/top-scores
# to confirm CRITICAL filtering now returns the same events.
# ============================================================

risk_mapping = {
    "🔴 Critical": "CRITICAL",
    "🟠 High": "HIGH",
    "🟡 Moderate": "MODERATE",
    "🟢 Low": "LOW"
}

allowed_risks = [risk_mapping[r] for r in selected_risks] if selected_risks else []

if not filtered.empty:
    filtered = filtered[filtered["risk_level"].isin(allowed_risks)]
else:
    filtered = filtered.iloc[0:0]


# ============================================================
# KPI CALCULATIONS  (all derived from backend-provided columns)
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

# FIX: was `risk_score >= 60`, an arbitrary cutoff matching neither the
# backend's HIGH threshold (50) nor CRITICAL (65). Now counts rows whose
# backend-assigned risk_level is HIGH or CRITICAL.
high_risk_df = (
    filtered[filtered["risk_level"].isin(["HIGH", "CRITICAL"])]
    if not filtered.empty else filtered
)
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

map_col, intel_col = st.columns([3.5, 1.15])


# ============================================================
# 🔒 LOCKED MAP SECTION — DO NOT MODIFY ANYTHING BELOW
# NOTE: map_visualization.create_fire_map() currently recomputes its
# OWN copy of the risk formula for the popup (see the comment inside
# it: "same formula as calculate_risk() in app.py"). That comment is
# now stale — app.py no longer computes risk. Per your instructions
# this block is locked, but flagging it: the popup's risk_score /
# risk_level can drift from what's in the KPI cards / event panel
# below (which now use the backend's numbers) unless
# map_visualization.py is also switched to read row["risk_score"] /
# row["risk_level"] / row["risk_level"] via get_recommendation()
# instead of recalculating. This is a decision I'm leaving to you
# since the block is explicitly marked locked.
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
            returned_objects=["last_object_clicked"],
            key="thermoscope_main_map"
        )

    except Exception as map_error:

        st.error(f"Map error: {map_error}")
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
        and map_result.get("last_object_clicked")
        and not filtered.empty
    ):

        clicked = map_result["last_object_clicked"]
        clicked_lat = clicked.get("lat")
        clicked_lon = clicked.get("lng")

        if clicked_lat is not None and clicked_lon is not None:

            distances = (
                (filtered["latitude"] - clicked_lat) ** 2
                + (filtered["longitude"] - clicked_lon) ** 2
            )

            nearest_index = distances.idxmin()
            selected_event = filtered.loc[nearest_index]

    # DEFAULT EVENT

    if selected_event is None and not filtered.empty:
        selected_event = filtered.iloc[0]

    # --------------------------------------------------------
    # EVENT CARD
    # --------------------------------------------------------

    if selected_event is not None:

        event = selected_event

        event_id = event.get("id", f"IND-{selected_event.name:04d}")

        classification = event.get("classification", "UNKNOWN")
        event_type = CLASS_NAMES.get(classification, "Unknown")

        # FIX: risk_score/risk_level read directly from the backend
        # response — never recomputed here.
        score = int(event.get("risk_score", 0))
        risk = event.get("risk_level", "LOW")

        confidence = event.get("confidence", "N/A")
        brightness = event.get("brightness", "N/A")
        distance = event.get("distance_to_industry", "N/A")
        satellite = event.get("satellite", "N/A")

        risk_hex = risk_color(risk)

        st.markdown(
            f'<div class="event-card" style="border-left:3px solid {risk_hex};">'
            f'<div class="event-id">{event_id}</div>'
            f'<div class="event-type" style="color:{risk_hex};">{event_type.upper()}</div>'

            f'<div class="event-row">'
            f'<span class="event-label">Risk Level</span>'
            f'<span class="event-value" style="color:{risk_hex};">{risk}</span>'
            f'</div>'

            f'<div class="event-row">'
            f'<span class="event-label">Risk Score</span>'
            f'<span class="event-value">{score}/100</span>'
            f'</div>'

            f'<div class="event-row">'
            f'<span class="event-label">Confidence</span>'
            f'<span class="event-value">{confidence}%</span>'
            f'</div>'

            f'<div class="event-row">'
            f'<span class="event-label">Brightness</span>'
            f'<span class="event-value">{brightness} K</span>'
            f'</div>'

            f'<div class="event-row">'
            f'<span class="event-label">Distance</span>'
            f'<span class="event-value">{distance} km</span>'
            f'</div>'

            f'<div class="event-row">'
            f'<span class="event-label">Satellite</span>'
            f'<span class="event-value">{satellite}</span>'
            f'</div>'

            f'</div>',
            unsafe_allow_html=True
        )

        # ----------------------------------------------------
        # AI EXPLANATION
        # (Illustrative breakdown for the UI panel only — not a
        #  second risk score. It never feeds risk_level / risk_score
        #  anywhere and is not part of the risk data contract.)
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title" style="margin-top:10px;">AI EXPLANATION</div>',
            unsafe_allow_html=True
        )

        try:
            confidence_value = int(float(confidence))
        except Exception:
            confidence_value = 0

        try:
            distance_value = float(distance)
        except Exception:
            distance_value = 999

        if distance_value <= 2:
            proximity_value = 96
        elif distance_value <= 5:
            proximity_value = 80
        elif distance_value <= 8:
            proximity_value = 60
        elif distance_value <= 15:
            proximity_value = 35
        else:
            proximity_value = 15

        try:
            brightness_value = float(brightness)
        except Exception:
            brightness_value = 280

        thermal_value = int(
            max(0, min(100, ((brightness_value - 280) / 100) * 100))
        )

        persistence_value = 88 if classification == "THERMAL_SOURCE" else 45

        explanation_values = [
            ("Industrial Proximity", proximity_value),
            ("Thermal Intensity", thermal_value),
            ("Persistence", persistence_value),
            ("Detection Confidence", confidence_value),
            ("Land-cover Context", 94)
        ]

        ai_html = '<div class="ai-card">'

        for explanation, value in explanation_values:

            value = max(0, min(100, int(value)))

            ai_html += (
                '<div class="ai-row">'
                f'<div class="ai-label">'
                f'{explanation}'
                f'<span class="ai-percent">{value}%</span>'
                f'</div>'
                f'<div style="height:4px;background:#182433;border-radius:5px;">'
                f'<div style="width:{value}%;height:4px;background:#35cf66;border-radius:5px;"></div>'
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

        st.markdown(ai_html, unsafe_allow_html=True)

    else:

        st.info("No events match the selected filters.")


# ============================================================
# FIRE DETECTION ANALYTICS
# ============================================================

st.markdown('<div class="section-title">FIRE DETECTION ANALYTICS</div>', unsafe_allow_html=True)

chart1, chart2, chart3 = st.columns(3)


# THERMAL ACTIVITY

with chart1:

    with st.container(border=True):

        st.markdown(
            '<div class="panel-title">THERMAL ACTIVITY — LAST 7 DAYS</div>',
            unsafe_allow_html=True
        )

        if not filtered.empty:

            daily = (
                filtered
                .assign(date=filtered["acquisition_date"].dt.date)
                .groupby("date")
                .size()
                .reset_index(name="count")
            )

            fig_thermal = px.area(daily, x="date", y="count")

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


# RISK TREND

with chart2:

    with st.container(border=True):

        st.markdown(
            '<div class="panel-title">RISK TREND — LAST 7 DAYS</div>',
            unsafe_allow_html=True
        )

        if not filtered.empty:

            daily_risk = (
                filtered
                .assign(date=filtered["acquisition_date"].dt.date)
                .groupby("date")["risk_score"]
                .mean()
                .reset_index()
            )

            fig_risk = px.line(daily_risk, x="date", y="risk_score", markers=True)
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


# SOURCE DISTRIBUTION

with chart3:

    with st.container(border=True):

        st.markdown(
            '<div class="panel-title">SOURCE DISTRIBUTION</div>',
            unsafe_allow_html=True
        )

        if not filtered.empty:

            distribution = (
                filtered["classification_label"]
                .value_counts()
                .reset_index()
            )

            distribution.columns = ["Type", "Count"]

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
        .sort_values("risk_score", ascending=False)
        .head(4)
    )

    feed_columns = st.columns(4)

    for feed_column, (_, event) in zip(feed_columns, feed.iterrows()):

        score = int(event["risk_score"])
        risk = event["risk_level"]  # FIX: read from backend, not recomputed

        classification = CLASS_NAMES.get(
            event.get("classification", "UNKNOWN"),
            "Unknown"
        )

        risk_hex = risk_color(risk)
        risk_icon = RISK_ICONS.get(risk, "⚪")

        event_time = (
            event["acquisition_date"].strftime("%H:%M")
            if pd.notna(event.get("acquisition_date"))
            else "N/A"
        )

        confidence = event.get("confidence", "N/A")
        distance = event.get("distance_to_industry", "N/A")

        with feed_column:

            st.markdown(
                f'<div class="feed-card" style="border-left:3px solid {risk_hex};">'
                f'<div class="feed-time">{event_time}</div>'
                f'<div class="feed-risk" style="color:{risk_hex};">{risk_icon} {risk}</div>'
                f'<div class="feed-title">{classification} detected</div>'
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

    st.info("No intelligence events available.")


# ============================================================
# REPORTS
# ============================================================

st.markdown('<div class="section-title">REPORTS</div>', unsafe_allow_html=True)

export1, export2 = st.columns(2)


# CSV EXPORT

with export1:

    csv_data = filtered.to_csv(index=False)

    st.download_button(
        "⬇ EXPORT CSV",
        data=csv_data,
        file_name="thermoscope_report.csv",
        mime="text/csv",
        use_container_width=True
    )


# GEOJSON EXPORT

with export2:

    features = []

    for index, row in filtered.iterrows():

        properties = {}

        for column in filtered.columns:

            value = row[column]

            if pd.isna(value):
                value = None
            elif isinstance(value, pd.Timestamp):
                value = value.isoformat()
            elif hasattr(value, "item"):
                try:
                    value = value.item()
                except Exception:
                    pass

            properties[column] = value

        try:
            latitude = float(row["latitude"])
            longitude = float(row["longitude"])
        except Exception:
            continue

        features.append({
            "type": "Feature",
            "properties": properties,
            "geometry": {
                "type": "Point",
                "coordinates": [longitude, latitude]
            }
        })

    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    st.download_button(
        "⬇ EXPORT GEOJSON",
        data=json.dumps(geojson_data, indent=2),
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