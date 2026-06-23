import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { savedJobsApi } from '../api/endpoints';
import Card from '../components/common/Card';
import JobCard from '../components/jobs/JobCard';

export default function SavedJobsPage() {
  const queryClient = useQueryClient();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [notes, setNotes] = useState('');

  const { data: savedJobs, isLoading } = useQuery({
    queryKey: ['saved-jobs'],
    queryFn: () => savedJobsApi.list(),
  });

  const handleRemove = async (id: string) => {
    await savedJobsApi.remove(id);
    queryClient.invalidateQueries({ queryKey: ['saved-jobs'] });
  };

  const handleSaveNotes = async (id: string) => {
    await savedJobsApi.updateNotes(id, notes);
    setEditingId(null);
    queryClient.invalidateQueries({ queryKey: ['saved-jobs'] });
  };

  return (
    <div>
      <h1>Saved Jobs</h1>
      <p className="text-secondary" style={{ marginBottom: '1.5rem' }}>
        Your bookmarked opportunities
      </p>

      {isLoading ? (
        <p>Loading...</p>
      ) : savedJobs && savedJobs.length > 0 ? (
        <div style={{ display: 'grid', gap: '1rem' }}>
          {savedJobs.map((saved) => (
            <Card key={saved.id}>
              <JobCard
                title={saved.job.title}
                company={saved.job.company}
                location={saved.job.location}
                isRemote={saved.job.is_remote}
                skills={saved.job.required_skills}
                isSaved
              />
              {editingId === saved.id ? (
                <div style={{ marginTop: '1rem' }}>
                  <textarea
                    className="input"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={3}
                    placeholder="Add notes..."
                  />
                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                    <button type="button" className="btn btn--primary" onClick={() => handleSaveNotes(saved.id)}>Save</button>
                    <button type="button" className="btn btn--ghost" onClick={() => setEditingId(null)}>Cancel</button>
                  </div>
                </div>
              ) : (
                <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <p className="text-secondary" style={{ fontSize: '0.875rem' }}>
                    {saved.notes || 'No notes'}
                  </p>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button type="button" className="btn btn--ghost" onClick={() => { setEditingId(saved.id); setNotes(saved.notes); }}>Edit Notes</button>
                    <button type="button" className="btn btn--ghost" onClick={() => handleRemove(saved.id)}>Remove</button>
                  </div>
                </div>
              )}
            </Card>
          ))}
        </div>
      ) : (
        <Card><p>No saved jobs yet. Browse jobs and save the ones you like.</p></Card>
      )}
    </div>
  );
}
