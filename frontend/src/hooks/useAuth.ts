import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/endpoints';
import { useAuthStore } from '../store';
import type { LoginCredentials, RegisterData } from '../types';
import { ROUTES } from '../utils/constants';

export function useLogin() {
  const setAuth = useAuthStore((s) => s.setAuth);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (credentials: LoginCredentials) => authApi.login(credentials),
    onSuccess: (res) => {
      setAuth(res.data.user, res.data.access, res.data.refresh);
      navigate(ROUTES.DASHBOARD);
    },
  });
}

export function useRegister() {
  const setAuth = useAuthStore((s) => s.setAuth);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (data: RegisterData) => authApi.register(data),
    onSuccess: (res) => {
      setAuth(res.data.user, res.data.access, res.data.refresh);
      navigate(ROUTES.DASHBOARD);
    },
  });
}

export function useLogout() {
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: () => {
      const refresh = localStorage.getItem('finditai_refresh_token');
      return authApi.logout(refresh || '');
    },
    onSettled: () => {
      clearAuth();
      navigate(ROUTES.LOGIN);
    },
  });
}

export function useCurrentUser() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return useQuery({
    queryKey: ['user', 'me'],
    queryFn: () => authApi.getMe().then((r) => r.data),
    enabled: isAuthenticated,
  });
}
