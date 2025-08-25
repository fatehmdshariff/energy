
# ⚡ Energy Load Forecasting Dashboard (EIA API)

This project provides a real-time dashboard to monitor, forecast, and evaluate electricity consumption using machine learning.
It leverages the U.S. Energy Information Administration (EIA) API to fetch hourly electricity usage, trains a Random Forest model, and visualizes predictions through an interactive Streamlit app.

📌 Features

🔄 Fetches real-time and historical load data from the EIA API

🤖 Trains and re-trains Random Forest regression models

📊 Streamlit dashboard to visualize actual vs predicted load

📈 Tracks model performance with MAE, RMSE, and R² Score

📥 Automatically saves datasets and trained models for reuse

🗂 Project Structure
energy/
│
├── Datasets/
│   ├── eia_training_data_2023.csv          # Cleaned historical load data
│   └── household_power_consumption.txt     # (Additional UCI dataset)
│
├── models/
│   ├── model_metadata.txt                  # Metadata (training timestamp, etc.)
│   ├── rf_features.pkl                     # Saved feature set
│   ├── rf_model_eia_2023.pkl               # Trained RF model on EIA dataset
│   ├── rf_model_hourly_latest.pkl          # Latest updated model
│   └── rf_model_hourly.pkl                 # Alternate model version
│
├── Scripts/
│   ├── Model_eval_EIA.ipynb                # EIA dataset evaluation notebook
│   ├── model_eval_UCI.ipynb                # UCI dataset evaluation notebook
│   ├── retrain_model_energy.py             # Re-trains RF model using new data
│   ├── strmlt.py                           # Streamlit dashboard app
│   └── training_dataa.py                   # Downloads & saves 2023 training data
│
├── .env                                    # API key (not committed)
├── .gitignore                              # Ignore .env, models, and generated files
├── LICENSE                                 # MIT License
├── README.md                               # Project documentation
└── requirements.txt                        # Required Python packages

🚀 Setup Instructions
1. Clone the Repository
git clone https://github.com/fatehmdshariff/energy.git
cd energy

2. Install Dependencies
pip install -r requirements.txt

3. Add Your API Key

Create a .env file in the root directory and add your EIA API key:

EIA_API_KEY=your_api_key_here https://www.eia.gov/opendata/register.php

🛠 Usage
✅ Fetch Historical Data (optional)
python Scripts/training_dataa.py

🔁 Retrain the Model
python Scripts/retrain_model_energy.py

📺 Launch the Streamlit Dashboard
streamlit run Scripts/strmlt.py

🧠 Machine Learning Model

Algorithm: Random Forest Regressor

Feature Engineering:

Hour of the day

Day of the week

Month of the year

Weekend indicator

Lag features (t-1, t-2, t-24)

Rolling mean features (3-hour, 24-hour averages)

📊 Model Performance
Metric	Value
MAE	608.48
RMSE	1140.39
R²	0.9932

✅ Captures both hourly and daily patterns
✅ Low error values → accurate short-term predictions
✅ High R² (~0.99) → explains nearly all variance

📚 Notebooks

Model_eval_EIA.ipynb: Training & evaluation using the EIA dataset

model_eval_UCI.ipynb: Experimental testing on UCI household dataset

🚧 Future Improvements

Add LSTM / GRU deep learning models for better sequence modeling

Enable region/zone selection via dropdown in the dashboard

Automate weekly retraining with Windows Scheduler / Cron

Deploy to Streamlit Cloud / Heroku

Add alerts for demand anomalies

🙌 Author

Fateh Mohammed Shariff
📍 Bangalore, India
🔗 GitHub

📄 License

This project is licensed under the MIT License.