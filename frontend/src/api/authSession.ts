import { useAuthStore } from '../store';
import { REFRESH_KEY, ROUTES, TOKEN_KEY } from '../utils/constants';

const PUBLIC_PATHS = new Set([
  ROUTES.HOME,
  ROUTES.LOGIN,
  ROUTES.REGISTER,
  ROUTES.FORGOT_PASSWORD,
]);

let isRefreshing = false;
let refreshWaiters: Array<(token: string) => void> = [];

function notifyRefreshWaiters(token: string) {
  refreshWaiters.forEach((cb) => cb(token));
  refreshWaiters = [];
}

export function handleSessionExpired() {
  useAuthStore.getState().clearAuth();

  const path = window.location.pathname;
  if (!PUBLIC_PATHS.has(path as typeof ROUTES.HOME)) {
    window.location.href = ROUTES.LOGIN;
  }
}

export function hasAuthTokens() {
  return Boolean(localStorage.getItem(TOKEN_KEY) && localStorage.getItem(REFRESH_KEY));
}

export function waitForTokenRefresh(): Promise<string> {
  return new Promise((resolve) => {
    refreshWaiters.push(resolve);
  });
}

export function getIsRefreshing() {
  return isRefreshing;
}

export function setIsRefreshing(value: boolean) {
  isRefreshing = value;
}

export function clearRefreshWaiters() {
  refreshWaiters = [];
}

export { notifyRefreshWaiters };
