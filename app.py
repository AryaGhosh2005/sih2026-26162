"""
app.py

SIH 26162 - Industrial Fire Detection System

Streamlit dashboard for:
- Thermal anomaly monitoring
- Industrial fire detection
- Filtering
- Risk assessment
- Map visualization
- Analytics
- CSV / GeoJSON export
"""

import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from streamlit_folium import st_folium

from map_visualization import (
    create_fire_map,
    CLASS_COLORS,
    CLASS_LABELS
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Industrial Fire Detection System",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>

#MainMenu,
footer,
header,
.stDeployButton {
    visibility: hidden;
}

.stApp {
    background: #080b12;
}

.block-container {
    padding-top: 55px;
    padding-left: 1rem;
    padding-right: 1rem;
    max-width: 100%;
}

/* -------------------------------------------------------
   Header
------------------------------------------------------- */

.dashboard-header {
    background: rgba(15, 18, 28, 0.95);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;

    padding: 12px 18px;
    margin-bottom: 10px;

    display: flex;
    align-items: center;
    justify-content: space-between;
}

.header-title {
    color: white;
    font-size: 19px;
    font-weight: 700;
}

.header-subtitle {
    color: #8b93a7;
    font-size: 11px;
    margin-top: 2px;
}

.live-status {
    color: #ff3b30;
    font-size: 11px;
    font-weight: 700;
}

.live-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    background: #ff0000;
    border-radius: 50%;
    margin-right: 5px;
    box-shadow: 0 0 8px #ff0000;
}

/* -------------------------------------------------------
   Section headings
------------------------------------------------------- */

.section-title {
    color: #dce1ea;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-top: 10px;
    margin-bottom: 8px;
}

/* -------------------------------------------------------
   Selected event card
------------------------------------------------------- */

.event-card {
    background: rgba(12, 16, 25, 0.96);

    border: 1px solid rgba(255,0,0,0.25);

    border-left: 3px solid #FF0000;

    border-radius: 10px;

    padding: 14px;

    margin-top: 8px;

    color: white;
}

.event-title {
    color: #FF0000;
    font-size: 13px;
    font-weight: 800;
}

.event-status {
    color: #ffb3b3;
    font-size: 10px;
    font-weight: 700;
    margin-top: 2px;
    margin-bottom: 10px;
}

.event-row {
    display: flex;
    justify-content: space-between;

    border-bottom: 1px solid rgba(255,255,255,0.06);

    padding: 5px 0;

    font-size: 11px;
}

.event-key {
    color: #788195;
}

.event-value {
    color: #f2f4f8;
    font-weight: 600;
}

/* -------------------------------------------------------
   Metric cards
------------------------------------------------------- */

.metric-card {
    background: rgba(14,18,28,0.9);

    border: 1px solid rgba(255,255,255,0.07);

    border-radius: 8px;

    padding: 10px;

    text-align: center;
}

.metric-label {
    color: #788195;
    font-size: 10px;
}

