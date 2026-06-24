import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { isAxiosError } from 'axios';
import { recommendationsApi, savedJobsApi } from '../api/endpoints';
import QuickApplyModal from '../components/applications/QuickApplyModal';
import Button from '../components/common/Button';
import AIBadge from '../components/common/AIBadge';
import RecommendationCard from '../components/recommendations/RecommendationCard';
import type { Job, Recommendation } from '../types';
import '../components/recommendations/RecommendationCard.scss';
import '../components/dashboard/DashboardCharts.scss';

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
  const [applyJob, setApplyJob] = useState<Job | null>(null);
  const [generateError, setGenerateError] = useState<string | null>(null);

  const generateMutation = useMutation({
    mutationFn: () => recommendationsApi.generate(10).then((r) => r.data),
    onMutate: () => setGenerateError(null),
    onError: (error) => {
      if (isAxiosError(error) && error.code === 'ERR_CANCELED') {
        return;
      }
      const message = isAxiosError(error)
        ? (error.response?.data as { detail?: string } | undefined)?.detail ??
          error.message
        : 'Could not generate matches. Please try again.';
      setGenerateError(message);
    },
  });

  const recommendations: Recommendation[] | undefined = generateMutation.data;
  const hasGenerated =
    generateMutation.isPending || generateMutation.isSuccess || generateMutation.isError;

  const skillGaps = useMemo(() => collectSkillGaps(recommendations), [recommendations]);
  const skillGapsKey = skillGaps.join(',');

  const { data: savedJobs } = useQuery({
    queryKey: ['saved-jobs'],
    queryFn: () => savedJobsApi.list(),
  });

  const savedKeys = new Set(
    savedJobs?.map((s) => `${s.job.source ?? 'seed'}:${s.job.external_id ?? s.job.id}`) ?? [],
  );

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

  const handleGenerate = () => {
    generateMutation.mutate();
  };

  const handleSave = async (job: Job) => {
    await savedJobsApi.save(job);
    queryClient.invalidateQueries({ queryKey: ['saved-jobs'] });
  };

  const handleQuickApply = (job: Job) => {
    if (job.source_url) {
      window.open(job.source_url, '_blank', 'noopener,noreferrer');
    }
    setApplyJob(job);
  };

  const hasRoadmap = roadmap && roadmap.roadmap && roadmap.roadmap.length > 0;

  return (
    <div className="recommendations-page">
      <div className="recommendations-page__header">
        <div className="recommendations-page__title-group">
          <AIBadge label="Live AI Matching" />
          <h1>AI Recommendations</h1>
          <p className="text-secondary">
            Matches your resume against live openings from Remotive, Lever, and Greenhouse
          </p>
        </div>
        <Button onClick={handleGenerate} loading={generateMutation.isPending}>
          Generate Matches
        </Button>
      </div>

      {!hasGenerated ? (
        <div className="recommendations-page__empty">
          <AIBadge label="Get Started" />
          <p>
            Upload your resume and click &quot;Generate Matches&quot; to rank live job openings
            against your profile.
          </p>
        </div>
      ) : generateMutation.isPending ? (
        <div className="dashboard-loading">
          <div className="dashboard-loading__spinner" />
          <span>Fetching live jobs and analyzing your resume…</span>
        </div>
      ) : generateMutation.isError && !recommendations?.length ? (
        <p className="text-secondary" style={{ color: 'var(--color-error)' }}>
          {generateError ?? 'Failed to generate matches. Check that the backend is running.'}
        </p>
      ) : recommendations && recommendations.length > 0 ? (
        <div className="recommendations-page__list">
          {recommendations.map((rec, i) => (
            <RecommendationCard
              key={rec.id}
              recommendation={rec}
              index={i}
              isSaved={savedKeys.has(`${rec.job.source}:${rec.job.external_id}`)}
              onSave={() => handleSave(rec.job)}
              onApply={() => handleQuickApply(rec.job)}
            />
          ))}
        </div>
      ) : (
        <div className="recommendations-page__empty">
          <p>
            No strong matches found in the current live job pool. Try again later or broaden your
            resume skills.
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

      <QuickApplyModal job={applyJob} onClose={() => setApplyJob(null)} />
    </div>
  );
}
