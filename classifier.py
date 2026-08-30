"""
classifier.py

SIH 26162
Industrial Fire Classification Engine

Input:
    data/firms_raw.csv
    data/industries.csv

Output:
    data/classified_fires.csv
"""

import os
import pandas as pd
from scipy.spatial import cKDTree
from ml_classifier import predict_fire_type

# =========================================================
# CONFIGURATION
# =========================================================

FIRMS_FILE = "data/firms_raw.csv"
INDUSTRIES_FILE = "data/industries.csv"
OUTPUT_FILE = "data/classified_fires.csv"


# =========================================================
# CLASSIFICATION THRESHOLDS
# =========================================================

# Industrial association
NEARBY_DISTANCE_KM = 50
DISTANT_DISTANCE_KM = 150

# Strong industrial-fire signal
INDUSTRIAL_DISTANCE_KM = 50
INDUSTRIAL_BRIGHTNESS = 325
INDUSTRIAL_CONFIDENCE = 55
INDUSTRIAL_FRP = 2

# Strong general thermal signal
WILDFIRE_BRIGHTNESS = 325

# Thermal source threshold
THERMAL_BRIGHTNESS = 300
THERMAL_FRP = 2


# =========================================================
# LOAD DATA
# =========================================================

if not os.path.exists(FIRMS_FILE):

    raise FileNotFoundError(
        f"Missing {FIRMS_FILE}"
    )


if not os.path.exists(INDUSTRIES_FILE):

    raise FileNotFoundError(
        f"Missing {INDUSTRIES_FILE}"
    )


fires_df = pd.read_csv(
    FIRMS_FILE
)

industries_df = pd.read_csv(
    INDUSTRIES_FILE
)


print(
    f"NASA detections: {len(fires_df)}"
)

print(
    f"Industrial facilities: "
    f"{len(industries_df)}"
)


# =========================================================
# COLUMN NORMALIZATION
# =========================================================

if "bright_ti4" in fires_df.columns:

    fires_df = fires_df.rename(
        columns={
            "bright_ti4": "brightness"
        }
    )


if "acq_date" in fires_df.columns:

    fires_df = fires_df.rename(
        columns={
            "acq_date":
                "acquisition_date"
        }
    )


# =========================================================
# ACQUISITION TIME
# =========================================================

if "acq_time" in fires_df.columns:

    fires_df["acquisition_time"] = (

        pd.to_numeric(
            fires_df["acq_time"],
            errors="coerce"
        )

        .fillna(0)

        .astype(int)

        .astype(str)

        .str.zfill(4)
    )


# =========================================================
# CONFIDENCE
# =========================================================

if "confidence" not in fires_df.columns:

    fires_df["confidence"] = 50


def clean_confidence(value):

    if pd.isna(value):

        return 50.0

    value = str(
        value
    ).strip().lower()


    if value == "l":

        return 30.0


    if value == "n":

        return 70.0


    if value == "h":

        return 95.0


    try:

        return float(value)

    except:

        return 50.0


fires_df["confidence"] = (

    fires_df["confidence"]

    .apply(clean_confidence)
)


# =========================================================
# NUMERIC CLEANING
# =========================================================

numeric_columns = [

    "latitude",
    "longitude",
    "brightness",
    "frp",
    "scan",
    "track"
]


for column in numeric_columns:

    if column in fires_df.columns:

        fires_df[column] = pd.to_numeric(

            fires_df[column],

            errors="coerce"
        )


fires_df["brightness"] = (

    fires_df["brightness"]

    .fillna(0)
)


fires_df["frp"] = (

    fires_df["frp"]

    .fillna(0)
)


# =========================================================
# VALIDATE INDUSTRY DATA
# =========================================================

required_industry_columns = [

    "name",
    "latitude",
    "longitude",
    "type"
]


missing_industry_columns = [

    column

    for column in required_industry_columns

    if column not in industries_df.columns
]


if missing_industry_columns:

    raise RuntimeError(

        "industries.csv is missing columns: "

        f"{missing_industry_columns}"
    )


