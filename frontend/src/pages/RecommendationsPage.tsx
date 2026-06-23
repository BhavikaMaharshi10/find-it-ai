import { useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { recommendationsApi } from '../api/endpoints';
import Button from '../components/common/Button';
import AIBadge from '../components/common/AIBadge';
import RecommendationCard from '../components/recommendations/RecommendationCard';
import '../components/recommendations/RecommendationCard.scss';

function collectSkillGaps(recommendations: { missing_skills: string[] }[] | undefined) {
  if (!recommendations?.length) return [];

  const seen = new Set<string>();
  const gaps: string[] = [];
  for (const rec of recommendations) {
    for (const skill of rec.missing_skills ?? []) {
      const key = skill.toLowerCase().trim();
      if (key && !seen.has(key)) {
        seen.add(key);
        gaps.push(skill);
      }
    }
  }
  return gaps;
}

export default function RecommendationsPage() {
  const queryClient = useQueryClient();

  const { data: recommendations, isLoading, refetch } = useQuery({
    queryKey: ['recommendations'],
    queryFn: () => recommendationsApi.list(10).then((r) => r.data),
  });

  const skillGaps = useMemo(() => collectSkillGaps(recommendations), [recommendations]);
  const skillGapsKey = skillGaps.join(',');

  const {
    data: roadmap,
    isLoading: roadmapLoading,
    isError: roadmapError,
  } = useQuery({
    queryKey: ['learning-roadmap', skillGapsKey],
    queryFn: () =>
      recommendationsApi.learningRoadmap(skillGapsKey || undefined).then((r) => r.data),
    enabled: skillGaps.length > 0,
  });

  const handleGenerate = async () => {
    await recommendationsApi.generate(10);
    await refetch();
    await queryClient.invalidateQueries({ queryKey: ['learning-roadmap'] });
  };

  const hasRoadmap = roadmap && roadmap.roadmap && roadmap.roadmap.length > 0;

  return (
    <div className="recommendations-page">
      <div className="recommendations-page__header">
        <div className="recommendations-page__title-group">
          <AIBadge label="RAG Powered" />
          <h1>AI Recommendations</h1>
          <p className="text-secondary">Personalized job matches with explainable intelligence</p>
        </div>
        <Button onClick={handleGenerate}>Generate Matches</Button>
      </div>

      {isLoading ? (
        <div className="dashboard-loading">
          <div className="dashboard-loading__spinner" />
          <span>Analyzing your profile...</span>
        </div>
      ) : recommendations && recommendations.length > 0 ? (
        <div className="recommendations-page__list">
          {recommendations.map((rec, i) => (
            <RecommendationCard key={rec.id} recommendation={rec} index={i} />
          ))}
        </div>
      ) : (
        <div className="recommendations-page__empty">
          <AIBadge label="Get Started" />
          <p>
            Upload your resume and click &quot;Generate Matches&quot; to get AI-powered
            recommendations tailored to your skills and goals.
          </p>
        </div>
      )}

      {skillGaps.length > 0 && (
        <motion.div
          className="recommendations-page__roadmap"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <AIBadge label="Learning Path" />
          <h2>Learning Roadmap</h2>

          {roadmapLoading ? (
            <div className="dashboard-loading" style={{ padding: '2rem 0' }}>
              <div className="dashboard-loading__spinner" />
              <span>Building your learning path...</span>
            </div>
          ) : roadmapError ? (
            <p className="text-secondary">Unable to load learning roadmap. Please try again.</p>
          ) : hasRoadmap ? (
            <>
              <p className="text-secondary">{roadmap.timeline}</p>
              <div className="recommendations-page__roadmap-steps">
                {roadmap.roadmap.map((step) => (
                  <div key={`${step.step}-${step.skill}`} className="recommendations-page__roadmap-step">
                    <span className="recommendations-page__step-number">{step.step}</span>
                    <div>
                      <strong>{step.skill}</strong>
                      <p className="text-secondary" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>
                        {step.description}
                      </p>
                      <span className="badge" style={{ marginTop: '0.5rem' }}>
                        {step.estimated_weeks} weeks
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className="text-secondary">
              Skill gaps detected across your matches. Generate matches again to refresh your roadmap.
            </p>
          )}
        </motion.div>
      )}
    </div>
  );
}
