"""Test if old prophet_model.pkl loads with current pandas/prophet versions."""
import pickle
import warnings
warnings.filterwarnings("ignore")

import pandas as pd

print("pandas version:", pd.__version__)

try:
    with open("models/prophet_model.pkl", "rb") as f:
        m = pickle.load(f)
    print("SUCCESS: Old pickle loads OK with pandas", pd.__version__)
    
    # Test making a forecast
    future = m.make_future_dataframe(periods=5)
    forecast = m.predict(future)
    print("Forecast works too:", forecast["yhat"].tail(3).values)
except Exception as e:
    print(f"FAILED: {e}")