# =========================================================
# NEAREST INDUSTRIAL FACILITY
# =========================================================

industry_coords = (

    industries_df[

        [
            "latitude",
            "longitude"
        ]

    ]

    .astype(float)

    .values
)


fire_coords = (

    fires_df[

        [
            "latitude",
            "longitude"
        ]

    ]

    .astype(float)

    .values
)


# ---------------------------------------------------------
# KD TREE
# ---------------------------------------------------------

tree = cKDTree(
    industry_coords
)


distances, indices = tree.query(
    fire_coords
)


# ---------------------------------------------------------
# APPROXIMATE KM CONVERSION
# ---------------------------------------------------------
#
# This is suitable for our India-scale MVP.
#
# 1 degree ≈ 111 km
#
# ---------------------------------------------------------

distances_km = (
    distances * 111
)


fires_df[
    "distance_to_industry"
] = (

    distances_km

    .round(2)
)

def industry_match_confidence(distance):

    if distance <= 10:
        return 95

    if distance <= 25:
        return 80

    if distance <= 50:
        return 60

    return 20


fires_df["industry_match_confidence"] = (
    fires_df["distance_to_industry"]
    .apply(industry_match_confidence)
)

fires_df[
    "nearest_industry"
] = (

    industries_df

    .iloc[indices]

    ["name"]

    .values
)


fires_df[
    "industry_type"
] = (

    industries_df

    .iloc[indices]

    ["type"]

    .values
)


# =========================================================
# INDUSTRIAL ASSOCIATION
# =========================================================

def determine_association(
    distance
):

    if distance <= NEARBY_DISTANCE_KM:

        return "NEARBY"


    if distance <= DISTANT_DISTANCE_KM:

        return "DISTANT"


    return "NONE"


fires_df[
    "industrial_association"
] = (

    fires_df[
        "distance_to_industry"
    ]

    .apply(
        determine_association
    )
)


# =========================================================
# CLASSIFICATION
# =========================================================

def classify(row):

    brightness = float(
        row.get(
            "brightness",
            0
        )
    )

    confidence = float(
        row.get(
            "confidence",
            0
        )
    )

    frp = float(
        row.get(
            "frp",
            0
        )
    )

    distance = float(
        row.get(
            "distance_to_industry",
            9999
        )
    )


    # =====================================================
    # INDUSTRIAL FIRE
    # =====================================================
    #
    # Strong thermal signal AND reasonably close to
    # an industrial facility.
    #
    # We intentionally use multiple indicators rather
    # than distance alone.
    #
    # =====================================================

    industrial_signal = (

        distance <= INDUSTRIAL_DISTANCE_KM

        and confidence >= INDUSTRIAL_CONFIDENCE

        and (

            brightness >= INDUSTRIAL_BRIGHTNESS

            or frp >= INDUSTRIAL_FRP
        )
    )


    if industrial_signal:

        return "INDUSTRIAL_FIRE"


    # =====================================================
    # WILDFIRE
    # =====================================================

    if (

        brightness >= WILDFIRE_BRIGHTNESS

        and distance > INDUSTRIAL_DISTANCE_KM
    ):

        return "WILDFIRE"


    # =====================================================
    # THERMAL SOURCE
    # =====================================================

    if (

        brightness >= THERMAL_BRIGHTNESS

        or frp >= THERMAL_FRP
    ):

        return "THERMAL_SOURCE"


    # =====================================================
    # UNKNOWN
    # =====================================================

    return "UNKNOWN"


fires_df["classification"] = (
    fires_df
    .apply(classify, axis=1)
)


fires_df["ai_prediction"] = fires_df.apply(
    lambda row: predict_fire_type(
        row["brightness"],
        row["confidence"],
        row["frp"],
        row["distance_to_industry"]
    ),
    axis=1
)

fires_df["ai_match"] = (
    fires_df["classification"]
    ==
    fires_df["ai_prediction"]
)

ai_matches = (
    fires_df["classification"]
    ==
    fires_df["ai_prediction"]
).sum()

ai_accuracy = (
    ai_matches / len(fires_df)
) * 100

