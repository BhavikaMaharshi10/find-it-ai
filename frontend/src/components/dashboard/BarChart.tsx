import './DashboardCharts.scss';

interface BarChartProps {
  data: Record<string, number> | { label: string; value: number }[];
  title: string;
}

export function BarChart({ data, title }: BarChartProps) {
  const items = Array.isArray(data)
    ? data.map((d) => ({ label: d.label, value: d.value }))
    : Object.entries(data).map(([label, value]) => ({ label, value }));

  const max = Math.max(...items.map((i) => i.value), 1);

  return (
    <div className="chart-card">
      <h3>{title}</h3>
      <div className="bar-chart">
        {items.map((item) => (
          <div key={item.label} className="bar-chart__row">
            <span className="bar-chart__label">{item.label}</span>
            <div className="bar-chart__bar-wrap">
              <div
                className="bar-chart__bar"
                style={{ width: `${(item.value / max) * 100}%` }}
              />
            </div>
            <span className="bar-chart__value">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
