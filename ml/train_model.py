"""
Trains both ARIMA and Prophet models on the sales data, evaluates on a held-out
test set (last 30 days), and saves the best-performing model + metadata.

Run:  python train_model.py
"""
import pandas as pd
import numpy as np
import pickle
import json
import warnings
warnings.filterwarnings("ignore")

from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet

from preprocessing import load_and_clean, add_features

TEST_DAYS = 30
MODEL_DIR = "models"


def train_arima(train_df, test_df):
    model = ARIMA(train_df["sales"], order=(5, 1, 2))
    fitted = model.fit()
    forecast = fitted.get_forecast(steps=len(test_df))
    pred = forecast.predicted_mean.values
    conf_int = forecast.conf_int(alpha=0.05)  # 95% confidence interval
    return fitted, pred, conf_int


def train_prophet(train_df):
    prophet_df = train_df[["date", "sales"]].rename(columns={"date": "ds", "sales": "y"})
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.95,
    )
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=TEST_DAYS)
    forecast = model.predict(future)
    pred = forecast["yhat"].values[-TEST_DAYS:]
    lower = forecast["yhat_lower"].values[-TEST_DAYS:]
    upper = forecast["yhat_upper"].values[-TEST_DAYS:]
    return model, pred, lower, upper


def evaluate(actual, predicted):
    mape = mean_absolute_percentage_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    accuracy = max(0, (1 - mape)) * 100
    return {"mape": round(mape * 100, 2), "rmse": round(rmse, 2), "accuracy": round(accuracy, 2)}


def main():
    print("Loading and preparing data...")
    df = load_and_clean("data/sales_data.csv")
    df = add_features(df)

    train_df = df.iloc[:-TEST_DAYS].reset_index(drop=True)
    test_df = df.iloc[-TEST_DAYS:].reset_index(drop=True)
    actual = test_df["sales"].values

    print("\nTraining ARIMA...")
    arima_model, arima_pred, arima_conf = train_arima(train_df, test_df)
    arima_metrics = evaluate(actual, arima_pred)
    print(f"ARIMA  -> Accuracy: {arima_metrics['accuracy']}% | RMSE: {arima_metrics['rmse']}")

    print("\nTraining Prophet...")
    prophet_model, prophet_pred, prophet_lower, prophet_upper = train_prophet(train_df)
    prophet_metrics = evaluate(actual, prophet_pred)
    print(f"Prophet -> Accuracy: {prophet_metrics['accuracy']}% | RMSE: {prophet_metrics['rmse']}")

    # Pick the best model
    best_is_prophet = prophet_metrics["accuracy"] >= arima_metrics["accuracy"]
    best_name = "prophet" if best_is_prophet else "arima"
    best_metrics = prophet_metrics if best_is_prophet else arima_metrics

    print(f"\nBest model: {best_name.upper()} ({best_metrics['accuracy']}% accuracy)")

    import os
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Retrain on the FULL dataset (train + test) so the saved model's future
    # forecasts start from the true latest date, not from the train-split cutoff.
    print("\nRetraining best model on full dataset for production use...")
    full_prophet_df = df[["date", "sales"]].rename(columns={"date": "ds", "sales": "y"})
    production_model = Prophet(
        yearly_seasonality=True, weekly_seasonality=True,
        daily_seasonality=False, interval_width=0.95,
    )
    production_model.fit(full_prophet_df)

    # Save Prophet model (used in production API)
    with open(f"{MODEL_DIR}/prophet_model.pkl", "wb") as f:
        pickle.dump(production_model, f)

    # Save ARIMA model too (for comparison endpoint)
    with open(f"{MODEL_DIR}/arima_model.pkl", "wb") as f:
        pickle.dump(arima_model, f)


    # Save metadata
    metadata = {
        "best_model": best_name,
        "arima_metrics": arima_metrics,
        "prophet_metrics": prophet_metrics,
        "trained_on_rows": len(train_df),
        "test_days": TEST_DAYS,
        "last_training_date": str(df["date"].max().date()),
    }
    with open(f"{MODEL_DIR}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Save last 60 days of processed data (for feature continuity in API)
    df.tail(60).to_csv(f"{MODEL_DIR}/recent_data.csv", index=False)

    print(f"\nModels saved to {MODEL_DIR}/")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
