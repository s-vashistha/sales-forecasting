const ALERT_STYLE = {
  critical:  { color: 'var(--coral)', bg: 'var(--coral-dim)', label: 'Critical' },
  warning:   { color: 'var(--amber)', bg: 'var(--amber-dim)', label: 'Warning' },
  healthy:   { color: 'var(--teal)',  bg: 'var(--teal-dim)',  label: 'Healthy' },
  overstock: { color: 'var(--amber)', bg: 'var(--amber-dim)', label: 'Overstock' },
};

export default function InventoryAlert({ data }) {
  if (!data) return null;
  const style = ALERT_STYLE[data.alert_level] || ALERT_STYLE.healthy;

  return (
    <div style={S.panel}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <p style={S.title}>Inventory outlook</p>
        <span style={{ ...S.badge, color: style.color, borderColor: style.color }}>{style.label}</span>
      </div>

      <p style={S.message}>{data.message}</p>

      <div style={S.statGrid}>
        <div>
          <p style={S.statLabel}>Days of stock left</p>
          <p className="mono" style={{ ...S.statValue, color: style.color }}>
            {data.estimated_days_of_stock_left}
          </p>
        </div>
        <div>
          <p style={S.statLabel}>14-day forecast</p>
          <p className="mono" style={S.statValue}>{data.forecast_14d_total} units</p>
        </div>
        <div>
          <p style={S.statLabel}>Avg daily demand</p>
          <p className="mono" style={S.statValue}>{data.avg_daily_forecast} units</p>
        </div>
        <div>
          <p style={S.statLabel}>Current avg stock</p>
          <p className="mono" style={S.statValue}>{data.current_avg_stock} units</p>
        </div>
      </div>
    </div>
  );
}

const S = {
  panel:     { background: 'var(--ink-800)', border: '1px solid var(--ink-600)', borderRadius: 4, padding: '20px 22px' },
  title:     { fontSize: 14, fontWeight: 600, letterSpacing: '0.02em' },
  badge:     { fontSize: 11, fontWeight: 600, padding: '3px 10px', borderRadius: 3, border: '1px solid', textTransform: 'uppercase', letterSpacing: '0.04em' },
  message:   { fontSize: 13, color: 'var(--paper-dim)', lineHeight: 1.6, marginBottom: 20 },
  statGrid:  { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px 20px' },
  statLabel: { fontSize: 11, color: 'var(--paper-dim)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.04em' },
  statValue: { fontSize: 16, fontWeight: 600 },
};
