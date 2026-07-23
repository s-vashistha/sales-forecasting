import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';

export default function ForecastChart({ history, forecast }) {
  // Merge actual history + forecast into one continuous series for the chart.
  const combined = [
    ...history.map((h) => ({ date: h.date, actual: h.actual })),
    ...forecast.map((f) => ({ date: f.date, forecast: f.forecast, band: [f.lower, f.upper] })),
  ];

  const splitDate = forecast[0]?.date;

  return (
    <div style={{ width: '100%', height: 340 }}>
      <ResponsiveContainer>
        <ComposedChart data={combined} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="var(--ink-700)" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fill: 'var(--paper-dim)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
            tickFormatter={(d) => d.slice(5)}
            interval={Math.floor(combined.length / 8)}
            axisLine={{ stroke: 'var(--ink-600)' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: 'var(--paper-dim)', fontSize: 11, fontFamily: 'var(--font-mono)' }}
            axisLine={false}
            tickLine={false}
            width={36}
          />
          <Tooltip content={<CustomTooltip />} />

          {/* Confidence band (only exists for forecast rows) */}
          <Area
            dataKey="band"
            stroke="none"
            fill="var(--amber)"
            fillOpacity={0.12}
            isAnimationActive={false}
          />

          <Line
            dataKey="actual"
            stroke="var(--teal)"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
          <Line
            dataKey="forecast"
            stroke="var(--amber)"
            strokeWidth={2}
            strokeDasharray="5 3"
            dot={false}
            isAnimationActive={false}
          />

          {splitDate && (
            <ReferenceLine x={splitDate} stroke="var(--ink-600)" strokeDasharray="2 2" />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const row = payload[0]?.payload;

  return (
    <div style={{ background: 'var(--ink-700)', border: '1px solid var(--ink-600)', borderRadius: 4, padding: '10px 12px' }}>
      <p className="mono" style={{ fontSize: 11, color: 'var(--paper-dim)', marginBottom: 6 }}>{label}</p>
      {row.actual != null && (
        <p className="mono" style={{ fontSize: 13, color: 'var(--teal)' }}>Actual: {row.actual}</p>
      )}
      {row.forecast != null && (
        <>
          <p className="mono" style={{ fontSize: 13, color: 'var(--amber)' }}>Forecast: {row.forecast}</p>
          <p className="mono" style={{ fontSize: 11, color: 'var(--paper-dim)' }}>
            Range: {row.band?.[0]} – {row.band?.[1]}
          </p>
        </>
      )}
    </div>
  );
}
