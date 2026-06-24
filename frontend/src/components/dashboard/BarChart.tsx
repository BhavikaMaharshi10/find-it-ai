import { motion } from 'framer-motion';
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
    <motion.div
      className="chart-card"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <h3>{title}</h3>
      <div className="bar-chart">
        {items.map((item, i) => (
          <div key={item.label} className="bar-chart__row">
            <span className="bar-chart__label">{item.label}</span>
            <div className="bar-chart__bar-wrap">
              <motion.div
                className="bar-chart__bar"
                initial={{ width: 0 }}
                animate={{ width: `${(item.value / max) * 100}%` }}
                transition={{ duration: 0.8, delay: i * 0.05, ease: [0.4, 0, 0.2, 1] }}
              />
            </div>
            <span className="bar-chart__value">{item.value}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
