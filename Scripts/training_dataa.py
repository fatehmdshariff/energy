
#to sae hte EIA history to a csv file as its not available 


import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("EIA_API_KEY")
BASE_URL = "https://api.eia.gov/v2/electricity/rto/region-data/data/"
params = {
    "api_key": API_KEY,
    "frequency": "hourly",
    "data[0]": "value",
    "facets[respondent][]": "CAL",
    "start": "2023-01-01T00",
    "end": "2023-12-31T23",
    "offset": 0,
    "length": 5000
}

all_data = []
while True:
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    batch = data["response"]["data"]
    if not batch:
        break
    all_data.extend(batch)
    if len(batch) < params["length"]:
        break
    params["offset"] += params["length"]

df = pd.DataFrame(all_data)
df["datetime"] = pd.to_datetime(df["period"])
df["load_mw"] = pd.to_numeric(df["value"], errors="coerce")
df = df[["datetime", "load_mw"]].dropna().sort_values("datetime")
df.to_csv("eia_training_data_2023.csv", index=False)
