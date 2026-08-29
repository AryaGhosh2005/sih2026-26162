#ml_classifier.py#


import joblib
import pandas as pd

model = joblib.load("fire_classifier.pkl")
encoder = joblib.load("label_encoder.pkl")


def predict_fire_type(
    brightness,
    confidence,
    frp,
    distance_to_industry
):
    X = pd.DataFrame(
        [[
            brightness,
            confidence,
            frp,
            distance_to_industry
        ]],
        columns=[
            "brightness",
            "confidence",
            "frp",
            "distance_to_industry"
        ]
    )

    prediction = model.predict(X)[0]

    return encoder.inverse_transform(
        [prediction]
    )[0]