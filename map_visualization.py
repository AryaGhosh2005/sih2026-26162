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
            # Popup
            # -------------------------------------------------

            popup_html = f"""
            <div style="
                font-family:'Segoe UI',sans-serif;
                min-width:230px;
                border-radius:8px;
                overflow:hidden;
            ">

                <div style="
                    background:{color};
                    color:white;
                    padding:9px 12px;
                    font-weight:700;
                    font-size:13px;
                ">
                    {label.upper()}
                </div>

                <div style="
                    padding:11px 12px;
                    background:#111827;
                    color:#ffffff;
                    font-size:11px;
                    line-height:1.7;
                ">

                    <div>
                        <span style="color:#9ca3af;">
                            Facility
                        </span>
                        <br>
                        <b>{facility}</b>
                    </div>

                    <hr style="
                        border:none;
                        border-top:1px solid #374151;
                    ">

                    <div>
                        <span style="color:#9ca3af;">
                            Brightness
                        </span>
                        &nbsp;
                        <b>{brightness} K</b>
                    </div>

                    <div>
                        <span style="color:#9ca3af;">
                            Confidence
                        </span>
                        &nbsp;
                        <b>{confidence}%</b>
                    </div>

                    <div>
                        <span style="color:#9ca3af;">
                            Industry Distance
                        </span>
                        &nbsp;
                        <b>{distance} km</b>
                    </div>

                    <div>
                        <span style="color:#9ca3af;">
                            Coordinates
                        </span>
                        <br>
                        <b>
                            {latitude:.4f},
                            {longitude:.4f}
                        </b>
                    </div>

                </div>
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
                    background:var(--marker-color);
                    border:2px solid white;
                    border-radius:50%;
                    box-shadow:
                        0 0 8px var(--marker-color),
                        0 0 16px var(--marker-color);
                    z-index:3;
                }}

                .thermal-pulse {{
                    position:absolute;
                    left:50%;
                    top:50%;
                    width:10px;
                    height:10px;
                    transform:translate(-50%, -50%);
                    border:2px solid var(--marker-color);
                    border-radius:50%;
                    animation:thermalPulse 1.8s infinite;
                    opacity:0.9;
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
                    max_width=280
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