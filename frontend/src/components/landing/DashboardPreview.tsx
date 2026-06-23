import { motion } from 'framer-motion';
import './DashboardPreview.scss';

const MOCK_STATS = [
  { label: 'Match Score', value: '94%', color: '#6D5DFC' },
  { label: 'Jobs Found', value: '127', color: '#8B5CF6' },
  { label: 'Applications', value: '12', color: '#A78BFA' },
];

const MOCK_JOBS = [
  { title: 'Senior ML Engineer', company: 'Anthropic', score: 94 },
  { title: 'AI Product Lead', company: 'Linear', score: 89 },
  { title: 'Staff Engineer', company: 'Vercel', score: 86 },
];

export default function DashboardPreview() {
  return (
    <motion.div
      className="dashboard-preview"
      initial={{ opacity: 0, y: 40, rotateX: 8 }}
      animate={{ opacity: 1, y: 0, rotateX: 0 }}
      transition={{ duration: 0.8, delay: 0.3, ease: [0.4, 0, 0.2, 1] }}
    >
      <div className="dashboard-preview__chrome">
        <div className="dashboard-preview__dots">
          <span /><span /><span />
        </div>
        <span className="dashboard-preview__url">app.finditai.com/dashboard</span>
      </div>

      <div className="dashboard-preview__body">
        <div className="dashboard-preview__stats">
          {MOCK_STATS.map((stat, i) => (
            <motion.div
              key={stat.label}
              className="dashboard-preview__stat"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + i * 0.1 }}
            >
              <span className="dashboard-preview__stat-label">{stat.label}</span>
              <span className="dashboard-preview__stat-value" style={{ color: stat.color }}>
                {stat.value}
              </span>
            </motion.div>
          ))}
        </div>

        <div className="dashboard-preview__section">
          <div className="dashboard-preview__section-header">
            <span className="ai-badge">AI Matches</span>
          </div>
          {MOCK_JOBS.map((job, i) => (
            <motion.div
              key={job.title}
              className="dashboard-preview__job"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 + i * 0.1 }}
            >
              <div>
                <div className="dashboard-preview__job-title">{job.title}</div>
                <div className="dashboard-preview__job-company">{job.company}</div>
              </div>
              <div className="dashboard-preview__job-score">{job.score}%</div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
