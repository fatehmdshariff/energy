import os
import pandas as pd
import requests
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

# ------------------ Load API Key ------------------
load_dotenv()
API_KEY = os.getenv("EIA_API_KEY")
if not API_KEY:
    raise ValueError("❌ EIA_API_KEY not found in .env file.")

# ------------------ Define Paths ------------------
BASE_DIR = os.path.dirname(__file__)
DATASET_DIR = os.path.join(BASE_DIR, '../datasets')
MODEL_DIR = os.path.join(BASE_DIR, '../models')
os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

DATA_PATH = os.path.join(DATASET_DIR, 'eia_training_data_2023.csv')
MODEL_PATH = os.path.join(MODEL_DIR, 'rf_model_eia_2023.pkl')
META_PATH = os.path.join(MODEL_DIR, 'model_metadata.txt')

# ------------------ Load Existing Data ------------------
if os.path.exists(DATA_PATH):
    df_old = pd.read_csv(DATA_PATH, parse_dates=["datetime"])
    print(f"✅ Loaded existing training data: {len(df_old)} rows")
else:
    print("⚠️ No existing training data found. Starting fresh.")
    df_old = pd.DataFrame(columns=["datetime", "load_mw"])

# ------------------ Fetch New Data from EIA API ------------------
today = datetime.now(timezone.utc)
start = (today - timedelta(days=7)).strftime('%Y-%m-%dT%H')
end = today.strftime('%Y-%m-%dT%H')

params = {
    "api_key": API_KEY,
    "frequency": "hourly",
    "data[0]": "value",
    "facets[respondent][]": "CAL",
    "start": start,
    "end": end,
    "offset": 0,
    "length": 5000
}

records = []
while True:
    response = requests.get("https://api.eia.gov/v2/electricity/rto/region-data/data/", params=params)
    if response.status_code != 200:
        raise ConnectionError(f"❌ API Error: {response.status_code} - {response.text}")
    data = response.json()["response"]["data"]
    if not data:
        break
    records.extend(data)
    if len(data) < params["length"]:
        break
    params["offset"] += params["length"]

# ------------------ Clean and Format New Data ------------------
df_new = pd.DataFrame(records)
if not df_new.empty:
    df_new["datetime"] = pd.to_datetime(df_new["period"])
    df_new["load_mw"] = pd.to_numeric(df_new["value"], errors="coerce")
    df_new = df_new[["datetime", "load_mw"]].dropna()
else:
    print("⚠️ No new data fetched. Using only existing dataset.")
    df_new = pd.DataFrame(columns=["datetime", "load_mw"])

# ------------------ Merge with Existing Data ------------------
if not df_new.empty:
    df = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates("datetime").sort_values("datetime")
else:
    df = df_old.copy()

# ------------------ Feature Engineering ------------------
df['hour'] = df['datetime'].dt.hour
df['dayofweek'] = df['datetime'].dt.dayofweek
df['month'] = df['datetime'].dt.month
df['is_weekend'] = df['dayofweek'].apply(lambda x: 1 if x >= 5 else 0)
df['lag_1'] = df['load_mw'].shift(1)
df['lag_2'] = df['load_mw'].shift(2)
df['lag_24'] = df['load_mw'].shift(24)
df['rolling_mean_3'] = df['load_mw'].rolling(3).mean()
df['rolling_mean_24'] = df['load_mw'].rolling(24).mean()
df = df.dropna()

# ------------------ Train Model ------------------
features = ['hour', 'dayofweek', 'month', 'is_weekend',
            'lag_1', 'lag_2', 'lag_24', 'rolling_mean_3', 'rolling_mean_24']
X = df[features]
y = df['load_mw']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ------------------ Save Model, Data & Metadata ------------------
joblib.dump(model, MODEL_PATH)
df.to_csv(DATA_PATH, index=False)

# Save training timestamp
train_date = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
with open(META_PATH, 'w') as f:
    f.write(f"last_trained: {train_date}\n")

print(f"✅ Model retrained and saved to: {MODEL_PATH}")
print(f"📦 Training data updated: {len(df)} total rows")
print(f"🕒 Training date saved to: {META_PATH}")
