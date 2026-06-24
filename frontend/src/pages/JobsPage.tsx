import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { isAxiosError } from 'axios';
import QuickApplyModal from '../components/applications/QuickApplyModal';
import { jobsApi, savedJobsApi } from '../api/endpoints';
import Button from '../components/common/Button';
import JobCard from '../components/jobs/JobCard';
import type { Job, LiveJobSearchResponse } from '../types';
import '../components/jobs/JobCard.scss';
import '../components/dashboard/DashboardCharts.scss';

interface SearchFilters {
  search: string;
  isRemote: string;
  experience: string;
}

const EMPTY_FILTERS: SearchFilters = { search: '', isRemote: '', experience: '' };

function buildSearchParams(filters: SearchFilters) {
  return {
    search: filters.search,
    ...(filters.isRemote !== '' ? { is_remote: filters.isRemote } : {}),
    ...(filters.experience ? { experience_level: filters.experience } : {}),
  };
}

export default function JobsPage() {
  const [filters, setFilters] = useState<SearchFilters>(EMPTY_FILTERS);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [applyJob, setApplyJob] = useState<Job | null>(null);
  const queryClient = useQueryClient();

  const searchMutation = useMutation({
    mutationFn: (nextFilters: SearchFilters) =>
      jobsApi.search(buildSearchParams(nextFilters)).then((r) => r.data),
    onMutate: () => setSearchError(null),
    onError: (error) => {
      if (isAxiosError(error) && error.code === 'ERR_CANCELED') {
        return;
      }
      const message = isAxiosError(error)
        ? (error.response?.data as { detail?: string } | undefined)?.detail ??
          error.message
        : 'Search failed. Please try again.';
      setSearchError(message);
    },
  });

  const { data: savedJobs } = useQuery({
    queryKey: ['saved-jobs'],
    queryFn: () => savedJobsApi.list(),
  });

  const savedKeys = new Set(
    savedJobs?.map((s) => `${s.job.source ?? 'seed'}:${s.job.external_id ?? s.job.id}`) ?? [],
  );

  const handleApplyFilters = () => {
    searchMutation.mutate({ ...filters });
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

  const data: LiveJobSearchResponse | undefined = searchMutation.data;
  const results = data?.results ?? [];
  const hasSearched =
    searchMutation.isPending || searchMutation.isSuccess || searchMutation.isError;

  return (
    <div>
      <h1>Job Search</h1>
      <p className="text-secondary" style={{ marginBottom: '1.5rem' }}>
        Live openings from Remotive, Lever, and Greenhouse — fetched in real time
      </p>

      <div className="job-filters">
        <div>
          <label htmlFor="search">Search</label>
          <input
            id="search"
            className="input"
            placeholder="e.g. developer, engineer..."
            value={filters.search}
            onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))}
            onKeyDown={(e) => e.key === 'Enter' && handleApplyFilters()}
          />
        </div>
        <div>
          <label htmlFor="remote">Remote</label>
          <select
            id="remote"
            className="input"
            value={filters.isRemote}
            onChange={(e) => setFilters((f) => ({ ...f, isRemote: e.target.value }))}
          >
            <option value="">All</option>
            <option value="true">Remote</option>
            <option value="false">On-site</option>
          </select>
        </div>
        <div>
          <label htmlFor="exp">Experience</label>
          <select
            id="exp"
            className="input"
            value={filters.experience}
            onChange={(e) => setFilters((f) => ({ ...f, experience: e.target.value }))}
          >
            <option value="">All levels</option>
            <option value="junior">Junior</option>
            <option value="mid">Mid</option>
            <option value="senior">Senior</option>
            <option value="lead">Lead</option>
          </select>
        </div>
        <div className="job-filters__apply">
          <Button onClick={handleApplyFilters} loading={searchMutation.isPending}>
            Apply
          </Button>
        </div>
      </div>

      {!hasSearched ? (
        <p className="text-secondary">Set your filters and click Apply to search live job openings.</p>
      ) : searchMutation.isPending ? (
        <div className="dashboard-loading">
          <div className="dashboard-loading__spinner" />
          <span>Fetching live jobs from Remotive, Lever, and Greenhouse…</span>
        </div>
      ) : searchMutation.isError && !data ? (
        <p className="text-error" style={{ color: 'var(--color-error)' }}>
          {searchError ?? 'Search failed. Check that the backend is running and try again.'}
        </p>
      ) : (
        <>
          <p className="text-secondary" style={{ marginBottom: '1rem' }}>
            {results.length} result{results.length !== 1 ? 's' : ''}
            {data?.cached ? ' (cached)' : ''}
          </p>
          <div className="job-list">
            {results.map((job) => (
              <JobCard
                key={job.external_key ?? job.id}
                title={job.title}
                company={job.company}
                location={job.location}
                isRemote={job.is_remote}
                skills={job.required_skills}
                salaryRange={job.salary_range}
                isSaved={savedKeys.has(`${job.source}:${job.external_id}`)}
                onSave={() => handleSave(job)}
                onApply={() => handleQuickApply(job)}
              />
            ))}
            {results.length === 0 && (
              <p>No jobs match your filters. Try different keywords — search matches title and company only.</p>
            )}
          </div>
        </>
      )}
      <QuickApplyModal job={applyJob} onClose={() => setApplyJob(null)} />
    </div>
  );
}
