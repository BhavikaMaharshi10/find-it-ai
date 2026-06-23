import { motion } from 'framer-motion';
import { formatScore } from '../../utils/helpers';
import './MatchScoreRing.scss';

interface MatchScoreRingProps {
  score: number;
  size?: number;
  showLabel?: boolean;
}

export default function MatchScoreRing({
  score,
  size = 64,
  showLabel = true,
}: MatchScoreRingProps) {
  const strokeWidth = 4;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="match-score-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <defs>
          <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#6D5DFC" />
            <stop offset="50%" stopColor="#8B5CF6" />
            <stop offset="100%" stopColor="#A78BFA" />
          </linearGradient>
        </defs>
        <circle
          className="match-score-ring__track"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          fill="none"
        />
        <motion.circle
          className="match-score-ring__progress"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: [0.4, 0, 0.2, 1] }}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="match-score-ring__value">
        <motion.span
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.4 }}
        >
          {formatScore(score)}
        </motion.span>
        {showLabel && <span className="match-score-ring__label">match</span>}
      </div>
    </div>
  );
}