print("\n")
print("=" * 60)
print("AI AGREEMENT")
print("=" * 60)
print(f"Matches: {ai_matches}/{len(fires_df)}")
print(f"Agreement: {ai_accuracy:.2f}%")

print("\n")
print("=" * 60)
print("AI DISAGREEMENTS")
print("=" * 60)

print(
    fires_df[
        fires_df["ai_match"] == False
    ][
        [
            "brightness",
            "confidence",
            "frp",
            "distance_to_industry",
            "classification",
            "ai_prediction"
        ]
    ]
)

# =========================================================
# RISK SCORE
# =========================================================

def calculate_risk_score(
    row
):

    score = 0


    brightness = float(
        row.get(
            "brightness",
            0
        )
    )


    confidence = float(
        row.get(
            "confidence",
            0
        )
    )


    frp = float(
        row.get(
            "frp",
            0
        )
    )


    distance = float(
        row.get(
            "distance_to_industry",
            9999
        )
    )


    classification = row.get(
        "classification",
        "UNKNOWN"
    )


    # -----------------------------------------------------
    # Brightness
    # -----------------------------------------------------

    if brightness >= 340:

        score += 30

    elif brightness >= 325:

        score += 20

    elif brightness >= 310:

        score += 10


    # -----------------------------------------------------
    # Confidence
    # -----------------------------------------------------

    if confidence >= 90:

        score += 20

    elif confidence >= 70:

        score += 15

    elif confidence >= 55:

        score += 10


    # -----------------------------------------------------
    # FRP
    # -----------------------------------------------------

    if frp >= 10:

        score += 25

    elif frp >= 5:

        score += 20

    elif frp >= 2:

        score += 10


    # -----------------------------------------------------
    # Industrial proximity
    # -----------------------------------------------------

    if distance <= 10:

        score += 25

    elif distance <= 25:

        score += 20

    elif distance <= 50:

        score += 15

    elif distance <= 100:

        score += 5


    # -----------------------------------------------------
    # Classification bonus
    # -----------------------------------------------------

    if classification == "INDUSTRIAL_FIRE":

        score += 10


    # -----------------------------------------------------
    # Cap score
    # -----------------------------------------------------

    return min(
        score,
        100
    )


fires_df[
    "risk_score"
] = (

    fires_df

    .apply(
        calculate_risk_score,
        axis=1
    )
)


# =========================================================
# RISK LEVEL
# =========================================================

def calculate_risk_level(
    score
):

    if score >= 70:

        return "HIGH"


    if score >= 40:

        return "MEDIUM"


    return "LOW"


fires_df[
    "risk_level"
] = (

    fires_df[
        "risk_score"
    ]

    .apply(
        calculate_risk_level
    )
)


# =========================================================
# SORT BY RISK
# =========================================================

fires_df = (

    fires_df

    .sort_values(

        by=[
            "risk_score",
            "brightness",
            "frp"
        ],

        ascending=False
    )

    .reset_index(
        drop=True
    )
)


# =========================================================
# CLASSIFICATION SUMMARY
# =========================================================

print("\n")
print("=" * 60)
print("CLASSIFICATION SUMMARY")
print("=" * 60)

print(

    fires_df[
        "classification"
    ]

    .value_counts()
)


# =========================================================
# RISK SUMMARY
# =========================================================

print("\n")
print("=" * 60)
print("RISK LEVEL SUMMARY")
print("=" * 60)

print(

    fires_df[
        "risk_level"
    ]

    .value_counts()
)


# =========================================================
# INDUSTRIAL ASSOCIATION SUMMARY
# =========================================================

print("\n")
print("=" * 60)
print("INDUSTRIAL ASSOCIATION SUMMARY")
print("=" * 60)

print(

    fires_df[
        "industrial_association"
    ]

    .value_counts()
)


# =========================================================
# DISTANCE STATISTICS
# =========================================================

print("\n")
print("=" * 60)
print("DISTANCE STATISTICS")
print("=" * 60)

print(

    fires_df[
        "distance_to_industry"
    ]

    .describe()
)


