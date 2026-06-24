import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
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

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: ApplicationStatus }) =>
      applicationsApi.update(id, { status }).then((r) => r.data),
    onMutate: async ({ id, status }) => {
      await queryClient.cancelQueries({ queryKey: ['applications'] });
      const previous = queryClient.getQueryData<Application[]>(['applications']);
      queryClient.setQueryData<Application[]>(['applications'], (old) =>
        old?.map((app) => (app.id === id ? { ...app, status } : app)) ?? [],
      );
      return { previous };
    },
    onError: (_error, _variables, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['applications'], context.previous);
      }
    },
    onSuccess: (updated) => {
      queryClient.setQueryData<Application[]>(['applications'], (old) =>
        old?.map((app) => (app.id === updated.id ? updated : app)) ?? [updated],
      );
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });

  const handleStatusChange = (id: string, status: ApplicationStatus) => {
    updateStatusMutation.mutate({ id, status });
  };

  const getByStatus = (status: ApplicationStatus) =>
    applications?.filter((a) => a.status === status) ?? [];

  const updatingId = updateStatusMutation.isPending
    ? updateStatusMutation.variables?.id
    : undefined;

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
                    isUpdating={updatingId === app.id}
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
                  disabled={updatingId === app.id}
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
  isUpdating,
}: {
  application: Application;
  onStatusChange: (id: string, status: ApplicationStatus) => void;
  isUpdating?: boolean;
}) {
  return (
    <div className={`kanban-card${isUpdating ? ' kanban-card--updating' : ''}`}>
      <h4>{application.job.title}</h4>
      <p className="text-secondary">{application.job.company}</p>
      <select
        className="input"
        value={application.status}
        onChange={(e) => onStatusChange(application.id, e.target.value as ApplicationStatus)}
        disabled={isUpdating}
        style={{ marginTop: '0.5rem', fontSize: '0.75rem' }}
      >
        {APPLICATION_STATUSES.map((s) => (
          <option key={s.value} value={s.value}>{s.label}</option>
        ))}
      </select>
    </div>
  );
}
