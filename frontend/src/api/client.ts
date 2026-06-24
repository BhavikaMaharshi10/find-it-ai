import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import {
  clearRefreshWaiters,
  getIsRefreshing,
  handleSessionExpired,
  notifyRefreshWaiters,
  setIsRefreshing,
  waitForTokenRefresh,
} from './authSession';
import { API_BASE_URL, REFRESH_KEY, TOKEN_KEY } from '../utils/constants';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/** Ends the request chain without an unhandled rejection after redirect. */
function haltRequest() {
  return Promise.reject(new axios.CanceledError('Session expired'));
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (!originalRequest || error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;
    const refreshToken = localStorage.getItem(REFRESH_KEY);

    if (!refreshToken) {
      handleSessionExpired();
      return haltRequest();
    }

    if (getIsRefreshing()) {
      const token = await waitForTokenRefresh();
      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${token}`;
      }
      return api(originalRequest);
    }

    setIsRefreshing(true);

    try {
      const { data } = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
        refresh: refreshToken,
      });
      localStorage.setItem(TOKEN_KEY, data.access);
      setIsRefreshing(false);
      notifyRefreshWaiters(data.access);

      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${data.access}`;
      }
      return api(originalRequest);
    } catch {
      setIsRefreshing(false);
      clearRefreshWaiters();
      handleSessionExpired();
      return haltRequest();
    }
  },
);

export default api;