# =========================================================
# INDUSTRIAL FIRE DETAILS
# =========================================================

industrial_fires = (

    fires_df[
        fires_df[
            "classification"
        ]
        ==
        "INDUSTRIAL_FIRE"
    ]
)


print("\n")
print("=" * 60)
print("INDUSTRIAL FIRE DETECTIONS")
print("=" * 60)


if industrial_fires.empty:

    print(
        "No industrial fires detected."
    )

else:

    print(
        industrial_fires[
            [
                "latitude",
                "longitude",
                "brightness",
                "confidence",
                "frp",
                "distance_to_industry",
                "nearest_industry",
                "industry_type",
                "risk_score",
                "risk_level"
            ]
        ]

        .head(20)

        .to_string(
            index=False
        )
    )


# =========================================================
# CLOSEST DETECTIONS
# =========================================================

print("\n")
print("=" * 60)
print("CLOSEST NASA DETECTIONS TO INDUSTRY")
print("=" * 60)


print(

    fires_df[

        [

            "classification",
            "brightness",
            "confidence",
            "frp",
            "distance_to_industry",
            "nearest_industry",
            "industry_type"
        ]

    ]

    .sort_values(
        "distance_to_industry"
    )

    .head(15)

    .to_string(
        index=False
    )
)


# =========================================================
# DATA CONTRACT CHECK
# =========================================================

required_output_columns = [

    "latitude",
    "longitude",
    "brightness",
    "acquisition_date",
    "satellite",
    "classification",
    "confidence",
    "distance_to_industry"
]


classification_values = [

    "INDUSTRIAL_FIRE",
    "WILDFIRE",
    "THERMAL_SOURCE",
    "UNKNOWN"
]


contract_ok = True


# ---------------------------------------------------------
# Columns
# ---------------------------------------------------------

missing_columns = [

    column

    for column in required_output_columns

    if column not in fires_df.columns
]


if missing_columns:

    contract_ok = False

    print(
        "\nMissing columns:"
    )

    print(
        missing_columns
    )


# ---------------------------------------------------------
# Classification values
# ---------------------------------------------------------

invalid_classifications = (

    set(
        fires_df[
            "classification"
        ]
        .dropna()
        .unique()
    )

    -

    set(
        classification_values
    )
)


if invalid_classifications:

    contract_ok = False

    print(
        "\nInvalid classifications:"
    )

    print(
        invalid_classifications
    )


# ---------------------------------------------------------
# Classification uppercase
# ---------------------------------------------------------

if not (

    fires_df[
        "classification"
    ]

    ==

    fires_df[
        "classification"
    ].str.upper()

).all():

    contract_ok = False

    print(
        "\nClassification case error."
    )


# ---------------------------------------------------------
# Contract result
# ---------------------------------------------------------

print("\n")
print("=" * 60)
print("DATA CONTRACT CHECK")
print("=" * 60)


if contract_ok:

    print(
        "PASS - Universal Data Contract satisfied"
    )

else:

    print(
        "FAIL - Universal Data Contract violated"
    )



#new#
######


print("\n")
print("=" * 60)
print("INDUSTRIAL FIRE CANDIDATES")
print("=" * 60)

candidate = fires_df[
    (fires_df["distance_to_industry"] <= 25) &
    (fires_df["brightness"] >= 305) &
    (fires_df["frp"] >= 2)
]

print("Candidate Count:", len(candidate))

print(
    candidate[
        [
            "brightness",
            "confidence",
            "frp",
            "distance_to_industry",
            "classification",
            "nearest_industry"
        ]
    ]
    .head(30)
    .to_string(index=False)
)
# =========================================================
# SAVE
# =========================================================

fires_df["id"] = [
    f"FIRE_{i+1:05d}"
    for i in range(len(fires_df))
]

fires_df.to_csv(

    OUTPUT_FILE,

    index=False
)


print("\n")
print("=" * 60)

print("Saved:")
print(OUTPUT_FILE)

print(
    f"Records: {len(fires_df)}"
)

print("=" * 60)