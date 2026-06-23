import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { authApi } from '../api/endpoints';
import Button from '../components/common/Button';
import type { ResetPasswordData } from '../types';
import { ROUTES, SECURITY_QUESTION } from '../utils/constants';

export default function ForgotPasswordPage() {
  const [step, setStep] = useState<'email' | 'reset'>('email');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const emailForm = useForm<{ email: string }>();
  const resetForm = useForm<ResetPasswordData>();

  const onEmailSubmit = async (data: { email: string }) => {
    setError('');
    try {
      await authApi.getSecurityQuestion(data.email);
      setEmail(data.email);
      resetForm.setValue('email', data.email);
      setStep('reset');
    } catch {
      setError('No account found with this email.');
    }
  };

  const onResetSubmit = async (data: ResetPasswordData) => {
    setError('');
    try {
      await authApi.resetPassword(data);
      setSuccess(true);
    } catch {
      setError('Incorrect security answer or invalid details. Please try again.');
    }
  };

  return (
    <div className="container" style={{ maxWidth: 420, paddingTop: '4rem' }}>
      <div className="card">
        <h2>Reset Password</h2>
        <p className="text-secondary" style={{ margin: '0.5rem 0 1.5rem' }}>
          {step === 'email'
            ? 'Enter your email to continue.'
            : 'Answer your security question to set a new password.'}
        </p>

        {success ? (
          <p style={{ color: 'var(--color-success)' }}>
            Password reset successfully.{' '}
            <Link to={ROUTES.LOGIN}>Sign in</Link>
          </p>
        ) : step === 'email' ? (
          <form onSubmit={emailForm.handleSubmit(onEmailSubmit)}>
            <input
              type="email"
              className="input"
              placeholder="Email"
              {...emailForm.register('email', { required: true })}
              style={{ marginBottom: '1rem' }}
            />
            {error && <p style={{ color: 'var(--color-error)', fontSize: '0.875rem', marginBottom: '1rem' }}>{error}</p>}
            <Button type="submit" style={{ width: '100%' }}>Continue</Button>
          </form>
        ) : (
          <form onSubmit={resetForm.handleSubmit(onResetSubmit)}>
            <input type="hidden" {...resetForm.register('email')} value={email} />
            <p style={{ fontSize: '0.875rem', marginBottom: '0.5rem', fontWeight: 500 }}>
              {SECURITY_QUESTION}
            </p>
            <input
              className="input"
              placeholder="Your answer"
              {...resetForm.register('security_answer', { required: true })}
              style={{ marginBottom: '1rem' }}
            />
            <input
              type="password"
              className="input"
              placeholder="New password"
              {...resetForm.register('new_password', { required: true, minLength: 8 })}
              style={{ marginBottom: '1rem' }}
            />
            <input
              type="password"
              className="input"
              placeholder="Confirm new password"
              {...resetForm.register('new_password_confirm', { required: true })}
              style={{ marginBottom: '1rem' }}
            />
            {error && <p style={{ color: 'var(--color-error)', fontSize: '0.875rem', marginBottom: '1rem' }}>{error}</p>}
            <Button type="submit" style={{ width: '100%' }}>Reset Password</Button>
            <button
              type="button"
              className="btn btn--ghost"
              style={{ width: '100%', marginTop: '0.5rem' }}
              onClick={() => { setStep('email'); setError(''); }}
            >
              Back
            </button>
          </form>
        )}

        <p style={{ marginTop: '1rem', textAlign: 'center', fontSize: '0.875rem' }}>
          <Link to={ROUTES.LOGIN}>Back to login</Link>
        </p>
      </div>
    </div>
  );
}
