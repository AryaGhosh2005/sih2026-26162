"""
map_visualization.py

Professional thermal anomaly map for SIH 26162.

Features:
- Satellite map by default
- OpenStreetMap layer
- Pulsing thermal hotspots
- Contract-compliant classification colors
- Heatmap layer
- Industrial facility layer
- Map legend
- Fullscreen
- Layer controls
"""

import pandas as pd
import folium
from folium import plugins
from branca.element import Element


# =========================================================
# CONTRACT COLORS
# =========================================================

CLASS_COLORS = {
    "INDUSTRIAL_FIRE": "#FF0000",
    "WILDFIRE": "#FF8C00",
    "THERMAL_SOURCE": "#00CC00",
    "UNKNOWN": "#0066CC"
}


CLASS_LABELS = {
    "INDUSTRIAL_FIRE": "Industrial Fire",
    "WILDFIRE": "Wildfire",
    "THERMAL_SOURCE": "Thermal Source",
    "UNKNOWN": "Unknown"
}


# =========================================================
# CREATE MAP
# =========================================================

def create_fire_map(
    industrial_fires_df,
    industries_df=None
):
    """
    Create the main thermal anomaly intelligence map.
    """

    # -----------------------------------------------------
    # Determine map center
    # -----------------------------------------------------

    if (
        industrial_fires_df is not None
        and not industrial_fires_df.empty
    ):

        center_lat = industrial_fires_df["latitude"].mean()
        center_lon = industrial_fires_df["longitude"].mean()

        zoom = 5

    else:

        center_lat = 20.5937
        center_lon = 78.9629

        zoom = 5


    # -----------------------------------------------------
    # Base map
    # -----------------------------------------------------

    m = folium.Map(
        location=[
            center_lat,
            center_lon
        ],
        zoom_start=zoom,
        control_scale=True,
        tiles=None
    )


    # -----------------------------------------------------
    # Satellite - DEFAULT
    # -----------------------------------------------------

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite",
        overlay=False,
        control=True
    ).add_to(m)


    # -----------------------------------------------------
    # OpenStreetMap
    # -----------------------------------------------------

    folium.TileLayer(
        tiles="OpenStreetMap",
        name="Street Map",
        overlay=False,
        control=True
    ).add_to(m)


    # -----------------------------------------------------
    # Facility layer
    # -----------------------------------------------------

    if (
        industries_df is not None
        and not industries_df.empty
    ):

        facility_group = folium.FeatureGroup(
            name="Industrial Facilities",
            show=True
        )

        for _, row in industries_df.iterrows():

            name = row.get(
                "name",
                "Facility"
            )

            industry_type = row.get(
                "type",
                "Industrial Facility"
            )

            popup_html = f"""
            <div style="
                font-family:Segoe UI,sans-serif;
                min-width:190px;
            ">

                <div style="
                    font-size:13px;
                    font-weight:700;
                    margin-bottom:6px;
                ">
                    INDUSTRIAL FACILITY
                </div>

                <div style="font-size:11px;">
                    <b>Name:</b> {name}<br>
                    <b>Type:</b> {industry_type}
                </div>

            </div>
            """

            folium.CircleMarker(
                location=[
                    row["latitude"],
                    row["longitude"]
                ],
                radius=4,
                color="#FFFFFF",
                weight=1,
                fill=True,
                fill_color="#444444",
                fill_opacity=0.75,
                popup=folium.Popup(
                    popup_html,
                    max_width=240
                ),
                tooltip=name
            ).add_to(facility_group)

        facility_group.add_to(m)


    # -----------------------------------------------------
    # Fire / anomaly layer
    # -----------------------------------------------------

    fire_group = folium.FeatureGroup(
        name="Thermal Anomalies",
        show=True
    )

    heat_points = []


    if (
        industrial_fires_df is not None
        and not industrial_fires_df.empty
    ):

        for index, row in industrial_fires_df.iterrows():

            classification = row.get(
                "classification",
                "UNKNOWN"
            )

            color = CLASS_COLORS.get(
                classification,
                CLASS_COLORS["UNKNOWN"]
            )

            label = CLASS_LABELS.get(
                classification,
                "Unknown"
            )

            latitude = float(
                row["latitude"]
            )

            longitude = float(
                row["longitude"]
            )

            brightness = row.get(
                "brightness",
                "N/A"
            )

            confidence = row.get(
                "confidence",
                "N/A"
            )

            distance = row.get(
                "distance_to_industry",
                "N/A"
            )

            facility = row.get(
                "nearest_industry",
                "Unknown"
            )


            # -------------------------------------------------
            # Risk score + contribution breakdown
            # (read directly from backend-generated DataFrame)
            # -------------------------------------------------

            brightness_pts = row.get(
                "brightness_score",
                0
            )

            confidence_pts = row.get(
                "confidence_score",
                0
            )

            proximity_pts = row.get(
                "proximity_score",
                0
            )

            industrial_pts = row.get(
                "classification_bonus",
                0
            )

            risk_score = row.get(
                "risk_score",
                0
            )

            risk_level = row.get(
                "risk_level",
                "LOW"
            )

            if risk_level == "CRITICAL":
                risk_level_color = "#ef4444"

            elif risk_level == "HIGH":
                risk_level_color = "#ff8a00"

            elif risk_level == "MODERATE":
                risk_level_color = "#f5bd24"

            else:
                risk_level_color = "#35cf66"


            # -------------------------------------------------
            # Display helpers for popup
            # -------------------------------------------------

            brightness_pts_display = int(brightness_pts)
            confidence_pts_display = int(confidence_pts)
            proximity_pts_display = int(proximity_pts)

            _recommendations = {
                "CRITICAL": "Immediate emergency response required. Evacuate personnel and alert fire services.",
                "HIGH": "Urgent inspection needed. Notify facility management and local authorities.",
                "MODERATE": "Schedule on-site inspection within 24 hours. Increase monitoring frequency.",
                "LOW": "Continue routine monitoring. Log for periodic review."
            }
            recommendation = _recommendations.get(risk_level, "Continue routine monitoring.")


            # -------------------------------------------------
            # Heatmap data
            # -------------------------------------------------

            try:

                intensity = max(
                    0.2,
                    min(
                        1.0,
                        (float(brightness) - 280) / 100
                    )
                )

            except:

                intensity = 0.5


            heat_points.append([
                latitude,
                longitude,
                intensity
            ])


            # -------------------------------------------------
            # PREMIUM GLASS POPUP
            # -------------------------------------------------

            popup_html = f"""

            <style>

                /* =========================================
                   REMOVE DEFAULT LEAFLET WHITE POPUP
                   ========================================= */

                .leaflet-popup-content-wrapper {{
                    background: transparent !important;
                    box-shadow: none !important;
                    padding: 0 !important;
                    border-radius: 16px !important;
                }}

                .leaflet-popup-content {{
                    margin: 0 !important;
                    padding: 0 !important;
                    width: auto !important;
                }}

                .leaflet-popup-tip {{
                    background: rgba(8, 13, 24, 0.97) !important;
                    box-shadow: none !important;
                }}


                /* =========================================
                   CLOSE BUTTON
                   ========================================= */

                .leaflet-popup-close-button {{
                    color: #ffffff !important;

                    background:
                        rgba(10, 15, 27, 0.92) !important;

                    border:
                        1px solid rgba(255,255,255,0.14) !important;

                    border-radius: 50% !important;

                    width: 23px !important;
                    height: 23px !important;

                    line-height: 21px !important;

                    font-size: 16px !important;
                    font-weight: 700 !important;

                    right: 8px !important;
                    top: 8px !important;

                    z-index: 50 !important;

                    box-shadow:
                        0 3px 12px rgba(0,0,0,0.5) !important;
                }}

                .leaflet-popup-close-button:hover {{
                    background:
                        rgba(255,255,255,0.12) !important;

                    color: #ffffff !important;
                }}


                /* =========================================
                   MAIN POPUP
                   ========================================= */

                .thermal-glass-popup {{

                    position: relative;

                    width: 270px;

                    overflow: hidden;

                    background:
                        linear-gradient(
                            145deg,
                            rgba(20,27,42,0.96),
                            rgba(6,11,20,0.98)
                        );

                    border:
                        1px solid rgba(255,255,255,0.13);

                    border-left:
                        3px solid {color};

                    border-radius:
                        16px;

                    box-shadow:
                        0 14px 38px rgba(0,0,0,0.60),
                        0 0 18px {color}55,
                        inset 0 1px 0 rgba(255,255,255,0.10);

                    backdrop-filter:
                        blur(14px);

                    -webkit-backdrop-filter:
                        blur(14px);

                    font-family:
                        'Segoe UI',
                        Arial,
                        sans-serif;

                    color:
                        #ffffff;
                }}


                /* =========================================
                   TOP AMBIENT GLOW
                   ========================================= */

                .thermal-glass-popup::before {{

                    content: "";

                    position: absolute;

                    top: -45px;
                    left: -35px;

                    width: 150px;
                    height: 100px;

                    background:
                        {color};

                    opacity:
                        0.16;

                    filter:
                        blur(35px);

                    pointer-events:
                        none;
                }}


                /* =========================================
                   HEADER
                   ========================================= */

                .thermal-popup-header {{

                    position:
                        relative;

                    display:
                        flex;

                    align-items:
                        center;

                    gap:
                        10px;

                    padding:
                        14px 42px 12px 15px;

                    background:
                        linear-gradient(
                            135deg,
                            {color}28,
                            rgba(255,255,255,0.025)
                        );

                    border-bottom:
                        1px solid rgba(255,255,255,0.09);
                }}


                /* =========================================
                   HEADER ICON
                   ========================================= */

                .thermal-popup-icon {{

                    width:
                        34px;

                    height:
                        34px;

                    flex:
                        0 0 34px;

                    display:
                        flex;

                    align-items:
                        center;

                    justify-content:
                        center;

                    border-radius:
                        10px;

                    background:
                        {color}18;

                    border:
                        1px solid {color}60;

                    box-shadow:
                        0 0 12px {color}25;

                    font-size:
                        16px;
                }}


                /* =========================================
                   TITLE
                   ========================================= */

                .thermal-popup-title {{

                    font-size:
                        13px;

                    font-weight:
                        800;

                    letter-spacing:
                        0.7px;

                    color:
                        #ffffff;
                }}


                .thermal-popup-subtitle {{

                    margin-top:
                        3px;

                    font-size:
                        8px;

                    letter-spacing:
                        1px;

                    color:
                        #7f8ba3;
                }}


                /* =========================================
                   BODY
                   ========================================= */

                .thermal-popup-body {{

                    position:
                        relative;

                    padding:
                        11px 13px 13px;

                    background:
                        linear-gradient(
                            145deg,
                            rgba(13,20,34,0.90),
                            rgba(5,10,18,0.97)
                        );
                }}


                /* =========================================
                   STATUS PILL
                   ========================================= */

                .thermal-status {{

                    display:
                        inline-flex;

                    align-items:
                        center;

                    gap:
                        5px;

                    padding:
                        4px 9px;

                    margin-bottom:
                        8px;

                    border-radius:
                        20px;

                    background:
                        {color}18;

                    border:
                        1px solid {color}55;

                    color:
                        {color};

                    font-size:
                        8px;

                    font-weight:
                        800;

                    letter-spacing:
                        0.7px;

                    box-shadow:
                        0 0 8px {color}15;
                }}


                /* =========================================
                   FACILITY CARD
                   ========================================= */

                .thermal-facility-card {{

                    padding:
                        9px 10px;

                    border-radius:
                        9px;

                    background:
                        rgba(255,255,255,0.035);

                    border:
                        1px solid rgba(255,255,255,0.06);

                    box-shadow:
                        inset 0 1px 0 rgba(255,255,255,0.035);
                }}


                .thermal-label {{

                    display:
                        block;

                    font-size:
                        8px;

                    text-transform:
                        uppercase;

                    letter-spacing:
                        0.8px;

                    color:
                        #77839a;
                }}


                .thermal-facility-value {{

                    margin-top:
                        4px;

                    font-size:
                        11px;

                    font-weight:
                        700;

                    color:
                        #ffffff;
                }}


                /* =========================================
                   DIVIDER
                   ========================================= */

                .thermal-divider {{

                    height:
                        1px;

                    margin:
                        10px 0;

                    background:
                        linear-gradient(
                            90deg,
                            transparent,
                            rgba(255,255,255,0.12),
                            transparent
                        );
                }}


                /* =========================================
                   METRIC ROW
                   ========================================= */

                .thermal-metric {{

                    display:
                        flex;

                    justify-content:
                        space-between;

                    align-items:
                        center;

                    padding:
                        6px 2px;

                    border-bottom:
                        1px solid rgba(255,255,255,0.055);
                }}


                .thermal-metric:last-child {{
                    border-bottom:
                        none;
                }}


                .thermal-metric-name {{

                    font-size:
                        9px;

                    color:
                        #7f8ba3;
                }}


                .thermal-metric-value {{

                    font-size:
                        10px;

                    font-weight:
                        700;

                    color:
                        #f4f7fb;
                }}


                .thermal-confidence {{

                    color:
                        #55e6a5;
                }}


                /* =========================================
                   COORDINATES
                   ========================================= */

                .thermal-coordinates {{

                    display:
                        flex;

                    flex-direction:
                        column;

                    gap:
                        4px;

                    padding:
                        6px 2px 1px;
                }}


                .thermal-coordinate-value {{

                    font-size:
                        10px;

                    font-weight:
                        700;

                    color:
                        #ffffff;
                }}


                /* =========================================
                   BOTTOM NEON ACCENT
                   ========================================= */

                .thermal-bottom-accent {{

                    height:
                        2px;

                    background:
                        linear-gradient(
                            90deg,
                            transparent,
                            {color},
                            transparent
                        );

                    opacity:
                        0.80;
                }}

                /* =========================================
                   FIRE RISK ANALYSIS SECTION
                   ========================================= */

                .thermal-section-title {{

                    font-size:
                        10px;

                    font-weight:
                        800;

                    letter-spacing:
                        0.8px;

                    color:
                        #ffffff;

                    margin-bottom:
                        8px;
                }}


                .thermal-risk-row {{

                    display:
                        flex;

                    justify-content:
                        space-between;

                    align-items:
                        center;

                    padding:
                        5px 2px;
                }}


                .thermal-risk-label {{

                    font-size:
                        10px;

                    color:
                        #7f8ba3;
                }}


                .thermal-risk-score {{

                    font-size:
                        15px;

                    font-weight:
                        800;

                    color:
                        #ffffff;
                }}


                .thermal-risk-level {{

                    font-size:
                        11px;

                    font-weight:
                        800;

                    letter-spacing:
                        0.5px;
                }}


                .thermal-contrib-positive {{

                    color:
                        #55e6a5;
                }}


                .thermal-recommendation-text {{

                    margin-top:
                        4px;

                    font-size:
                        10.5px;

                    font-weight:
                        600;

                    line-height:
                        1.4;

                    color:
                        #f4f7fb;
                }}

            </style>


            <div class="thermal-glass-popup">


                <!-- HEADER -->

                <div class="thermal-popup-header">

                    <div class="thermal-popup-icon">
                        🔥
                    </div>

                    <div>

                        <div class="thermal-popup-title">
                            {label.upper()}
                        </div>

                        <div class="thermal-popup-subtitle">
                            SATELLITE THERMAL DETECTION
                        </div>

                    </div>

                </div>


                <!-- BODY -->

                <div class="thermal-popup-body">


                    <!-- FACILITY -->

                    <div class="thermal-facility-card">

                        <span class="thermal-label">
                            Facility
                        </span>

                        <div class="thermal-facility-value">
                            {facility}
                        </div>

                    </div>


                    <!-- DIVIDER -->

                    <div class="thermal-divider"></div>


                    <!-- SECTION TITLE -->

                    <div class="thermal-section-title">
                        FIRE RISK ANALYSIS
                    </div>


                    <!-- RISK SCORE -->

                    <div class="thermal-risk-row">

                        <span class="thermal-risk-label">
                            Risk Score
                        </span>

                        <span class="thermal-risk-score">
                            {risk_score}
                        </span>

                    </div>


                    <!-- RISK LEVEL -->

                    <div class="thermal-risk-row">

                        <span class="thermal-risk-label">
                            Risk Level
                        </span>

                        <span class="thermal-risk-level" style="color:{risk_level_color};">
                            {risk_level}
                        </span>

                    </div>


                    <!-- DIVIDER -->

                    <div class="thermal-divider"></div>


                    <!-- BRIGHTNESS CONTRIBUTION -->

                    <div class="thermal-metric">

                        <span class="thermal-metric-name">
                            Brightness
                        </span>

                        <span class="thermal-metric-value thermal-contrib-positive">
                            +{brightness_pts_display}
                        </span>

                    </div>


                    <!-- CONFIDENCE CONTRIBUTION -->

                    <div class="thermal-metric">

                        <span class="thermal-metric-name">
                            Confidence
                        </span>

                        <span class="thermal-metric-value thermal-contrib-positive">
                            +{confidence_pts_display}
                        </span>

                    </div>


                    <!-- PROXIMITY CONTRIBUTION -->

                    <div class="thermal-metric">

                        <span class="thermal-metric-name">
                            Proximity
                        </span>

                        <span class="thermal-metric-value thermal-contrib-positive">
                            +{proximity_pts_display}
                        </span>

                    </div>


                    <!-- INDUSTRIAL CONTRIBUTION -->

                    <div class="thermal-metric">

                        <span class="thermal-metric-name">
                            Industrial
                        </span>

                        <span class="thermal-metric-value thermal-contrib-positive">
                            +{industrial_pts}
                        </span>

                    </div>


                    <!-- DIVIDER -->

                    <div class="thermal-divider"></div>


                    <!-- RECOMMENDATION -->

                    <div>

                        <span class="thermal-label">
                            Recommendation
                        </span>

                        <div class="thermal-recommendation-text">
                            {recommendation}
                        </div>

                    </div>

                </div>


                <!-- BOTTOM ACCENT -->

                <div class="thermal-bottom-accent"></div>

            </div>
            """


            # -------------------------------------------------
            # Pulsing hotspot
            # -------------------------------------------------

            icon_html = f"""
            <div class="thermal-marker"
                 style="--marker-color:{color};">

                <div class="thermal-pulse"></div>

                <div class="thermal-core"></div>

            </div>

            <style>

                .thermal-marker {{
                    position:relative;
                    width:30px;
                    height:30px;
                    transform:translate(-50%, -50%);
                }}

                .thermal-core {{
                    position:absolute;
                    left:50%;
                    top:50%;
                    width:10px;
                    height:10px;
                    transform:translate(-50%, -50%);

                    background:
                        var(--marker-color);

                    border:
                        2px solid white;

                    border-radius:
                        50%;

                    box-shadow:
                        0 0 8px var(--marker-color),
                        0 0 16px var(--marker-color);

                    z-index:
                        3;
                }}

                .thermal-pulse {{
                    position:absolute;
                    left:50%;
                    top:50%;
                    width:10px;
                    height:10px;
                    transform:translate(-50%, -50%);

                    border:
                        2px solid var(--marker-color);

                    border-radius:
                        50%;

                    animation:
                        thermalPulse 1.8s infinite;

                    opacity:
                        0.9;
                }}

                @keyframes thermalPulse {{

                    0% {{
                        width:10px;
                        height:10px;
                        opacity:0.9;
                    }}

                    70% {{
                        width:30px;
                        height:30px;
                        opacity:0.15;
                    }}

                    100% {{
                        width:34px;
                        height:34px;
                        opacity:0;
                    }}

                }}

            </style>
            """


            folium.Marker(
                location=[
                    latitude,
                    longitude
                ],

                popup=folium.Popup(
                    popup_html,
                    max_width=300
                ),

                tooltip=label,

                icon=folium.DivIcon(
                    html=icon_html,
                    icon_size=(30, 30),
                    icon_anchor=(15, 15)
                )

            ).add_to(fire_group)


    fire_group.add_to(m)


    # -----------------------------------------------------
    # Heatmap
    # -----------------------------------------------------

    if heat_points:

        heat_group = folium.FeatureGroup(
            name="Thermal Intensity",
            show=False
        )

        plugins.HeatMap(
            heat_points,
            min_opacity=0.25,
            radius=25,
            blur=18,
            max_zoom=8
        ).add_to(heat_group)

        heat_group.add_to(m)


    # -----------------------------------------------------
    # Legend
    # -----------------------------------------------------

    legend_html = """
    <div style="
        position: fixed;
        bottom: 25px;
        right: 15px;
        z-index: 9999;

        background: rgba(10,10,18,0.88);
        backdrop-filter: blur(10px);

        color: white;

        padding: 12px 15px;

        border-radius: 10px;

        border: 1px solid rgba(255,255,255,0.15);

        box-shadow:
            0 4px 20px rgba(0,0,0,0.35);

        font-family:
            'Segoe UI',
            Arial,
            sans-serif;

        font-size: 11px;

        min-width: 150px;
    ">

        <div style="
            font-weight:700;
            font-size:12px;
            margin-bottom:9px;
        ">
            THERMAL CLASSIFICATION
        </div>


        <div style="margin:5px 0;">

            <span style="
                display:inline-block;
                width:9px;
                height:9px;
                border-radius:50%;
                background:#FF0000;
                margin-right:7px;
            "></span>

            Industrial Fire

        </div>


        <div style="margin:5px 0;">

            <span style="
                display:inline-block;
                width:9px;
                height:9px;
                border-radius:50%;
                background:#FF8C00;
                margin-right:7px;
            "></span>

            Wildfire

        </div>


        <div style="margin:5px 0;">

            <span style="
                display:inline-block;
                width:9px;
                height:9px;
                border-radius:50%;
                background:#00CC00;
                margin-right:7px;
            "></span>

            Thermal Source

        </div>


        <div style="margin:5px 0;">

            <span style="
                display:inline-block;
                width:9px;
                height:9px;
                border-radius:50%;
                background:#0066CC;
                margin-right:7px;
            "></span>

            Unknown

        </div>

    </div>
    """


    m.get_root().html.add_child(
        Element(legend_html)
    )


    # -----------------------------------------------------
    # Controls
    # -----------------------------------------------------

    folium.LayerControl(
        position="topright",
        collapsed=True
    ).add_to(m)


    plugins.Fullscreen(
        position="topright"
    ).add_to(m)


    return m