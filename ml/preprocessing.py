"""
Feature engineering pipeline:
- Moving averages (7-day, 30-day)
- Lag features (1-day, 7-day, 14-day)
- Seasonal decomposition (trend / seasonal / residual)
- Day-of-week & month encoding
"""
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose


def load_and_clean(path="data/sales_data.csv"):
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.groupby("date", as_index=False)["sales"].sum()  # aggregate all categories per day
    df = df.sort_values("date").reset_index(drop=True)

    # Handle missing dates / values
    df = df.set_index("date").asfreq("D")
    df["sales"] = df["sales"].interpolate(method="linear")
    df = df.reset_index()
    return df


def add_features(df):
    df = df.copy()

    # Moving averages
    df["ma_7"] = df["sales"].rolling(window=7, min_periods=1).mean()
    df["ma_30"] = df["sales"].rolling(window=30, min_periods=1).mean()

    # Lag features
    df["lag_1"] = df["sales"].shift(1)
    df["lag_7"] = df["sales"].shift(7)
    df["lag_14"] = df["sales"].shift(14)

    # Calendar features
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Fill NaNs created by lag/rolling windows
    df = df.bfill()
    return df


def decompose_seasonality(df, period=7):
    """Returns trend, seasonal, and residual components — used for EDA/reporting."""
    result = seasonal_decompose(df.set_index("date")["sales"], model="additive", period=period)
    return {
        "trend": result.trend,
        "seasonal": result.seasonal,
        "residual": result.resid,
    }


if __name__ == "__main__":
    df = load_and_clean()
    df = add_features(df)
    print(df.tail(10))
    print(f"\nTotal rows: {len(df)}")
    print(f"Features: {list(df.columns)}")
