"""
Flask REST API exposing ML sales forecasts + inventory recommendations.

Endpoints:
  GET  /api/health
  GET  /api/forecast?days=30            -> forecast with confidence intervals
  GET  /api/history?days=90             -> recent actual sales
  GET  /api/inventory-recommendations   -> reorder alerts based on forecast vs stock
  GET  /api/model-metrics               -> ARIMA vs Prophet comparison
"""
import os
import json
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from statsmodels.tsa.arima.model import ARIMA

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.environ.get("MODEL_DIR_PATH", os.path.join(BASE_DIR, "..", "ml", "models"))

app = Flask(__name__)
CORS(app, origins=["https://sales-forecasting-seven.vercel.app", "http://localhost:5173"])

# ── Load data + metadata (no pickle) ──
with open(os.path.join(MODEL_DIR, "metadata.json")) as f:
    metadata = json.load(f)

recent_data = pd.read_csv(os.path.join(MODEL_DIR, "recent_data.csv"), parse_dates=["date"])

# Lightweight ARIMA model trained at startup from recent data
# (avoids pickle compatibility issues across pandas versions)
history_sales = recent_data["sales"].values
arima_model = ARIMA(history_sales, order=(5, 1, 2))
arima_fitted = arima_model.fit()


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "model": "arima"})


@app.route("/api/forecast")
def forecast():
    days = int(request.args.get("days", 30))
    days = min(max(days, 1), 90)  # clamp between 1-90

    forecast_result = arima_fitted.get_forecast(steps=days)
    pred = forecast_result.predicted_mean.values
    conf_int = forecast_result.conf_int(alpha=0.05)

    # Generate dates starting from the last date in recent_data
    last_date = recent_data["date"].max()
    date_range = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days)

    payload = [
        {
            "date": date.strftime("%Y-%m-%d"),
            "forecast": round(float(pred[i]), 1),
            "lower": round(float(conf_int[i, 0]), 1),
            "upper": round(float(conf_int[i, 1]), 1),
        }
        for i, date in enumerate(date_range)
    ]
    return jsonify({"days": days, "model": "arima", "forecast": payload})


@app.route("/api/history")
def history():
    days = int(request.args.get("days", 90))
    days = min(max(days, 1), len(recent_data))

    rows = recent_data.tail(days)
    payload = [
        {"date": row["date"].strftime("%Y-%m-%d"), "actual": round(row["sales"], 1)}
        for _, row in rows.iterrows()
    ]
    return jsonify({"history": payload})


@app.route("/api/inventory-recommendations")
def inventory_recommendations():
    """
    Compares 14-day forecast against average recent stock levels to flag
    products at risk of stockout or overstock.
    """
    forecast_result = arima_fitted.get_forecast(steps=14)
    pred = forecast_result.predicted_mean.values
    forecast_14d = float(pred.sum())

    avg_daily_forecast = forecast_14d / 14
    current_avg_stock = float(recent_data["stock_level"].mean()) if "stock_level" in recent_data.columns else 250.0
    days_of_stock_left = current_avg_stock / avg_daily_forecast if avg_daily_forecast > 0 else 0

    if days_of_stock_left < 7:
        alert_level = "critical"
        message = "Stock will run out in under 7 days at forecasted demand. Reorder immediately."
    elif days_of_stock_left < 14:
        alert_level = "warning"
        message = "Stock covers under 2 weeks of forecasted demand. Plan a reorder soon."
    elif days_of_stock_left > 45:
        alert_level = "overstock"
        message = "Stock levels are high relative to forecasted demand. Consider promotions to clear excess."
    else:
        alert_level = "healthy"
        message = "Stock levels are well balanced against forecasted demand."

    return jsonify({
        "forecast_14d_total": round(forecast_14d, 1),
        "avg_daily_forecast": round(avg_daily_forecast, 1),
        "current_avg_stock": round(current_avg_stock, 1),
        "estimated_days_of_stock_left": round(days_of_stock_left, 1),
        "alert_level": alert_level,
        "message": message,
    })


@app.route("/api/model-metrics")
def model_metrics():
    return jsonify(metadata)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
