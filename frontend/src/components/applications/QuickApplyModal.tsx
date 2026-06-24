import { useMutation, useQueryClient } from '@tanstack/react-query';
import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { Link } from 'react-router-dom';
import { isAxiosError } from 'axios';
import { applicationsApi } from '../../api/endpoints';
import Button from '../common/Button';
import type { Application, Job } from '../../types';
import { ROUTES } from '../../utils/constants';
import './QuickApplyModal.scss';

interface QuickApplyModalProps {
  job: Job | null;
  onClose: () => void;
}

export default function QuickApplyModal({ job, onClose }: QuickApplyModalProps) {
  const queryClient = useQueryClient();
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const markMutation = useMutation({
    mutationFn: (targetJob: Job) =>
      applicationsApi.createFromJob(targetJob, 'applied').then((r) => r.data),
    onSuccess: async (createdApplication) => {
      queryClient.setQueryData<Application[]>(['applications'], (old) => {
        const list = old ?? [];
        const existingIndex = list.findIndex(
          (app) =>
            app.id === createdApplication.id ||
            (app.job.source === createdApplication.job.source &&
              app.job.external_id === createdApplication.job.external_id),
        );
        if (existingIndex >= 0) {
          const next = [...list];
          next[existingIndex] = createdApplication;
          return next;
        }
        return [createdApplication, ...list];
      });
      await queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      setError(null);
      setSuccess(true);
    },
    onError: (err) => {
      const message = isAxiosError(err)
        ? (err.response?.data as { detail?: string } | undefined)?.detail ??
          err.message
        : 'Could not save to your tracker. Please try again.';
      setError(typeof message === 'string' ? message : 'Could not save to your tracker.');
    },
  });

  useEffect(() => {
    setSuccess(false);
    setError(null);
    markMutation.reset();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- reset when a different job opens
  }, [job]);

  useEffect(() => {
    if (!job) return undefined;

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !markMutation.isPending) {
        onClose();
      }
    };

    document.body.style.overflow = 'hidden';
    window.addEventListener('keydown', onKeyDown);

    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', onKeyDown);
    };
  }, [job, markMutation.isPending, onClose]);

  if (!job) return null;

  return createPortal(
    <AnimatePresence>
      <motion.div
        className="quick-apply-modal__backdrop"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={markMutation.isPending ? undefined : onClose}
        aria-hidden
      />
      <div className="quick-apply-modal__container">
        <motion.div
          className="quick-apply-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="quick-apply-title"
          initial={{ opacity: 0, scale: 0.96, y: 12 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: 12 }}
          transition={{ duration: 0.2 }}
        >
        {success ? (
          <>
            <h2 id="quick-apply-title" className="quick-apply-modal__title">
              Added to tracker
            </h2>
            <p className="quick-apply-modal__subtitle text-secondary">
              <strong>{job.title}</strong> at {job.company} is now in your Application Tracker
              under <em>Applied</em>.
            </p>
            <div className="quick-apply-modal__actions">
              <Button variant="secondary" onClick={onClose}>
                Close
              </Button>
              <Link to={ROUTES.APPLICATIONS} className="btn btn--primary" onClick={onClose}>
                View tracker
              </Link>
            </div>
          </>
        ) : (
          <>
            <h2 id="quick-apply-title" className="quick-apply-modal__title">
              Track your application
            </h2>
            <p className="quick-apply-modal__subtitle text-secondary">
              Applied to <strong>{job.title}</strong> at {job.company}? Mark it as applied to
              keep it in your tracker.
            </p>

            {error && <p className="quick-apply-modal__error">{error}</p>}

            <div className="quick-apply-modal__actions">
              <Button variant="ghost" onClick={onClose} disabled={markMutation.isPending}>
                Not now
              </Button>
              {job.source_url && (
                <Button
                  variant="secondary"
                  onClick={() => window.open(job.source_url, '_blank', 'noopener,noreferrer')}
                  disabled={markMutation.isPending}
                >
                  Open listing
                </Button>
              )}
              <Button
                onClick={() => markMutation.mutate(job)}
                loading={markMutation.isPending}
              >
                Mark as applied
              </Button>
            </div>
          </>
        )}
        </motion.div>
      </div>
    </AnimatePresence>,
    document.body,
  );
}
