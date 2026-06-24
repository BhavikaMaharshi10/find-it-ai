import { Navigate, Outlet } from 'react-router-dom';
import { hasAuthTokens } from '../api/authSession';
import { useAuthStore } from '../store';

export function ProtectedRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  if (!isAuthenticated || !hasAuthTokens()) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}

export function PublicRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  if (isAuthenticated && hasAuthTokens()) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
