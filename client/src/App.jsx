import { useState, useEffect } from 'react';
import { forecastService } from './services/api';
import MetricCard from './components/MetricCard';
import ForecastChart from './components/ForecastChart';
import InventoryAlert from './components/InventoryAlert';

export default function App() {
  const [history,  setHistory]  = useState([]);
  const [forecast, setForecast] = useState([]);
  const [inventory, setInventory] = useState(null);
  const [metrics,  setMetrics]  = useState(null);
  const [horizon,  setHorizon]  = useState(30);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState('');

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError('');

    Promise.all([
      forecastService.getHistory(90),
      forecastService.getForecast(horizon),
      forecastService.getInventory(),
      forecastService.getModelMetrics(),
    ])
      .then(([h, f, inv, m]) => {
        if (cancelled) return;
        setHistory(h.data.history);
        setForecast(f.data.forecast);
        setInventory(inv.data);
        setMetrics(m.data);
      })
      .catch(() => !cancelled && setError('Could not reach the forecasting API. Is the Flask server running?'))
      .finally(() => !cancelled && setLoading(false));

    return () => { cancelled = true; };
  }, [horizon]);

  const avgForecast = forecast.length
    ? Math.round(forecast.reduce((s, f) => s + f.forecast, 0) / forecast.length)
    : '—';

  return (
    <div style={S.shell}>
      <header style={S.header}>
        <div>
          <p style={S.eyebrow}>Retail demand forecasting</p>
          <h1 style={S.title}>Sales Forecasting &amp; Inventory Optimization</h1>
        </div>
        {metrics && (
          <div style={S.modelBadge}>
            <span className="mono" style={S.modelBadgeText}>
              {metrics.best_model.toUpperCase()} · {metrics.prophet_metrics.accuracy}% accuracy
            </span>
          </div>
        )}
      </header>

      {error && <div style={S.errorBox}>{error}</div>}

      {loading ? (
        <p style={S.loadingText}>Loading forecast…</p>
      ) : (
        <>
          <div style={S.metricRow}>
            <MetricCard eyebrow="Next" label={`${horizon}-day avg forecast`} value={avgForecast} unit=" units/day" accent="amber" />
            <MetricCard eyebrow="Model" label="Forecast accuracy" value={metrics?.prophet_metrics.accuracy} unit="%" accent="teal" />
            <MetricCard eyebrow="Model" label="Error (RMSE)" value={metrics?.prophet_metrics.rmse} unit=" units" accent="coral" />
          </div>

          <section style={S.chartSection}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <p style={S.sectionTitle}>Actual vs forecast</p>
              <div style={S.horizonPicker}>
                {[7, 14, 30].map((d) => (
                  <button
                    key={d}
                    onClick={() => setHorizon(d)}
                    style={{ ...S.horizonBtn, ...(horizon === d ? S.horizonBtnActive : {}) }}
                  >
                    {d}d
                  </button>
                ))}
              </div>
            </div>
            <ForecastChart history={history} forecast={forecast} />
            <div style={S.legend}>
              <span style={S.legendItem}><i style={{ ...S.legendDot, background: 'var(--teal)' }} />Actual sales</span>
              <span style={S.legendItem}><i style={{ ...S.legendDot, background: 'var(--amber)' }} />Forecast</span>
              <span style={S.legendItem}><i style={{ ...S.legendDot, background: 'var(--amber)', opacity: 0.3 }} />95% confidence interval</span>
            </div>
          </section>

          <InventoryAlert data={inventory} />
        </>
      )}
    </div>
  );
}

const S = {
  shell:     { maxWidth: 960, margin: '0 auto', padding: '2.5rem 1.5rem 4rem' },
  header:    { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 28, flexWrap: 'wrap', gap: 12 },
  eyebrow:   { fontSize: 12, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--amber)', marginBottom: 6 },
  title:     { fontSize: 22, fontWeight: 600, letterSpacing: '-0.01em' },
  modelBadge:{ background: 'var(--ink-800)', border: '1px solid var(--teal-dim)', borderRadius: 4, padding: '6px 12px' },
  modelBadgeText: { fontSize: 12, color: 'var(--teal)' },
  errorBox:  { background: 'var(--coral-dim)', color: 'var(--paper)', padding: '12px 16px', borderRadius: 4, marginBottom: 20, fontSize: 13 },
  loadingText: { color: 'var(--paper-dim)', fontSize: 14 },
  metricRow: { display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap' },
  chartSection: { background: 'var(--ink-800)', border: '1px solid var(--ink-600)', borderRadius: 4, padding: '20px 22px', marginBottom: 24 },
  sectionTitle: { fontSize: 14, fontWeight: 600 },
  horizonPicker: { display: 'flex', gap: 4, background: 'var(--ink-900)', border: '1px solid var(--ink-600)', borderRadius: 4, padding: 2 },
  horizonBtn: { background: 'transparent', border: 'none', color: 'var(--paper-dim)', fontSize: 12, padding: '4px 10px', borderRadius: 3 },
  horizonBtnActive: { background: 'var(--ink-700)', color: 'var(--amber)' },
  legend:    { display: 'flex', gap: 20, marginTop: 14, flexWrap: 'wrap' },
  legendItem:{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--paper-dim)' },
  legendDot: { width: 8, height: 8, borderRadius: 2, display: 'inline-block' },
};