.metric-value {
    color: white;
    font-size: 22px;
    font-weight: 700;
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# DATA LOADING
# =========================================================

@st.cache_data(ttl=300)
def load_data():

    fires_path = "data/classified_fires.csv"
    industries_path = "data/industries.csv"

    if not os.path.exists(fires_path):
        raise FileNotFoundError(
            "classified_fires.csv not found. "
            "Run classifier.py first."
        )

    if not os.path.exists(industries_path):
        raise FileNotFoundError(
            "industries.csv not found. "
            "Run data_generator.py first."
        )

    fires = pd.read_csv(fires_path)

    industries = pd.read_csv(industries_path)

    # -----------------------------------------------------
    # Date
    # -----------------------------------------------------

    if "acquisition_date" in fires.columns:

        fires["acquisition_date"] = pd.to_datetime(
            fires["acquisition_date"],
            errors="coerce"
        )

    # -----------------------------------------------------
    # Contract classification labels
    # -----------------------------------------------------

    fires["classification_label"] = (
        fires["classification"]
        .map(CLASS_LABELS)
        .fillna("Unknown")
    )

    # -----------------------------------------------------
    # Contract field compatibility
    # -----------------------------------------------------

    if (
        "distance_to_industry" not in fires.columns
        and "distance_to_industry_km" in fires.columns
    ):

        fires["distance_to_industry"] = (
            fires["distance_to_industry_km"]
        )

    return fires, industries


# =========================================================
# RISK SCORE
# =========================================================

def calculate_risk(row):
    """
    Transparent prototype risk score.

    Uses only fields currently available:
    - Brightness
    - Confidence
    - Distance to industry
    - Classification
    """

    brightness = float(
        row.get("brightness", 0)
    )

    confidence = float(
        row.get("confidence", 0)
    )

    distance = float(
        row.get("distance_to_industry", 999)
    )

    classification = row.get(
        "classification",
        "UNKNOWN"
    )

    # Brightness component
    brightness_score = (
        (brightness - 280) / 100
    ) * 40

    brightness_score = max(
        0,
        min(40, brightness_score)
    )

    # Confidence component
    confidence_score = (
        confidence / 100
    ) * 30

    # Industry proximity
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

    # Industrial fires receive a small priority boost
    if classification == "INDUSTRIAL_FIRE":
        score += 5

    return int(
        max(
            0,
            min(100, round(score))
        )
    )


def risk_level(score):

    if score >= 80:
        return "CRITICAL"

    if score >= 60:
        return "HIGH"

    if score >= 40:
        return "MODERATE"

    return "LOW"


# =========================================================
# FILTERING
# =========================================================

def apply_filters(
    df,
    date_range,
    selected_types,
    selected_satellites,
    min_brightness,
    min_confidence,
    max_distance
):

    filtered = df.copy()

    # Date
    if (
        "acquisition_date" in filtered.columns
        and date_range
        and len(date_range) == 2
    ):

        start_date = pd.to_datetime(
            date_range[0]
        )

        end_date = pd.to_datetime(
            date_range[1]
        )

        filtered = filtered[
            (
                filtered["acquisition_date"]
                >= start_date
            )
            &
            (
                filtered["acquisition_date"]
                <= end_date
            )
        ]

    # Classification
    if selected_types:

        filtered = filtered[
            filtered["classification_label"]
            .isin(selected_types)
        ]

    # Satellite
    if selected_satellites:

        filtered = filtered[
            filtered["satellite"]
            .isin(selected_satellites)
        ]

    # Brightness
    if min_brightness is not None:

        filtered = filtered[
            filtered["brightness"]
            >= min_brightness
        ]

    # Confidence
    if min_confidence is not None:

        filtered = filtered[
            filtered["confidence"]
            >= min_confidence
        ]

    # Distance
    if max_distance is not None:

        filtered = filtered[
            filtered["distance_to_industry"]
            <= max_distance
        ]

    return filtered


# =========================================================
# GEOJSON EXPORT
# =========================================================

def dataframe_to_geojson(df):

    features = []

    for index, row in df.iterrows():

        properties = {}

        for column in df.columns:

            value = row[column]

            if pd.isna(value):
                value = None

            elif isinstance(
                value,
                pd.Timestamp
            ):

                value = value.strftime(
                    "%Y-%m-%d"
                )

            elif hasattr(
                value,
                "item"
            ):

                value = value.item()

            properties[column] = value

        feature = {
            "type": "Feature",
            "properties": properties,
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(row["longitude"]),
                    float(row["latitude"])
                ]
            }
        }

        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }


# =========================================================
# MAIN
# =========================================================

