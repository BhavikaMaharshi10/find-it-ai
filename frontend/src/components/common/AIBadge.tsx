import { IconSparkles } from './Icons';
import './AIBadge.scss';

interface AIBadgeProps {
  label?: string;
  confidence?: number;
  showConfidence?: boolean;
}

export default function AIBadge({
  label = 'AI Insight',
  confidence,
  showConfidence = false,
}: AIBadgeProps) {
  return (
    <span className="ai-badge-component">
      <IconSparkles size={12} />
      <span>{label}</span>
      {showConfidence && confidence !== undefined && (
        <span className="ai-badge-component__confidence">{Math.round(confidence)}%</span>
      )}
    </span>
  );
}
