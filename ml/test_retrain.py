import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
print("pandas:", pd.__version__)
print("numpy:", np.__version__)

from prophet import Prophet
print("prophet imported OK")

from preprocessing import load_and_clean, add_features
print("preprocessing imported OK")

df = load_and_clean("data/sales_data.csv")
df = add_features(df)
print("data ready, rows:", len(df))

train_df = df.iloc[:-30].reset_index(drop=True)
test_df = df.iloc[-30:].reset_index(drop=True)
print("train:", len(train_df), "test:", len(test_df))

from statsmodels.tsa.arima.model import ARIMA
model = ARIMA(train_df["sales"], order=(5, 1, 2))
fitted = model.fit()
print("ARIMA trained OK")

forecast = fitted.get_forecast(steps=30)
pred = forecast.predicted_mean.values
print("ARIMA pred OK")

prophet_df = train_df[["date", "sales"]].rename(columns={"date": "ds", "sales": "y"})
m = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    interval_width=0.95,
)
m.fit(prophet_df)
print("Prophet trained OK!")

print("\nAll checks passed! Ready for full retrain.")
