import MatchScoreRing from '../common/MatchScoreRing';
import Button from '../common/Button';
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
    <article className="job-card">
      <div className="job-card__header">
        <div className="job-card__info">
          <h3 className="job-card__title">{title}</h3>
          <p className="job-card__company">{company}</p>
        </div>
        {matchScore !== undefined && (
          <MatchScoreRing score={matchScore} size={56} showLabel={false} />
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
          <Button variant="secondary" size="sm" onClick={onSave}>
            {isSaved ? 'Saved' : 'Save'}
          </Button>
        )}
        {onApply && (
          <Button size="sm" onClick={onApply}>
            Quick Apply
          </Button>
        )}
      </div>
    </article>
  );
}
