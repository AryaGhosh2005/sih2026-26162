"""
data_generator.py

SIH 26162 - Industrial Fire Detection System

DATA PIPELINE

NASA FIRMS
    ↓
firms_raw.csv
    ↓
classifier.py
    ↓
classified_fires.csv

Industrial facilities are loaded from:
    data/industries.csv

IMPORTANT:
This script DOES NOT query OpenStreetMap.

The industrial facility dataset is maintained separately
so NASA ingestion remains fast and reliable.
"""

import os
from io import StringIO

import pandas as pd
import requests
from dotenv import load_dotenv


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

API_KEY = os.getenv(
    "NASA_FIRMS_API_KEY"
)

DATA_DIR = "data"

FIRMS_OUTPUT = os.path.join(
    DATA_DIR,
    "firms_raw.csv"
)

INDUSTRIES_FILE = os.path.join(
    DATA_DIR,
    "industries.csv"
)

SOURCE = "VIIRS_NOAA21_NRT"

INDIA_BBOX = "68,8,97,37"

DAY_RANGE = 5

NASA_TIMEOUT = 60


# =========================================================
# CREATE DATA DIRECTORY
# =========================================================

os.makedirs(
    DATA_DIR,
    exist_ok=True
)


# =========================================================
# NASA FIRMS
# =========================================================

