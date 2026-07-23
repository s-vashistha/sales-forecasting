export default function MetricCard({ label, value, unit, accent = 'amber', eyebrow }) {
  const accentColor = { amber: 'var(--amber)', teal: 'var(--teal)', coral: 'var(--coral)' }[accent];

  return (
    <div style={S.card}>
      {eyebrow && <p style={S.eyebrow}>{eyebrow}</p>}
      <p style={S.label}>{label}</p>
      <p className="mono" style={{ ...S.value, color: accentColor }}>
        {value}<span style={S.unit}>{unit}</span>
      </p>
    </div>
  );
}

const S = {
  card:    { background: 'var(--ink-800)', border: '1px solid var(--ink-600)', borderRadius: 4, padding: '18px 20px', flex: 1, minWidth: 0 },
  eyebrow: { fontSize: 11, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--paper-dim)', marginBottom: 6 },
  label:   { fontSize: 13, color: 'var(--paper-dim)', marginBottom: 8 },
  value:   { fontSize: 28, fontWeight: 600, lineHeight: 1 },
  unit:    { fontSize: 14, fontWeight: 400, marginLeft: 4, color: 'var(--paper-dim)' },
};
