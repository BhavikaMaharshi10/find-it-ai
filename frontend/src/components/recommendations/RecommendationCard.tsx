import { motion } from 'framer-motion';
import type { Recommendation } from '../../types';
import AIBadge from '../common/AIBadge';
import MatchScoreRing from '../common/MatchScoreRing';
import Button from '../common/Button';
import './RecommendationCard.scss';

interface RecommendationCardProps {
  recommendation: Recommendation;
  index?: number;
  onSave?: () => void;
  onApply?: () => void;
  isSaved?: boolean;
}

export default function RecommendationCard({
  recommendation,
  index = 0,
  onSave,
  onApply,
  isSaved,
}: RecommendationCardProps) {
  const { job, match_score, reasoning, missing_skills, strengths } = recommendation;

  return (
    <motion.article
      className="recommendation-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.08 }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
    >
      <div className="recommendation-card__glow" aria-hidden="true" />

      <div className="recommendation-card__header">
        <div className="recommendation-card__info">
          <AIBadge label="AI Match" confidence={match_score} showConfidence />
          <h3 className="recommendation-card__title">{job.title}</h3>
          <p className="recommendation-card__company">{job.company}</p>
          <div className="recommendation-card__meta">
            <span>{job.is_remote ? 'Remote' : job.location}</span>
            {job.salary_range && <span>{job.salary_range}</span>}
          </div>
        </div>
        <MatchScoreRing score={match_score} size={72} />
      </div>

      <div className="recommendation-card__skills">
        {job.required_skills.slice(0, 5).map((skill) => (
          <span key={skill} className="badge">{skill}</span>
        ))}
      </div>

      <div className="recommendation-card__insight">
        <div className="recommendation-card__insight-header">
          <span className="recommendation-card__insight-label">AI Explanation</span>
        </div>
        <p className="recommendation-card__reasoning">{reasoning}</p>
      </div>

      {strengths.length > 0 && (
        <div className="recommendation-card__strengths">
          <span className="recommendation-card__section-label">Your strengths</span>
          <div className="recommendation-card__tags">
            {strengths.map((s) => (
              <span key={s} className="badge badge--success">{s}</span>
            ))}
          </div>
        </div>
      )}

      {missing_skills.length > 0 && (
        <div className="recommendation-card__gaps">
          <span className="recommendation-card__section-label">Missing skills</span>
          <div className="recommendation-card__tags">
            {missing_skills.map((s) => (
              <span key={s} className="badge badge--warning">{s}</span>
            ))}
          </div>
        </div>
      )}

      <div className="recommendation-card__actions">
        {onSave && (
          <Button variant="secondary" onClick={onSave}>
            {isSaved ? 'Saved' : 'Save'}
          </Button>
        )}
        {onApply && (
          <Button onClick={onApply}>Quick Apply</Button>
        )}
      </div>
    </motion.article>
  );
}