def download_firms_data():

    print("=" * 60)

    print(
        "SIH 26162 - NASA FIRMS DATA INGESTION"
    )

    print("=" * 60)

    # -----------------------------------------------------
    # API KEY
    # -----------------------------------------------------

    if not API_KEY:

        raise RuntimeError(

            "\nNASA_FIRMS_API_KEY was not found.\n\n"

            "Create a .env file containing:\n\n"

            "NASA_FIRMS_API_KEY=YOUR_KEY_HERE\n"
        )

    print(
        "\nConnecting to NASA FIRMS..."
    )

    print(
        f"Dataset: {SOURCE}"
    )

    print(
        "Area: India"
    )

    print(
        f"Days requested: {DAY_RANGE}"
    )

    # -----------------------------------------------------
    # NASA URL
    # -----------------------------------------------------

    url = (

        "https://firms.modaps.eosdis.nasa.gov/"

        f"api/area/csv/"

        f"{API_KEY}/"

        f"{SOURCE}/"

        f"{INDIA_BBOX}/"

        f"{DAY_RANGE}"
    )

    # -----------------------------------------------------
    # REQUEST
    # -----------------------------------------------------

    try:

        response = requests.get(

            url,

            timeout=NASA_TIMEOUT
        )

    except requests.RequestException as e:

        raise RuntimeError(

            f"\nCould not connect to NASA FIRMS:\n{e}"
        )

    # -----------------------------------------------------
    # HTTP STATUS
    # -----------------------------------------------------

    if response.status_code != 200:

        print(
            "\nNASA FIRMS request failed."
        )

        print(
            f"HTTP Status: "
            f"{response.status_code}"
        )

        print(
            "\nNASA response:"
        )

        print(
            response.text[:1000]
        )

        raise RuntimeError(
            "\nNASA FIRMS API request failed."
        )

    # -----------------------------------------------------
    # READ CSV
    # -----------------------------------------------------

    try:

        firms_df = pd.read_csv(

            StringIO(
                response.text
            )
        )

    except Exception as e:

        print(
            "\nNASA response:"
        )

        print(
            response.text[:1000]
        )

        raise RuntimeError(

            f"\nCould not read NASA CSV:\n{e}"
        )

    # -----------------------------------------------------
    # REQUIRED COLUMNS
    # -----------------------------------------------------

    required_columns = [

        "latitude",
        "longitude",
        "bright_ti4",
        "scan",
        "track",
        "acq_date",
        "acq_time",
        "satellite",
        "instrument",
        "confidence",
        "version",
        "bright_ti5",
        "frp",
        "daynight"
    ]

    missing_columns = [

        column

        for column in required_columns

        if column not in firms_df.columns
    ]

    if missing_columns:

        raise RuntimeError(

            "\nNASA response is missing columns:\n"

            + str(missing_columns)
        )

    # =====================================================
    # NORMALIZATION
    # =====================================================

    firms_df = firms_df.rename(

        columns={

            "bright_ti4":
                "brightness",

            "acq_date":
                "acquisition_date"
        }
    )

    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    firms_df[
        "acquisition_date"
    ] = (

        pd.to_datetime(

            firms_df[
                "acquisition_date"
            ],

            errors="coerce"
        )

        .dt.strftime(
            "%Y-%m-%d"
        )
    )

    # -----------------------------------------------------
    # NUMERIC COLUMNS
    # -----------------------------------------------------

    numeric_columns = [

        "latitude",
        "longitude",
        "brightness",
        "scan",
        "track",
        "bright_ti5",
        "frp"
    ]

    for column in numeric_columns:

        firms_df[column] = pd.to_numeric(

            firms_df[column],

            errors="coerce"
        )

    # -----------------------------------------------------
    # CONFIDENCE
    # -----------------------------------------------------

    firms_df[
        "confidence_raw"
    ] = (

        firms_df[
            "confidence"
        ]

        .astype(str)

        .str.lower()

        .str.strip()
    )

    confidence_map = {

        "l": 30,
        "n": 70,
        "h": 95
    }

    firms_df[
        "confidence"
    ] = (

        firms_df[
            "confidence_raw"
        ]

        .map(
            confidence_map
        )

        .fillna(50)
    )

    # -----------------------------------------------------
    # ACQUISITION TIME
    # -----------------------------------------------------

    firms_df[
        "acquisition_time"
    ] = (

        pd.to_numeric(

            firms_df[
                "acq_time"
            ],

            errors="coerce"
        )

        .fillna(0)

        .astype(int)

        .astype(str)

        .str.zfill(4)
    )

    # -----------------------------------------------------
    # DAY / NIGHT
    # -----------------------------------------------------

    firms_df[
        "daynight"
    ] = (

        firms_df[
            "daynight"
        ]

        .astype(str)

        .str.upper()
    )

    # -----------------------------------------------------
    # REMOVE INVALID DATA
    # -----------------------------------------------------

    firms_df = firms_df.dropna(

        subset=[

            "latitude",
            "longitude",
            "brightness"
        ]
    )

    # -----------------------------------------------------
    # INDIA BOUNDARY CHECK
    # -----------------------------------------------------

    firms_df = firms_df[

        (firms_df["latitude"] >= 8)

        &

        (firms_df["latitude"] <= 37)

        &

        (firms_df["longitude"] >= 68)

        &

        (firms_df["longitude"] <= 97)
    ]

    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    firms_df = firms_df.sort_values(

        by=[

            "acquisition_date",
            "acquisition_time"
        ],

        ascending=False
    )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    firms_df.to_csv(

        FIRMS_OUTPUT,

        index=False
    )

    # =====================================================
    # OUTPUT
    # =====================================================

    print(
        "\nNASA FIRMS connection successful!"
    )

    print(
        f"Records downloaded: "
        f"{len(firms_df)}"
    )

    print(
        f"Saved to: {FIRMS_OUTPUT}"
    )

    print(
        "\nNASA preview:"
    )

    print(

        firms_df[

            [

                "latitude",
                "longitude",
                "brightness",
                "acquisition_date",
                "acquisition_time",
                "satellite",
                "confidence",
                "frp",
                "daynight"
            ]

        ]

        .head(10)

        .to_string(
            index=False
        )
    )

    return firms_df


# =========================================================
# LOAD INDUSTRIAL FACILITIES
# =========================================================