def main():

    # =====================================================
    # HEADER
    # =====================================================

    header_left, header_right = st.columns([3, 1])

    with header_left:
        st.markdown(
            """
            <div class="header-title">
                🔥 Industrial Fire Detection
            </div>
            <div class="header-subtitle">
                AI-Driven Thermal Intelligence Platform
            </div>
            """,
            unsafe_allow_html=True
        )

    with header_right:
        st.markdown(
            "🔴 **LIVE**　 NASA FIRMS　 SIH 26162"
        )

    # -----------------------------------------------------
    # Load data
    # -----------------------------------------------------

    try:

        fires_df, industries_df = load_data()

    except Exception as e:

        st.error(str(e))

        st.stop()

    if fires_df.empty:

        st.warning(
            "No classified fire data available."
        )

        st.stop()

    # =====================================================
    # SIDEBAR FILTERS
    # =====================================================

    with st.sidebar:

        st.markdown(
            "### 🔍 FILTERS"
        )

        # -------------------------------------------------
        # Date
        # -------------------------------------------------

        st.caption("DATE RANGE")

        min_date = (
            fires_df["acquisition_date"]
            .min()
            .date()
        )

        max_date = (
            fires_df["acquisition_date"]
            .max()
            .date()
        )

        date_range = st.date_input(
            "Date",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed"
        )

        # -------------------------------------------------
        # Classification
        # -------------------------------------------------

        st.caption("CLASSIFICATION")

        classification_options = [
            "Industrial Fire",
            "Wildfire",
            "Thermal Source",
            "Unknown"
        ]

        selected_types = st.multiselect(
            "Classification",
            options=classification_options,
            default=classification_options,
            label_visibility="collapsed"
        )

        # -------------------------------------------------
        # Satellite
        # -------------------------------------------------

        st.caption("SATELLITE")

        satellites = sorted(
            fires_df["satellite"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_satellites = st.multiselect(
            "Satellite",
            options=satellites,
            default=satellites,
            label_visibility="collapsed"
        )

        # -------------------------------------------------
        # Brightness
        # -------------------------------------------------

        st.caption("MINIMUM BRIGHTNESS")

        min_brightness = st.slider(
            "Brightness",
            min_value=280,
            max_value=380,
            value=280,
            step=5,
            format="%d K",
            label_visibility="collapsed"
        )

        # -------------------------------------------------
        # Confidence
        # -------------------------------------------------

        st.caption("MINIMUM CONFIDENCE")

        min_confidence = st.slider(
            "Confidence",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            format="%d%%",
            label_visibility="collapsed"
        )

        # -------------------------------------------------
        # Distance
        # -------------------------------------------------

        st.caption(
            "MAX DISTANCE TO INDUSTRY"
        )

        max_distance = st.slider(
            "Distance",
            min_value=1,
            max_value=50,
            value=50,
            step=1,
            format="%d km",
            label_visibility="collapsed"
        )

        st.divider()

        st.caption("FILTER ACTIONS")

        apply_button = st.button(
            "APPLY FILTERS",
            use_container_width=True
        )

        reset_button = st.button(
            "RESET",
            use_container_width=True
        )

    # =====================================================
    # APPLY FILTERS
    # =====================================================

    filtered_df = apply_filters(
        fires_df,
        date_range,
        selected_types,
        selected_satellites,
        min_brightness,
        min_confidence,
        max_distance
    )

    # =====================================================
    # MAP
    # =====================================================

    st.markdown(
        '<div class="section-title">🗺️ THERMAL MONITORING MAP</div>',
        unsafe_allow_html=True
    )

    fire_map = create_fire_map(
        filtered_df,
        industries_df
    )

    map_data = st_folium(
        fire_map,
        width=None,
        height=700,
        returned_objects=[
            "last_object_clicked"
        ]
    )

    # =====================================================
    # SELECTED EVENT
    # =====================================================

    selected_event = None

    if (
        map_data
        and map_data.get(
            "last_object_clicked"
        )
        and not filtered_df.empty
    ):

        clicked = map_data[
            "last_object_clicked"
        ]

        clicked_lat = clicked.get(
            "lat"
        )

        clicked_lon = clicked.get(
            "lng"
        )

        if (
            clicked_lat is not None
            and clicked_lon is not None
        ):

            # Find closest anomaly to click
            distances = (
                (
                    filtered_df["latitude"]
                    - clicked_lat
                ) ** 2
                +
                (
                    filtered_df["longitude"]
                    - clicked_lon
                ) ** 2
            )

            nearest_index = distances.idxmin()

            selected_event = (
                filtered_df.loc[
                    nearest_index
                ]
            )

    # =====================================================
    # EVENT PANEL
    # =====================================================

    if selected_event is not None:

        event = selected_event

        classification = event.get(
            "classification",
            "UNKNOWN"
        )

        color = CLASS_COLORS.get(
            classification,
            "#0066CC"
        )

        risk_score = calculate_risk(
            event
        )

        risk = risk_level(
            risk_score
        )

        distance = event.get(
            "distance_to_industry",
            "N/A"
        )

        st.markdown(
            f"""
            <div class="event-card" style="border-left-color:{color};border-color:{color}40;">

                <div class="event-title"
                     style="color:{color};">

                    {CLASS_LABELS.get(
                        classification,
                        "Unknown"
                    ).upper()}

                </div>

                <div class="event-status">
                    ● {risk} PRIORITY
                </div>

                <div class="event-row">
                    <span class="event-key">
                        Alert ID
                    </span>
                    <span class="event-value">
                        IND_{selected_event.name:04d}
                    </span>
                </div>

                <div class="event-row">
                    <span class="event-key">
                        Facility
                    </span>
                    <span class="event-value">
                        {event.get(
                            "nearest_industry",
                            "Unknown"
                        )}
                    </span>
                </div>

                <div class="event-row">
                    <span class="event-key">
                        Industry Type
                    </span>
                    <span class="event-value">
                        {event.get(
                            "industry_type",
                            "Unknown"
                        )}
                    </span>
                </div>

                <div class="event-row">
                    <span class="event-key">
                        Risk Score
                    </span>
                    <span class="event-value">
                        {risk_score}/100 ({risk})
                    </span>
                </div>

                <div class="event-row">
                    <span class="event-key">
                        Confidence
                    </span>
                    <span class="event-value">
                        {event.get(
                            "confidence",
                            "N/A"
                        )}%
                    </span>
                </div>

                <div class="event-row">
                    <span class="event-key">
                        Brightness
                    </span>
                    <span class="event-value">
                        {event.get(
                            "brightness",
                            "N/A"
                        )} K
                    </span>
                </div>

                <div class="event-row">
                    <span class="event-key">
                        Satellite
                    </span>
                    <span class="event-value">
                        {event.get(
                            "satellite",
                            "N/A"
                        )}
                    </span>
                </div>

                <div class="event-row">
                    <span class="event-key">
                        Distance
                    </span>
                    <span class="event-value">
                        {distance} km
                    </span>
                </div>

                <div class="event-row">
                    <span class="event-key">
                        Coordinates
                    </span>
                    <span class="event-value">
                        {event["latitude"]:.4f},
                        {event["longitude"]:.4f}
                    </span>
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # =====================================================
    # ANALYTICS
    # =====================================================

    st.markdown(
        '<div class="section-title">📊 ANALYTICS</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    total = len(filtered_df)

    industrial = len(
        filtered_df[
            filtered_df["classification"]
            == "INDUSTRIAL_FIRE"
        ]
    )

    wildfire = len(
        filtered_df[
            filtered_df["classification"]
            == "WILDFIRE"
        ]
    )

    thermal = len(
        filtered_df[
            filtered_df["classification"]
            == "THERMAL_SOURCE"
        ]
    )

    unknown = len(
        filtered_df[
            filtered_df["classification"]
            == "UNKNOWN"
        ]
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("🔥 Total Alerts", total)
    c2.metric("🏭 Industrial", industrial)
    c3.metric("🌲 Wildfires", wildfire)
    c4.metric("♨️ Thermal", thermal)
    c5.metric("❓ Unknown", unknown)

    # =====================================================
    # CHARTS
    # =====================================================

    if not filtered_df.empty:

        chart1, chart2 = st.columns(2)

        # -------------------------------------------------
        # Fires by type
        # -------------------------------------------------

        with chart1:

            st.markdown(
                "**Fires by Type**"
            )

            counts = (
                filtered_df[
                    "classification_label"
                ]
                .value_counts()
                .reset_index()
            )

            counts.columns = [
                "Type",
                "Count"
            ]

            color_map = {
            "Industrial Fire": "#ef4444",
            "Wildfire": "#ff8a00",
            "Thermal Source": "#a855f7",
            "Unknown": "#64748b"
            }

            fig = px.pie(
                counts,
                values="Count",
                names="Type",
                hole=0.55,
                color="Type",
                color_discrete_map=color_map
            )

            fig.update_layout(
                height=330,
                margin=dict(
                    l=10,
                    r=10,
                    t=20,
                    b=10
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    color="#dce1ea"
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # -------------------------------------------------
        # Daily trend
        # -------------------------------------------------

        with chart2:

            st.markdown(
                "**Daily Detection Trend**"
            )

            daily = (
                filtered_df
                .groupby(
                    filtered_df[
                        "acquisition_date"
                    ].dt.date
                )
                .size()
                .reset_index(
                    name="Count"
                )
            )

            daily.columns = [
                "Date",
                "Count"
            ]

            fig2 = px.line(
                daily,
                x="Date",
                y="Count",
                markers=True
            )

            fig2.update_traces(
                line=dict(
                    color="#FF0000",
                    width=2
                ),
                marker=dict(
                    size=5
                )
            )

            fig2.update_layout(
                height=330,
                margin=dict(
                    l=10,
                    r=10,
                    t=20,
                    b=10
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    color="#dce1ea"
                )
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

    # =====================================================
    # EXPORT
    # =====================================================

    st.markdown(
        '<div class="section-title">⬇️ EXPORT</div>',
        unsafe_allow_html=True
    )

    export1, export2 = st.columns(2)

    # -----------------------------------------------------
    # CSV
    # -----------------------------------------------------

    with export1:

        csv_data = filtered_df.to_csv(
            index=False
        )

        st.download_button(
            "⬇️ EXPORT CSV",
            data=csv_data,
            file_name=(
                f"thermal_anomalies_"
                f"{datetime.now().strftime('%Y%m%d')}.csv"
            ),
            mime="text/csv",
            use_container_width=True
        )

    # -----------------------------------------------------
    # GeoJSON
    # -----------------------------------------------------

    with export2:

        geojson_data = dataframe_to_geojson(
            filtered_df
        )

        import json

        geojson_string = json.dumps(
            geojson_data,
            indent=2
        )

        st.download_button(
            "⬇️ EXPORT GEOJSON",
            data=geojson_string,
            file_name=(
                f"thermal_anomalies_"
                f"{datetime.now().strftime('%Y%m%d')}.geojson"
            ),
            mime="application/geo+json",
            use_container_width=True
        )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()