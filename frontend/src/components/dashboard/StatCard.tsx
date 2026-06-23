import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import AnimatedCounter from '../common/AnimatedCounter';
import './DashboardCharts.scss';

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  trend?: string;
  numericValue?: number;
  suffix?: string;
}

export default function StatCard({ label, value, icon, trend, numericValue, suffix }: StatCardProps) {
  return (
    <motion.div
      className="stat-card"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
    >
      <div className="stat-card__glow" aria-hidden="true" />
      <div className="stat-card__header">
        {icon && <span className="stat-card__icon">{icon}</span>}
        <span className="stat-card__label">{label}</span>
      </div>
      <div className="stat-card__value">
        {numericValue !== undefined ? (
          <AnimatedCounter value={numericValue} suffix={suffix} />
        ) : (
          value
        )}
      </div>
      {trend && <div className="stat-card__trend">{trend}</div>}
    </motion.div>
  );
}
