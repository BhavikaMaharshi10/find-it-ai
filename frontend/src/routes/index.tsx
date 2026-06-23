import { lazy, Suspense } from 'react';
import { createBrowserRouter } from 'react-router-dom';
import { ProtectedRoute, PublicRoute } from './guards';
import { ROUTES } from '../utils/constants';

const PublicLayout = lazy(() => import('../layouts/PublicLayout'));
const DashboardLayout = lazy(() => import('../layouts/DashboardLayout'));
const LandingPage = lazy(() => import('../pages/LandingPage'));
const LoginPage = lazy(() => import('../pages/LoginPage'));
const RegisterPage = lazy(() => import('../pages/RegisterPage'));
const ForgotPasswordPage = lazy(() => import('../pages/ForgotPasswordPage'));
const DashboardPage = lazy(() => import('../pages/DashboardPage'));
const JobsPage = lazy(() => import('../pages/JobsPage'));
const RecommendationsPage = lazy(() => import('../pages/RecommendationsPage'));
const SavedJobsPage = lazy(() => import('../pages/SavedJobsPage'));
const ApplicationsPage = lazy(() => import('../pages/ApplicationsPage'));
const ResumePage = lazy(() => import('../pages/ResumePage'));
const ProfilePage = lazy(() => import('../pages/ProfilePage'));
const SettingsPage = lazy(() => import('../pages/SettingsPage'));
const NotFoundPage = lazy(() => import('../pages/NotFoundPage'));

function PageLoader() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
      <p>Loading...</p>
    </div>
  );
}

function withSuspense(Component: React.ComponentType) {
  return (
    <Suspense fallback={<PageLoader />}>
      <Component />
    </Suspense>
  );
}

export const router = createBrowserRouter([
  {
    element: <PublicRoute />,
    children: [
      {
        element: withSuspense(PublicLayout),
        children: [
          { path: ROUTES.HOME, element: withSuspense(LandingPage) },
          { path: ROUTES.LOGIN, element: withSuspense(LoginPage) },
          { path: ROUTES.REGISTER, element: withSuspense(RegisterPage) },
          { path: ROUTES.FORGOT_PASSWORD, element: withSuspense(ForgotPasswordPage) },
        ],
      },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: withSuspense(DashboardLayout),
        children: [
          { path: ROUTES.DASHBOARD, element: withSuspense(DashboardPage) },
          { path: ROUTES.JOBS, element: withSuspense(JobsPage) },
          { path: ROUTES.RECOMMENDATIONS, element: withSuspense(RecommendationsPage) },
          { path: ROUTES.SAVED_JOBS, element: withSuspense(SavedJobsPage) },
          { path: ROUTES.APPLICATIONS, element: withSuspense(ApplicationsPage) },
          { path: ROUTES.RESUME, element: withSuspense(ResumePage) },
          { path: ROUTES.PROFILE, element: withSuspense(ProfilePage) },
          { path: ROUTES.SETTINGS, element: withSuspense(SettingsPage) },
        ],
      },
    ],
  },
  { path: '*', element: withSuspense(NotFoundPage) },
]);
