import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { applicationsApi } from '../api/endpoints';
import Card from '../components/common/Card';
import { APPLICATION_STATUSES } from '../utils/constants';
import type { Application, ApplicationStatus } from '../types';
import './ApplicationsPage.scss';

const KANBAN_COLUMNS: ApplicationStatus[] = [
  'applied',
  'interview_scheduled',
  'interview_completed',
  'offer_received',
  'accepted',
  'rejected',
];

export default function ApplicationsPage() {
  const [view, setView] = useState<'kanban' | 'list'>('kanban');
  const queryClient = useQueryClient();

  const { data: applications, isLoading } = useQuery({
    queryKey: ['applications'],
    queryFn: () => applicationsApi.list(),
  });

  const handleStatusChange = async (id: string, status: ApplicationStatus) => {
    await applicationsApi.update(id, { status });
    queryClient.invalidateQueries({ queryKey: ['applications'] });
  };

  const getByStatus = (status: ApplicationStatus) =>
    applications?.filter((a) => a.status === status) ?? [];

  return (
    <div>
      <div className="applications-header">
        <div>
          <h1>Application Tracker</h1>
          <p className="text-secondary">Track your job applications</p>
        </div>
        <div className="view-toggle">
          <button
            type="button"
            className={`btn ${view === 'kanban' ? 'btn--primary' : 'btn--ghost'}`}
            onClick={() => setView('kanban')}
          >
            Kanban
          </button>
          <button
            type="button"
            className={`btn ${view === 'list' ? 'btn--primary' : 'btn--ghost'}`}
            onClick={() => setView('list')}
          >
            List
          </button>
        </div>
      </div>

      {isLoading ? (
        <p>Loading applications...</p>
      ) : view === 'kanban' ? (
        <div className="kanban-board">
          {KANBAN_COLUMNS.map((status) => (
            <div key={status} className="kanban-column">
              <h3 className="kanban-column__title">
                {APPLICATION_STATUSES.find((s) => s.value === status)?.label ?? status}
                <span className="kanban-column__count">{getByStatus(status).length}</span>
              </h3>
              <div className="kanban-column__cards">
                {getByStatus(status).map((app) => (
                  <ApplicationCard
                    key={app.id}
                    application={app}
                    onStatusChange={handleStatusChange}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="application-list">
          {applications?.map((app) => (
            <Card key={app.id} className="application-list-item">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3>{app.job.title}</h3>
                  <p className="text-secondary">{app.job.company}</p>
                </div>
                <select
                  className="input"
                  value={app.status}
                  onChange={(e) => handleStatusChange(app.id, e.target.value as ApplicationStatus)}
                  style={{ width: 'auto' }}
                >
                  {APPLICATION_STATUSES.map((s) => (
                    <option key={s.value} value={s.value}>{s.label}</option>
                  ))}
                </select>
              </div>
            </Card>
          ))}
          {applications?.length === 0 && <Card><p>No applications yet.</p></Card>}
        </div>
      )}
    </div>
  );
}

function ApplicationCard({
  application,
  onStatusChange,
}: {
  application: Application;
  onStatusChange: (id: string, status: ApplicationStatus) => void;
}) {
  return (
    <div className="kanban-card">
      <h4>{application.job.title}</h4>
      <p className="text-secondary">{application.job.company}</p>
      <select
        className="input"
        value={application.status}
        onChange={(e) => onStatusChange(application.id, e.target.value as ApplicationStatus)}
        style={{ marginTop: '0.5rem', fontSize: '0.75rem' }}
      >
        {APPLICATION_STATUSES.map((s) => (
          <option key={s.value} value={s.value}>{s.label}</option>
        ))}
      </select>
    </div>
  );
}
