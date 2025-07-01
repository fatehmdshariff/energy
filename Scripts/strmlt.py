import streamlit as st
import pandas as pd
import joblib
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ---------------------- 1. Load environment variables ----------------------
load_dotenv()
API_KEY = os.getenv("EIA_API_KEY")

# ---------------------- 2. Page settings ----------------------
st.set_page_config(page_title="Live Energy Load Forecast", layout="wide")
st.title("🔌 Real-Time Energy Load Forecast")

# ---------------------- 3. Load model ----------------------
model = joblib.load("../models/rf_model_eia_2023.pkl")

# ---------------------- 4. Fetch latest data ----------------------
@st.cache_data(show_spinner=True)
def fetch_latest_data():
    url = f"https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key={API_KEY}&frequency=hourly&data[0]=value&facets[respondent][]=CAL"
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Failed to fetch live data. Check API key or endpoint.")
        return None

    data = response.json()
    records = data['response']['data']
    df = pd.DataFrame(records)

    # Clean and format
    df['datetime'] = pd.to_datetime(df['period'])
    df['load_mw'] = pd.to_numeric(df['value'], errors='coerce')
    df = df[['datetime', 'load_mw']]
    df = df.dropna()
    df = df.sort_values('datetime')
    df = df.set_index('datetime')
    return df

# ---------------------- 5. Feature engineering ----------------------
@st.cache_data(show_spinner=False)
def prepare_features(df):
    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['month'] = df.index.month
    df['is_weekend'] = df['dayofweek'].apply(lambda x: 1 if x >= 5 else 0)
    df['lag_1'] = df['load_mw'].shift(1)
    df['lag_2'] = df['load_mw'].shift(2)
    df['lag_24'] = df['load_mw'].shift(24)
    df['rolling_mean_3'] = df['load_mw'].rolling(window=3).mean()
    df['rolling_mean_24'] = df['load_mw'].rolling(window=24).mean()
    df = df.dropna()
    return df

# ---------------------- 6. Prediction ----------------------
@st.cache_data(show_spinner=False)
def predict(df, _model):
    features = ['hour', 'dayofweek', 'month', 'is_weekend',
                'lag_1', 'lag_2', 'lag_24', 'rolling_mean_3', 'rolling_mean_24']
    X = df[features]
    df['predicted_load'] = _model.predict(X)
    return df

# ---------------------- 7. Main execution ----------------------
with st.spinner("Fetching live data and generating predictions..."):
    df_live = fetch_latest_data()
    if df_live is not None:
        df_ready = prepare_features(df_live)
        df_final = predict(df_ready, model)

        # Reset index and format datetime for display
        df_display = df_final[['load_mw', 'predicted_load']].copy()
        df_display = df_display.reset_index()
        df_display['datetime'] = df_display['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Display data table
        st.subheader("📊 Latest Actual vs Predicted Load")
        st.dataframe(df_display.tail(10), use_container_width=True)

        # Evaluation metrics
        mae = mean_absolute_error(df_final['load_mw'], df_final['predicted_load'])
        rmse = mean_squared_error(df_final['load_mw'], df_final['predicted_load']) ** 0.5
        r2 = r2_score(df_final['load_mw'], df_final['predicted_load'])

        # Show metrics
        st.subheader("📈 Model Evaluation (Live Data)")
        col1, col2, col3 = st.columns(3)
        col1.metric("MAE (MW)", f"{mae:.2f}")
        col2.metric("RMSE (MW)", f"{rmse:.2f}")
        col3.metric("R² Score", f"{r2:.4f}")

        # Plot chart
        st.subheader("📉 Load Over Time")
        df_chart = df_final[['load_mw', 'predicted_load']].astype('float').dropna()
        st.line_chart(df_chart)
