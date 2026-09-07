#train_model.py#
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report


print("Loading data...")

df = pd.read_csv("data/classified_fires.csv")

#new#
print("\nClass Distribution:")
print(df["classification"].value_counts())
#new#

FEATURES = [
    "brightness",
    "confidence",
    "frp",
    "distance_to_industry"
]

TARGET = "classification"

df = df.dropna(subset=FEATURES + [TARGET])

X = df[FEATURES]

encoder = LabelEncoder()
y = encoder.fit_transform(df[TARGET])

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y

)

print("Training Random Forest...")

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("\nClassification Report\n")
print(
    classification_report(
        y_test,
        predictions,
        target_names=encoder.classes_
    )
)

joblib.dump(model, "fire_classifier.pkl")
joblib.dump(encoder, "label_encoder.pkl")

print("\nModel Saved:")
print("fire_classifier.pkl")
print("label_encoder.pkl")