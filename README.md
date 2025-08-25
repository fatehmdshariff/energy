# ⚡ Energy Load Forecasting Dashboard (EIA API)

This project provides a **real-time dashboard** to monitor, forecast, and evaluate electricity consumption using ML.  
It pulls **hourly California load** from the **U.S. Energy Information Administration (EIA)** API, trains a **Random Forest** model, and visualizes predictions in a **Streamlit** app.

---

## 📌 Features
- 🔄 Fetches **real-time & historical** data from EIA
- 🤖 Trains and **re-trains** Random Forest regression models
- 📊 **Streamlit** dashboard (actual vs. predicted)
- 📈 Tracks **MAE, RMSE, R²**
- 💾 Saves datasets & trained models

---

## 🗂 Project Structure
```text
energy/
├── Datasets/
│   ├── eia_training_data_2023.csv          # Cleaned historical load data
│   └── household_power_consumption.txt     # (Additional UCI dataset)
├── models/
│   ├── model_metadata.txt                  # Metadata (training timestamp, etc.)
│   ├── rf_features.pkl                     # Saved feature list
│   ├── rf_model_eia_2023.pkl               # Trained RF model on EIA
│   ├── rf_model_hourly_latest.pkl          # Latest hourly model
│   └── rf_model_hourly.pkl                 # Alternate hourly model
├── Scripts/
│   ├── Model_eval_EIA.ipynb                # EIA model eval notebook
│   ├── model_eval_UCI.ipynb                # UCI dataset exploration
│   ├── retrain_model_energy.py             # Weekly retrain script (manual run)
│   ├── strmlt.py                           # Streamlit app
│   └── training_dataa.py                   # Downloads 2023 training data
├── .env                                    # EIA_API_KEY=... (not committed)
├── .gitignore                              # Ignores .env and generated files
├── LICENSE                                 # MIT
└── requirements.txt                        # Python dependencies


🚀 Setup
# 1) Clone
git clone https://github.com/fatehmdshariff/energy.git
cd energy

# 2) (Optional) Create venv
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3) Install
pip install -r requirements.txt



🔑 Set your API key
Create a .env file in the repo root:
EIA_API_KEY=your_api_key_here
Get a free key: https://www.eia.gov/opendata/register.php


🛠 Usage

Fetch historical data (optional)
python Scripts/training_dataa.py

Retrain the model (adds latest hourly data, updates model)
python Scripts/retrain_model_energy.py

Launch the Streamlit dashboard
streamlit run Scripts/strmlt.py



🧠 Model & Features

Algorithm: Random Forest Regressor

Features used:

hour, day_of_week, month, is_weekend

Lags: load_mw.shift(1), shift(2), shift(24)

shift(1) → previous hour

shift(24) → same hour yesterday (captures daily pattern)

Rolling means: rolling(window=3).mean(), rolling(window=24).mean()

smooth short-term noise and capture day-level trend

📊 Performance (latest run)
Metric	Value
MAE	608.48
RMSE	1140.39
R²	0.9932

Trained on California hourly load; model captures strong hourly & daily seasonality.

🧪 Notebooks

Scripts/Model_eval_EIA.ipynb — training & evaluation on EIA data

Scripts/model_eval_UCI.ipynb — exploratory/experimental UCI analysis

🔁 Retraining (planned automation)

Script: Scripts/retrain_model_energy.py (currently run manually weekly)

Next: schedule via Windows Task Scheduler or cron to:

pull latest hourly data (EIA),

append to dataset,

retrain & overwrite rf_model_hourly_latest.pkl,

log metrics in models/model_metadata.txt.

📦 Deploy (optional)

Streamlit Cloud: push repo and set EIA_API_KEY as a secret

Heroku/Render: add buildpack for Python, run streamlit run Scripts/strmlt.py

🙌 Author

Fateh Mohammed Shariff — Bangalore, India
GitHub: https://github.com/fatehmdshariff

📄 License
MIT License

