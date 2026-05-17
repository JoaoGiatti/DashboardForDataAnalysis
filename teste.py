import pandas as pd
df = pd.read_csv("dados/spotify_final.csv", low_memory=False)
print(df.columns.tolist())
print(df.head(2))