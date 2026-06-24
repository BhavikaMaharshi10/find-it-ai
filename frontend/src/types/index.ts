export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  security_answer: string;
}

export interface ResetPasswordData {
  email: string;
  security_answer: string;
  new_password: string;
  new_password_confirm: string;
}

export interface Profile {
  id: string;
  user: User;
  headline: string;
  location: string;
  phone: string;
  linkedin_url: string;
  github_url: string;
  avatar: string | null;
  preferences: Record<string, unknown>;
}

export interface Resume {
  id: string;
  original_filename: string;
  raw_text: string;
  structured_data: Record<string, unknown>;
  skills: string[];
  education: EducationEntry[];
  work_experience: WorkExperience[];
  projects: Project[];
  certifications: Certification[];
  ai_summary: string;
  is_active: boolean;
  created_at: string;
}

export interface EducationEntry {
  institution: string;
  degree: string;
  field: string;
  start_date: string;
  end_date: string;
}

export interface WorkExperience {
  company: string;
  title: string;
  description: string;
  start_date: string;
  end_date: string;
  skills: string[];
}

export interface Project {
  name: string;
  description: string;
  technologies: string[];
  url?: string;
}

export interface Certification {
  name: string;
  issuer: string;
  date: string;
}

export interface Job {
  id?: string;
  external_key?: string;
  external_id?: string;
  source?: string;
  title: string;
  company: string;
  description: string;
  location: string;
  is_remote: boolean;
  experience_level: ExperienceLevel;
  required_skills: string[];
  preferred_skills?: string[];
  salary_range: string;
  employment_type: string;
  source_url: string;
  posted_at: string | null;
}

export interface LiveJobSearchResponse {
  count: number;
  results: Job[];
  cached: boolean;
}

export type ExperienceLevel = 'junior' | 'mid' | 'senior' | 'lead';

export interface Recommendation {
  id: string;
  job: Job;
  match_score: number;
  reasoning: string;
  missing_skills: string[];
  strengths: string[];
  is_viewed: boolean;
  created_at: string;
}

export interface SavedJob {
  id: string;
  job: Job;
  notes: string;
  saved_at: string;
}

export type ApplicationStatus =
  | 'applied'
  | 'interview_scheduled'
  | 'interview_completed'
  | 'rejected'
  | 'offer_received'
  | 'accepted';

export interface Application {
  id: string;
  job: Job;
  status: ApplicationStatus;
  notes: string;
  applied_date: string;
  interview_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  jobs_found: number;
  saved_jobs: number;
  applications_sent: number;
  average_match_score: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  total_pages: number;
  current_page: number;
  results: T[];
}

export interface ApiError {
  success: false;
  error: {
    code: number;
    message: string;
    details?: Record<string, unknown>;
  };
}

export interface LearningRoadmap {
  roadmap: LearningStep[];
  courses: Course[];
  certifications: CertificationSuggestion[];
  timeline: string;
}

export interface LearningStep {
  step: number;
  skill: string;
  description: string;
  estimated_weeks: number;
}

export interface Course {
  title: string;
  platform: string;
  url: string;
  skill: string;
}

export interface CertificationSuggestion {
  name: string;
  provider: string;
  skill: string;
}
