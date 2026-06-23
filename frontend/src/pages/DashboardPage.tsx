import { BarChart } from '../components/dashboard/BarChart';
import StatCard from '../components/dashboard/StatCard';
import Button from '../components/common/Button';
import {
  useApplicationStatus,
  useApplicationTrends,
  useDashboardStats,
  useMatchDistribution,
  useRefreshRecommendations,
  useSkillGaps,
} from '../hooks/useDashboard';
import { formatScore } from '../utils/helpers';
import '../components/dashboard/DashboardCharts.scss';

export default function DashboardPage() {
  const { data: stats, isLoading } = useDashboardStats();
  const { data: matchDist } = useMatchDistribution();
  const { data: skillGaps } = useSkillGaps();
  const { data: appTrends } = useApplicationTrends();
  const { data: appStatus } = useApplicationStatus();
  const refreshRecs = useRefreshRecommendations();

  if (isLoading) return <p>Loading dashboard...</p>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1>Dashboard</h1>
          <p className="text-secondary">Your job search overview</p>
        </div>
        <Button onClick={() => refreshRecs.mutate()} loading={refreshRecs.isPending}>
          Refresh Recommendations
        </Button>
      </div>

      <div className="dashboard-grid dashboard-grid--stats">
        <StatCard label="Jobs Found" value={stats?.jobs_found ?? 0} icon="🔍" />
        <StatCard label="Saved Jobs" value={stats?.saved_jobs ?? 0} icon="🔖" />
        <StatCard label="Applications" value={stats?.applications_sent ?? 0} icon="📋" />
        <StatCard label="Avg Match Score" value={formatScore(stats?.average_match_score ?? 0)} icon="✨" />
      </div>

      <div className="dashboard-grid dashboard-grid--charts">
        {matchDist && <BarChart data={matchDist} title="Match Score Distribution" />}
        {skillGaps && (
          <BarChart
            data={skillGaps.map((g) => ({ label: g.skill, value: g.count }))}
            title="Skill Gap Analysis"
          />
        )}
        {appStatus && (
          <BarChart
            data={appStatus.map((s) => ({ label: s.status.replace(/_/g, ' '), value: s.count }))}
            title="Application Status"
          />
        )}
        {appTrends && appTrends.length > 0 && (
          <BarChart
            data={appTrends.map((t) => ({ label: t.applied_date, value: t.count }))}
            title="Application Trends"
          />
        )}
      </div>
    </div>
  );
}
