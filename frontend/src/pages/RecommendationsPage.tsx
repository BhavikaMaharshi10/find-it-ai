import { useQuery } from '@tanstack/react-query';
import { recommendationsApi } from '../api/endpoints';
import Card from '../components/common/Card';
import JobCard from '../components/jobs/JobCard';
import Button from '../components/common/Button';

export default function RecommendationsPage() {
  const { data: recommendations, isLoading, refetch } = useQuery({
    queryKey: ['recommendations'],
    queryFn: () => recommendationsApi.list(10).then((r) => r.data),
  });

  const { data: roadmap } = useQuery({
    queryKey: ['learning-roadmap'],
    queryFn: () => recommendationsApi.learningRoadmap().then((r) => r.data),
  });

  const handleGenerate = async () => {
    await recommendationsApi.generate(10);
    refetch();
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1>AI Recommendations</h1>
          <p className="text-secondary">Personalized job matches powered by RAG</p>
        </div>
        <Button onClick={handleGenerate}>Generate Matches</Button>
      </div>

      {isLoading ? (
        <p>Loading recommendations...</p>
      ) : recommendations && recommendations.length > 0 ? (
        <div style={{ display: 'grid', gap: '1rem', marginBottom: '2rem' }}>
          {recommendations.map((rec) => (
            <Card key={rec.id}>
              <JobCard
                title={rec.job.title}
                company={rec.job.company}
                location={rec.job.location}
                isRemote={rec.job.is_remote}
                skills={rec.job.required_skills}
                matchScore={rec.match_score}
              />
              <p style={{ marginTop: '1rem', fontSize: '0.875rem' }}>{rec.reasoning}</p>
              {rec.missing_skills.length > 0 && (
                <div style={{ marginTop: '0.75rem' }}>
                  <strong style={{ fontSize: '0.875rem' }}>Missing skills: </strong>
                  {rec.missing_skills.map((s) => (
                    <span key={s} className="badge" style={{ marginRight: '0.25rem' }}>{s}</span>
                  ))}
                </div>
              )}
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <p>Upload your resume and click &quot;Generate Matches&quot; to get AI-powered recommendations.</p>
        </Card>
      )}

      {roadmap && roadmap.roadmap && roadmap.roadmap.length > 0 && (
        <div>
          <h2 style={{ marginBottom: '1rem' }}>Learning Roadmap</h2>
          <p className="text-secondary" style={{ marginBottom: '1rem' }}>{roadmap.timeline}</p>
          <div style={{ display: 'grid', gap: '0.75rem' }}>
            {roadmap.roadmap.map((step) => (
              <Card key={step.step} hover={false}>
                <strong>Step {step.step}: {step.skill}</strong>
                <p className="text-secondary" style={{ fontSize: '0.875rem' }}>{step.description}</p>
                <span className="badge">{step.estimated_weeks} weeks</span>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
