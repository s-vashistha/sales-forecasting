"""
Generates 3 years of realistic daily sales data with:
- Upward trend
- Weekly seasonality (weekend spikes)
- Yearly seasonality (festive/holiday spikes in Oct-Dec)
- Random noise
Simulates a retail business (e.g. electronics store) - realistic for a portfolio project.
"""
import pandas as pd
import numpy as np

np.random.seed(42)

def generate_sales_data(start_date="2023-01-01", days=1095, out_path="sales_data.csv"):
    dates = pd.date_range(start=start_date, periods=days, freq="D")

    # Base trend: slow linear growth
    trend = np.linspace(200, 350, days)

    # Weekly seasonality: higher sales on weekends (Sat/Sun)
    weekday = dates.dayofweek
    weekly_effect = np.where(weekday >= 5, 40, 0)

    # Yearly seasonality: festive season boost (Oct-Dec) + summer dip (Apr-May)
    day_of_year = dates.dayofyear
    yearly_effect = 60 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
    festive_boost = np.where(dates.month.isin([10, 11, 12]), 70, 0)

    # Random noise
    noise = np.random.normal(0, 20, days)

    sales = trend + weekly_effect + yearly_effect + festive_boost + noise
    sales = np.clip(sales, 20, None).round(0)

    df = pd.DataFrame({
        "date": dates,
        "sales": sales,
        "product_category": np.random.choice(
            ["Electronics", "Apparel", "Home & Kitchen", "Groceries"], days,
            p=[0.35, 0.25, 0.2, 0.2]
        ),
        "units_sold": (sales / np.random.uniform(15, 25, days)).round(0).astype(int),
        "stock_level": np.random.randint(50, 500, days),
    })

    df.to_csv(out_path, index=False)
    print(f"Generated {days} days of sales data -> {out_path}")
    return df

if __name__ == "__main__":
    generate_sales_data()
