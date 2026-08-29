import pandas as pd
import random

df = pd.read_csv("data/industries.csv")

industry_types = [
    "Manufacturing",
    "Chemical",
    "Steel",
    "Power",
    "Textile",
    "Food Processing",
    "Petrochemical",
    "Automobile",
    "Pharmaceutical",
    "Electronics"
]

risk_categories = [
    "LOW",
    "MEDIUM",
    "HIGH"
]

for i in range(len(df)):
    df.loc[i, "name"] = f"Industrial Facility {i+1:05d}"

    if "industry_type" not in df.columns or pd.isna(df.loc[i, "industry_type"]):
        df.loc[i, "industry_type"] = random.choice(industry_types)

    if "risk_category" not in df.columns or pd.isna(df.loc[i, "risk_category"]):
        df.loc[i, "risk_category"] = random.choice(risk_categories)

df.to_csv("data/industries.csv", index=False)

print(f"Updated {len(df)} facilities")