def load_industries():

    print("\n")
    print("=" * 60)

    print(
        "INDUSTRIAL FACILITY DATA"
    )

    print("=" * 60)

    # -----------------------------------------------------
    # IMPORTANT:
    # DO NOT DOWNLOAD / GENERATE / OVERWRITE FACILITIES
    # -----------------------------------------------------

    if not os.path.exists(
        INDUSTRIES_FILE
    ):

        raise FileNotFoundError(

            "\nindustries.csv was not found.\n\n"

            f"Expected location:\n"
            f"{INDUSTRIES_FILE}\n\n"

            "Create the facility dataset first."
        )

    print(
        "\nLoading existing facility dataset..."
    )

    industries_df = pd.read_csv(

        INDUSTRIES_FILE
    )

    # -----------------------------------------------------
    # REQUIRED COLUMNS
    # -----------------------------------------------------

    required_columns = [

        "name",
        "latitude",
        "longitude",
        "type"
    ]

    missing_columns = [

        column

        for column in required_columns

        if column not in industries_df.columns
    ]

    if missing_columns:

        raise RuntimeError(

            "\nindustries.csv is missing:\n"

            + str(missing_columns)
        )

    # -----------------------------------------------------
    # NUMERIC
    # -----------------------------------------------------

    industries_df[
        "latitude"
    ] = pd.to_numeric(

        industries_df[
            "latitude"
        ],

        errors="coerce"
    )

    industries_df[
        "longitude"
    ] = pd.to_numeric(

        industries_df[
            "longitude"
        ],

        errors="coerce"
    )

    # -----------------------------------------------------
    # REMOVE INVALID FACILITIES
    # -----------------------------------------------------

    industries_df = industries_df.dropna(

        subset=[

            "latitude",
            "longitude"
        ]
    )

    # -----------------------------------------------------
    # INDIA CHECK
    # -----------------------------------------------------

    industries_df = industries_df[

        (industries_df["latitude"] >= 8)

        &

        (industries_df["latitude"] <= 37)

        &

        (industries_df["longitude"] >= 68)

        &

        (industries_df["longitude"] <= 97)
    ]

    # -----------------------------------------------------
    # REMOVE DUPLICATES
    # -----------------------------------------------------

    industries_df = (

        industries_df

        .drop_duplicates(
            subset=[
                "name",
                "latitude",
                "longitude"
            ]
        )

        .reset_index(
            drop=True
        )
    )

    # -----------------------------------------------------
    # DATA SOURCE
    # -----------------------------------------------------

    if "data_source" not in industries_df.columns:

        industries_df[
            "data_source"
        ] = "REFERENCE_DATASET"

    # -----------------------------------------------------
    # SAVE CLEANED DATA
    # -----------------------------------------------------

    industries_df.to_csv(

        INDUSTRIES_FILE,

        index=False
    )

    # =====================================================
    # OUTPUT
    # =====================================================

    print(
        "\nIndustrial facility dataset loaded."
    )

    print(
        f"Facilities: "
        f"{len(industries_df)}"
    )

    print(
        "\nFacility types:"
    )

    print(
        industries_df[
            "type"
        ].value_counts()
    )

    print(
        "\nData source:"
    )

    print(
        industries_df[
            "data_source"
        ].value_counts()
    )

    print(
        f"\nSaved: "
        f"{INDUSTRIES_FILE}"
    )

    return industries_df


# =========================================================
# MAIN
# =========================================================

def main():

    print("\n")

    # =====================================================
    # STEP 1
    # NASA
    # =====================================================

    firms_df = (
        download_firms_data()
    )

    # =====================================================
    # STEP 2
    # INDUSTRIES
    # =====================================================

    industries_df = (
        load_industries()
    )

    # =====================================================
    # FINAL SUMMARY
    # =====================================================

    print("\n")
    print("=" * 60)

    print(
        "DATA INGESTION COMPLETE"
    )

    print("=" * 60)

    print(
        f"\nNASA FIRMS detections : "
        f"{len(firms_df)}"
    )

    print(
        f"Industrial facilities : "
        f"{len(industries_df)}"
    )

    print(
        f"\nNASA data:"
        f" {FIRMS_OUTPUT}"
    )

    print(
        f"Industry data:"
        f" {INDUSTRIES_FILE}"
    )

    print(
        "\nNext step:"
    )

    print(
        "python classifier.py"
    )

    print("=" * 60)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()