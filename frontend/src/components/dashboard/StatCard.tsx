import './DashboardCharts.scss';

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: string;
  trend?: string;
}

export default function StatCard({ label, value, icon, trend }: StatCardProps) {
  return (
    <div className="stat-card">
      <div className="stat-card__header">
        {icon && <span className="stat-card__icon" aria-hidden="true">{icon}</span>}
        <span className="stat-card__label">{label}</span>
      </div>
      <div className="stat-card__value">{value}</div>
      {trend && <div className="stat-card__trend">{trend}</div>}
    </div>
  );
}
