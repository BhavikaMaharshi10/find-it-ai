import { formatScore } from '../../utils/helpers';
import Card from '../common/Card';
import './JobCard.scss';

interface JobCardProps {
  title: string;
  company: string;
  location: string;
  isRemote: boolean;
  skills: string[];
  salaryRange?: string;
  matchScore?: number;
  onSave?: () => void;
  onApply?: () => void;
  isSaved?: boolean;
}

export default function JobCard({
  title,
  company,
  location,
  isRemote,
  skills,
  salaryRange,
  matchScore,
  onSave,
  onApply,
  isSaved,
}: JobCardProps) {
  return (
    <Card className="job-card">
      <div className="job-card__header">
        <div>
          <h3 className="job-card__title">{title}</h3>
          <p className="job-card__company">{company}</p>
        </div>
        {matchScore !== undefined && (
          <div className="job-card__score">{formatScore(matchScore)}</div>
        )}
      </div>
      <div className="job-card__meta">
        <span>{isRemote ? 'Remote' : location}</span>
        {salaryRange && <span>{salaryRange}</span>}
      </div>
      <div className="job-card__skills">
        {skills.slice(0, 5).map((skill) => (
          <span key={skill} className="badge">{skill}</span>
        ))}
      </div>
      <div className="job-card__actions">
        {onSave && (
          <button type="button" className="btn btn--ghost" onClick={onSave}>
            {isSaved ? 'Saved' : 'Save'}
          </button>
        )}
        {onApply && (
          <button type="button" className="btn btn--primary" onClick={onApply}>
            Apply
          </button>
        )}
      </div>
    </Card>
  );
}
