export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const TOKEN_KEY = 'finditai_access_token';
export const REFRESH_KEY = 'finditai_refresh_token';
export const THEME_KEY = 'finditai_theme';

export const APPLICATION_STATUSES = [
  { value: 'applied', label: 'Applied' },
  { value: 'interview_scheduled', label: 'Interview Scheduled' },
  { value: 'interview_completed', label: 'Interview Completed' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'offer_received', label: 'Offer Received' },
  { value: 'accepted', label: 'Accepted' },
] as const;

export const EXPERIENCE_LEVELS = [
  { value: 'junior', label: 'Junior' },
  { value: 'mid', label: 'Mid-Level' },
  { value: 'senior', label: 'Senior' },
  { value: 'lead', label: 'Lead' },
] as const;

export const SECURITY_QUESTION = 'What is your favourite sport?';

export const ROUTES = {
  HOME: '/',
  FEATURES: '/features',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  DASHBOARD: '/dashboard',
  PROFILE: '/profile',
  RESUME: '/resume',
  JOBS: '/jobs',
  RECOMMENDATIONS: '/recommendations',
  SAVED_JOBS: '/saved-jobs',
  APPLICATIONS: '/applications',
  SETTINGS: '/settings',
} as const;
