import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import Button from '../components/common/Button';
import { useLogin } from '../hooks/useAuth';
import type { LoginCredentials } from '../types';
import { ROUTES } from '../utils/constants';

export default function LoginPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginCredentials>();
  const login = useLogin();

  return (
    <div className="container" style={{ maxWidth: 420, paddingTop: '4rem' }}>
      <div className="card">
        <h2 style={{ marginBottom: '0.5rem' }}>Welcome back</h2>
        <p className="text-secondary" style={{ marginBottom: '1.5rem' }}>
          Sign in to your FindItAI account
        </p>
        {login.isError && (
          <p style={{ color: 'var(--color-error)', marginBottom: '1rem', fontSize: '0.875rem' }}>
            Invalid email or password.
          </p>
        )}
        <form onSubmit={handleSubmit((data) => login.mutate(data))}>
          <div style={{ marginBottom: '1rem' }}>
            <input
              type="email"
              className="input"
              placeholder="Email address"
              {...register('email', { required: 'Email is required' })}
            />
            {errors.email && <span style={{ color: 'var(--color-error)', fontSize: '0.875rem' }}>{errors.email.message}</span>}
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <input
              type="password"
              className="input"
              placeholder="Password"
              {...register('password', { required: 'Password is required' })}
            />
          </div>
          <Button type="submit" loading={login.isPending} style={{ width: '100%' }}>
            Sign In
          </Button>
        </form>
        <p style={{ marginTop: '1rem', textAlign: 'center', fontSize: '0.875rem' }}>
          <Link to={ROUTES.FORGOT_PASSWORD}>Forgot password?</Link>
        </p>
        <p style={{ marginTop: '0.5rem', textAlign: 'center', fontSize: '0.875rem' }}>
          Don&apos;t have an account? <Link to={ROUTES.REGISTER}>Register</Link>
        </p>
      </div>
    </div>
  );
}
