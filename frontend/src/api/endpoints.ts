import api from './client';
import type {
  Application,
  AuthTokens,
  DashboardStats,
  Job,
  LearningRoadmap,
  LoginCredentials,
  PaginatedResponse,
  Profile,
  Recommendation,
  RegisterData,
  Resume,
  SavedJob,
  User,
} from '../types';

function unwrapList<T>(data: PaginatedResponse<T> | T[]): T[] {
  return Array.isArray(data) ? data : data.results;
}

export const authApi = {
  login: (credentials: LoginCredentials) =>
    api.post<AuthTokens & { user: User }>('/auth/login/', {
      email: credentials.email,
      password: credentials.password,
    }),

  register: (data: RegisterData) =>
    api.post<AuthTokens & { user: User }>('/auth/register/', data),

  logout: (refresh: string) => api.post('/auth/logout/', { refresh }),

  getSecurityQuestion: (email: string) =>
    api.post<{ security_question: string }>('/auth/security-question/', { email }),

  resetPassword: (data: import('../types').ResetPasswordData) =>
    api.post('/auth/reset-password/', data),

  changePassword: (data: {
    old_password: string;
    new_password: string;
    new_password_confirm: string;
  }) => api.post('/auth/change-password/', data),

  getMe: () => api.get<User>('/auth/me/'),

  updateMe: (data: Partial<User>) => api.patch<User>('/auth/me/', data),
};

export const profileApi = {
  get: () => api.get<Profile>('/profile/'),
  update: (data: Partial<Profile>) => api.patch<Profile>('/profile/', data),
};

export const resumeApi = {
  list: () => api.get<PaginatedResponse<Resume> | Resume[]>('/resume/').then((r) => unwrapList(r.data)),
  getActive: () => api.get<Resume>('/resume/active/'),
  upload: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return api.post<Resume>('/resume/upload/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  delete: (id: string) => api.delete(`/resume/${id}/`),
};

export const jobsApi = {
  list: (params?: Record<string, string | number | boolean>) =>
    api.get<PaginatedResponse<Job>>('/jobs/', { params }),

  get: (id: string) => api.get<Job>(`/jobs/${id}/`),
};

export const savedJobsApi = {
  list: () =>
    api.get<PaginatedResponse<SavedJob> | SavedJob[]>('/jobs/saved/').then((r) => unwrapList(r.data)),
  save: (jobId: string, notes?: string) =>
    api.post<SavedJob>('/jobs/saved/', { job_id: jobId, notes }),
  updateNotes: (id: string, notes: string) =>
    api.patch<SavedJob>(`/jobs/saved/${id}/notes/`, { notes }),
  remove: (id: string) => api.delete(`/jobs/saved/${id}/`),
};

export const recommendationsApi = {
  list: (topK = 10) => api.get<Recommendation[]>('/recommendations/', { params: { top_k: topK } }),
  generate: (topK = 10) => api.post<Recommendation[]>('/recommendations/', { top_k: topK }),
  get: (id: string) => api.get<Recommendation>(`/recommendations/${id}/`),
  learningRoadmap: (skills?: string) =>
    api.get<LearningRoadmap>('/recommendations/learning/', {
      params: skills ? { skills } : undefined,
    }),
  ragQuery: (query: string) => api.post('/recommendations/rag/', { query }),
};

export const applicationsApi = {
  list: (status?: string) =>
    api
      .get<PaginatedResponse<Application> | Application[]>('/applications/', {
        params: status ? { status } : undefined,
      })
      .then((r) => unwrapList(r.data)),
  create: (jobId: string, status = 'applied') =>
    api.post<Application>('/applications/', { job_id: jobId, status }),
  update: (id: string, data: Partial<Application>) =>
    api.patch<Application>(`/applications/${id}/`, data),
  delete: (id: string) => api.delete(`/applications/${id}/`),
};

export const dashboardApi = {
  getStats: () => api.get<DashboardStats>('/dashboard/stats/'),
  getMatchDistribution: () => api.get<Record<string, number>>('/dashboard/match-distribution/'),
  getSkillGaps: () => api.get<{ skill: string; count: number }[]>('/dashboard/skill-gaps/'),
  getApplicationTrends: () =>
    api.get<{ applied_date: string; count: number }[]>('/dashboard/application-trends/'),
  getApplicationStatus: () =>
    api.get<{ status: string; count: number }[]>('/dashboard/application-status/'),
};
