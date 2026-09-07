import pandas as pd

df = pd.read_csv("data/classified_fires.csv")

print(
    df.sort_values(
        "risk_score",
        ascending=False
    )[
        [
            "risk_score",
            "risk_level",
            "classification",
            "brightness",
            "confidence",
            "distance_to_industry"
        ]
    ].head(20)
)