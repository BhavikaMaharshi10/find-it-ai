import { BarChart } from '../components/dashboard/BarChart';
import StatCard from '../components/dashboard/StatCard';
import Button from '../components/common/Button';
import AIBadge from '../components/common/AIBadge';
import {
  IconSearch,
  IconBookmark,
  IconClipboard,
  IconSparkles,
} from '../components/common/Icons';
import {
  useApplicationStatus,
  useApplicationTrends,
  useDashboardStats,
  useMatchDistribution,
  useRefreshRecommendations,
  useSkillGaps,
} from '../hooks/useDashboard';
import '../components/dashboard/DashboardCharts.scss';

export default function DashboardPage() {
  const { data: stats, isLoading } = useDashboardStats();
  const { data: matchDist } = useMatchDistribution();
  const { data: skillGaps } = useSkillGaps();
  const { data: appTrends } = useApplicationTrends();
  const { data: appStatus } = useApplicationStatus();
  const refreshRecs = useRefreshRecommendations();

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <div className="dashboard-loading__spinner" />
        <span>Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-page__header">
        <div className="dashboard-page__title-group">
          <AIBadge label="Overview" />
          <h1>Dashboard</h1>
          <p className="text-secondary">Your job search intelligence at a glance</p>
        </div>
        <Button onClick={() => refreshRecs.mutate()} loading={refreshRecs.isPending}>
          Refresh Recommendations
        </Button>
      </div>

      <div className="dashboard-grid dashboard-grid--stats">
        <StatCard
          label="Jobs Found"
          value={stats?.jobs_found ?? 0}
          numericValue={stats?.jobs_found ?? 0}
          icon={<IconSearch size={18} />}
        />
        <StatCard
          label="Saved Jobs"
          value={stats?.saved_jobs ?? 0}
          numericValue={stats?.saved_jobs ?? 0}
          icon={<IconBookmark size={18} />}
        />
        <StatCard
          label="Applications"
          value={stats?.applications_sent ?? 0}
          numericValue={stats?.applications_sent ?? 0}
          icon={<IconClipboard size={18} />}
        />
        <StatCard
          label="Avg Match Score"
          value={`${Math.round(stats?.average_match_score ?? 0)}%`}
          numericValue={stats?.average_match_score ?? 0}
          suffix="%"
          icon={<IconSparkles size={18} />}
        />
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
