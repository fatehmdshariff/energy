"""
import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("EIA_API_KEY")
if not API_KEY:
    raise ValueError("API key not found! Make sure it's set in the .env file.")

# ✅ EIA v2-compatible URL
SERIES_ID = "EBA.CAL-ALL.D.H"
url = f"https://api.eia.gov/v2/seriesid/{SERIES_ID}?api_key={API_KEY}"

# Make request
response = requests.get(url)

# Print full error message for debug
print("Full response:", response.text)

if response.status_code != 200:
    raise ConnectionError(f"API request failed with status code {response.status_code}")

# Extract and process data
data = response.json()
records = data['response']['data']
df_live = pd.DataFrame(records)

# Convert datetime column
df_live['datetime'] = pd.to_datetime(df_live['period'])

# Set datetime as index
df_live = df_live.sort_values('datetime')
df_live = df_live.set_index('datetime')

# Keep only useful columns
df_live = df_live[['value']]
df_live.columns = ['load_mw']

# Show latest records
print(df_live.tail())
"""





import requests
import pandas as pd
import os
import joblib
from dotenv import load_dotenv
from sklearn.preprocessing import StandardScaler

# ---------------------- 1. Load environment variables ----------------------
load_dotenv()
API_KEY = os.getenv("EIA_API_KEY")

if not API_KEY:
    raise ValueError("API key not found! Make sure it's set in the .env file.")

# ---------------------- 2. Define EIA API URL ----------------------
# Hourly load data for California (EIA v2)
url = f"https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key={API_KEY}&frequency=hourly&data[0]=value&facets[respondent][]=CAL"

# ---------------------- 3. Make API request ----------------------
response = requests.get(url)
if response.status_code != 200:
    print("Full response:", response.text)
    raise ConnectionError(f"API request failed with status code {response.status_code}")

# ---------------------- 4. Convert response to DataFrame ----------------------
data = response.json()
records = data['response']['data']
df_live = pd.DataFrame(records)

# Extract relevant columns
df_live['datetime'] = pd.to_datetime(df_live['period'])
df_live['load_mw'] = df_live['value']
df_live = df_live[['datetime', 'load_mw']]

# Sort and set index
df_live = df_live.sort_values('datetime')
df_live = df_live.set_index('datetime')

# ---------------------- 5. Feature Engineering ----------------------
df_live['hour'] = df_live.index.hour
df_live['dayofweek'] = df_live.index.dayofweek
df_live['month'] = df_live.index.month
df_live['is_weekend'] = df_live['dayofweek'].apply(lambda x: 1 if x >= 5 else 0)

# Lag features
df_live['lag_1'] = df_live['load_mw'].shift(1)
df_live['lag_2'] = df_live['load_mw'].shift(2)
df_live['lag_24'] = df_live['load_mw'].shift(24)

# Rolling features (✅ match training-time features)
df_live['rolling_mean_3'] = df_live['load_mw'].rolling(window=3).mean()
df_live['rolling_mean_24'] = df_live['load_mw'].rolling(window=24).mean()

# Drop rows with NaNs
df_live = df_live.dropna()

# ---------------------- 6. Load Model ----------------------
model = joblib.load(r"D:\Projects_25\Energy_Ananlysis\energy\models\rf_model_hourly.pkl")

# ---------------------- 7. Prepare Features ----------------------
features = ['hour', 'dayofweek', 'month', 'is_weekend',
            'lag_1', 'lag_2', 'lag_24', 'rolling_mean_3', 'rolling_mean_24']
X_live = df_live[features]

# If you trained your model using scaled features, apply same scaler here
# scaler = joblib.load("../model/scaler.pkl")
# X_live = scaler.transform(X_live)

# ---------------------- 8. Predict ----------------------
df_live['predicted_load'] = model.predict(X_live)

# ---------------------- 9. Display Latest Predictions ----------------------
print("\n🔮 Latest Real-time Energy Predictions:")
print(df_live[['load_mw', 'predicted_load']].tail(10))


