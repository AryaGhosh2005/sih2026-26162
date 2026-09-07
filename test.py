import pandas as pd
df = pd.read_csv("data/classified_fires.csv")
print(df["distance_to_industry"].max())