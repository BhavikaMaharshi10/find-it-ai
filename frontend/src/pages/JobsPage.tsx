import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { applicationsApi, jobsApi, savedJobsApi } from '../api/endpoints';
import JobCard from '../components/jobs/JobCard';
import '../components/jobs/JobCard.scss';

export default function JobsPage() {
  const [search, setSearch] = useState('');
  const [isRemote, setIsRemote] = useState<string>('');
  const [experience, setExperience] = useState('');
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['jobs', search, isRemote, experience],
    queryFn: () =>
      jobsApi
        .list({
          search,
          ...(isRemote !== '' ? { is_remote: isRemote } : {}),
          ...(experience ? { experience_level: experience } : {}),
        })
        .then((r) => r.data),
  });

  const { data: savedJobs } = useQuery({
    queryKey: ['saved-jobs'],
    queryFn: () => savedJobsApi.list(),
  });

  const savedIds = new Set(savedJobs?.map((s) => s.job.id) ?? []);

  const handleSave = async (jobId: string) => {
    await savedJobsApi.save(jobId);
    queryClient.invalidateQueries({ queryKey: ['saved-jobs'] });
  };

  const handleApply = async (jobId: string) => {
    await applicationsApi.create(jobId);
  };

  return (
    <div>
      <h1>Job Search</h1>
      <p className="text-secondary" style={{ marginBottom: '1.5rem' }}>
        Discover opportunities matched to your profile
      </p>

      <div className="job-filters">
        <div>
          <label htmlFor="search">Search</label>
          <input
            id="search"
            className="input"
            placeholder="Title, company, skills..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="remote">Remote</label>
          <select id="remote" className="input" value={isRemote} onChange={(e) => setIsRemote(e.target.value)}>
            <option value="">All</option>
            <option value="true">Remote</option>
            <option value="false">On-site</option>
          </select>
        </div>
        <div>
          <label htmlFor="exp">Experience</label>
          <select id="exp" className="input" value={experience} onChange={(e) => setExperience(e.target.value)}>
            <option value="">All levels</option>
            <option value="junior">Junior</option>
            <option value="mid">Mid</option>
            <option value="senior">Senior</option>
            <option value="lead">Lead</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <p>Loading jobs...</p>
      ) : (
        <div className="job-list">
          {data?.results.map((job) => (
            <JobCard
              key={job.id}
              title={job.title}
              company={job.company}
              location={job.location}
              isRemote={job.is_remote}
              skills={job.required_skills}
              salaryRange={job.salary_range}
              isSaved={savedIds.has(job.id)}
              onSave={() => handleSave(job.id)}
              onApply={() => handleApply(job.id)}
            />
          ))}
          {data?.results.length === 0 && <p>No jobs found.</p>}
        </div>
      )}
    </div>
  );
}
