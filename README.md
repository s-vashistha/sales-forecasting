# Sales Forecasting & Inventory Optimization

A full-stack ML application that forecasts product sales using time-series models
(ARIMA + Prophet), exposes predictions through a Flask REST API, and visualizes
them in a React dashboard with confidence intervals and inventory reorder alerts.

## Architecture

```
sales-forecasting/
├── ml/                     # Data + model training (Python)
│   ├── data/
│   │   └── generate_data.py    # generates 3 years of synthetic daily sales
│   ├── preprocessing.py        # feature engineering (MAs, lags, seasonality)
│   ├── train_model.py          # trains ARIMA + Prophet, saves best model
│   ├── models/                 # saved model artifacts (generated)
│   └── requirements.txt
├── server/                 # Flask REST API
│   ├── app.py
│   ├── requirements.txt
│   ├── runtime.txt            # Pins Python 3.11 for Render compatibility
│   └── render_build.sh
└── client/                 # React dashboard
    ├── src/
    │   ├── components/
    │   │   ├── MetricCard.jsx
    │   │   ├── ForecastChart.jsx
    │   │   └── InventoryAlert.jsx
    │   ├── services/api.js
    │   └── App.jsx
    └── package.json
```

## How it works

1. **`ml/data/generate_data.py`** creates 3 years of realistic daily sales data with
   trend, weekly seasonality (weekend spikes), yearly seasonality (festive-season
   boosts), and noise.
2. **`ml/preprocessing.py`** builds features: 7/30-day moving averages, 1/7/14-day
   lag features, calendar features, and seasonal decomposition.
3. **`ml/train_model.py`** trains both ARIMA and Prophet on a train/test split,
   evaluates accuracy (MAPE, RMSE) on a held-out 30-day test window, then retrains
   the better-performing model on the full dataset for production forecasting.
4. **`server/app.py`** trains a lightweight ARIMA model at startup from recent data
   (avoids pickle version-compatibility issues) and exposes REST endpoints for
   forecasts, historical data, and inventory reorder recommendations.
5. **`client/`** is a React + Vite dashboard that charts actual vs. forecasted
   sales with a 95% confidence band, and surfaces inventory stockout/overstock
   alerts computed from the forecast.

---

## Part 1 — Install & run the ML pipeline

### 1.1 Prerequisites
- Python 3.10+
- pip

### 1.2 Set up a virtual environment
```bash
cd sales-forecasting/ml
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 1.3 Install dependencies
```bash
pip install -r requirements.txt
```

> Note: `prophet` depends on `pystan`/`cmdstanpy` and can take a few minutes to
> install on first run — this is normal.

### 1.4 Generate the dataset
```bash
cd data
python3 generate_data.py
cd ..
```
This creates `data/sales_data.csv` (3 years of daily sales).

### 1.5 Train the models
```bash
python3 train_model.py
```
This will:
- Train ARIMA and Prophet on the first ~1065 days
- Evaluate both on the last 30 days
- Print accuracy for each (Prophet typically wins, ~95%+ accuracy on this dataset)
- Retrain the winning model on the **full** dataset
- Save everything to `ml/models/`:
  - `prophet_model.pkl`, `arima_model.pkl`
  - `metadata.json` (accuracy metrics)
  - `recent_data.csv` (last 60 days, used by the API for inventory calculations)

---

## Part 2 — Install & run the Flask API

### 2.1 Set up environment
```bash
cd ../server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2.2 Run the API
```bash
python3 app.py
```
The API starts on `http://localhost:5001`. Verify it's working:
```bash
curl http://localhost:5001/api/health
# {"status": "ok", "model": "arima"}
```

### 2.3 Available endpoints
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/forecast?days=30` | Forecast + confidence interval for N days (1–90) |
| GET | `/api/history?days=90` | Recent actual sales |
| GET | `/api/inventory-recommendations` | Stock alert based on forecast vs. current stock |
| GET | `/api/model-metrics` | ARIMA vs Prophet accuracy comparison |

---

## Part 3 — Install & run the React dashboard

### 3.1 Install dependencies
```bash
cd ../client
npm install
```

### 3.2 Configure the API URL
```bash
cp .env.example .env
```
Leave `VITE_API_URL=http://localhost:5001/api` for local development.

### 3.3 Run the dev server
```bash
npm run dev
```
Open `http://localhost:5173` — you should see the dashboard with:
- Metric cards (forecast average, model accuracy, RMSE)
- Actual vs. forecast chart with a shaded confidence band
- 7/14/30-day horizon toggle
- Inventory outlook panel (critical / warning / healthy / overstock)

---

## Part 4 — Deployment

### 4.1 Deploy the Flask API to Render

1. Push the whole `sales-forecasting` folder to a GitHub repo. Render's free tier
   has an ephemeral filesystem between deploys.
2. Go to [render.com](https://render.com) → **New** → **Web Service**.
3. Connect your GitHub repo.
4. Configure:
   - **Root Directory:** `server`
   - **Build Command:** `bash render_build.sh`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Environment:** Python 3
5. The `server/runtime.txt` pins Python 3.11.11 — this is **required** because
   Render's default Python 3.14 lacks pre-built wheels for ML packages.
6. Add an environment variable so the app finds the models:
   - **Key:** `MODEL_DIR_PATH`, **Value:** `/opt/render/project/src/ml/models`
7. Click **Create Web Service**. Render will give you a URL like
   `https://sales-forecasting-api.onrender.com`.

### 4.2 Deploy the React dashboard to Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New Project**.
2. Import the same GitHub repo.
3. Configure:
   - **Root Directory:** `client`
   - **Framework Preset:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Add an environment variable:
   - `VITE_API_URL` = `https://sales-forecasting-api.onrender.com/api`
5. Click **Deploy**.

Vercel will give you a live URL, e.g. `https://sales-forecasting.vercel.app`.

### 4.3 Update CORS on the backend
In `server/app.py`, restrict CORS to your deployed frontend domain instead of `*`:
```python
CORS(app, origins=["https://sales-forecasting.vercel.app"])
```

---

## Retraining with new data

To retrain on updated sales data, replace `ml/data/sales_data.csv` with your own
data (must have `date` and `sales` columns) and re-run:
```bash
cd ml
python3 train_model.py
```
Then restart (or redeploy) the Flask API so regenerated `recent_data.csv` and
`metadata.json` are picked up.

## Tech stack

**ML:** Python, Pandas, NumPy, statsmodels (ARIMA), Prophet, scikit-learn
**Backend:** Flask, Flask-CORS, Gunicorn
**Frontend:** React 18, Vite, Recharts, Axios
**Deployment:** Render (API) + Vercel (dashboard)
