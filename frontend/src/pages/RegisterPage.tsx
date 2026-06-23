import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import Button from '../components/common/Button';
import { useRegister } from '../hooks/useAuth';
import type { RegisterData } from '../types';
import { ROUTES, SECURITY_QUESTION } from '../utils/constants';

export default function RegisterPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<RegisterData>();
  const registerMutation = useRegister();

  return (
    <div className="container" style={{ maxWidth: 420, paddingTop: '4rem' }}>
      <div className="card">
        <h2 style={{ marginBottom: '0.5rem' }}>Create your account</h2>
        <p className="text-secondary" style={{ marginBottom: '1.5rem' }}>
          Start your AI-powered job search journey
        </p>
        <form onSubmit={handleSubmit((data) => registerMutation.mutate(data))}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
            <input className="input" placeholder="First name" {...register('first_name', { required: true })} />
            <input className="input" placeholder="Last name" {...register('last_name', { required: true })} />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <input type="email" className="input" placeholder="Email" {...register('email', { required: true })} />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <input type="password" className="input" placeholder="Password" {...register('password', { required: true, minLength: 8 })} />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <input type="password" className="input" placeholder="Confirm password" {...register('password_confirm', { required: true })} />
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <label htmlFor="security_answer" style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
              {SECURITY_QUESTION}
            </label>
            <input
              id="security_answer"
              className="input"
              placeholder="Your answer (used to reset password)"
              {...register('security_answer', { required: 'Security answer is required', minLength: 2 })}
            />
            {errors.security_answer && (
              <span style={{ color: 'var(--color-error)', fontSize: '0.875rem' }}>
                {errors.security_answer.message}
              </span>
            )}
          </div>
          <Button type="submit" loading={registerMutation.isPending} style={{ width: '100%' }}>
            Create Account
          </Button>
        </form>
        <p style={{ marginTop: '1rem', textAlign: 'center', fontSize: '0.875rem' }}>
          Already have an account? <Link to={ROUTES.LOGIN}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
