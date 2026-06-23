import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore, useThemeStore, useUIStore } from '../store';
import { ROUTES } from '../utils/constants';
import './DashboardLayout.scss';

const NAV_ITEMS = [
  { to: ROUTES.DASHBOARD, label: 'Dashboard', icon: '📊' },
  { to: ROUTES.JOBS, label: 'Job Search', icon: '🔍' },
  { to: ROUTES.RECOMMENDATIONS, label: 'Recommendations', icon: '✨' },
  { to: ROUTES.SAVED_JOBS, label: 'Saved Jobs', icon: '🔖' },
  { to: ROUTES.APPLICATIONS, label: 'Applications', icon: '📋' },
  { to: ROUTES.RESUME, label: 'Resume', icon: '📄' },
  { to: ROUTES.PROFILE, label: 'Profile', icon: '👤' },
  { to: ROUTES.SETTINGS, label: 'Settings', icon: '⚙️' },
];

export default function DashboardLayout() {
  const { user, clearAuth } = useAuthStore();
  const { theme, toggleTheme } = useThemeStore();
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    clearAuth();
    navigate(ROUTES.LOGIN);
  };

  return (
    <div className={`dashboard-layout ${sidebarOpen ? '' : 'dashboard-layout--collapsed'}`}>
      <aside className="dashboard-layout__sidebar" aria-label="Sidebar navigation">
        <div className="dashboard-layout__sidebar-header">
          <span className="dashboard-layout__logo">FindIt<span>AI</span></span>
        </div>
        <nav className="dashboard-layout__nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `dashboard-layout__nav-item ${isActive ? 'dashboard-layout__nav-item--active' : ''}`
              }
            >
              <span aria-hidden="true">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="dashboard-layout__sidebar-footer">
          <button
            type="button"
            className="dashboard-layout__theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
          <button type="button" className="btn btn--ghost" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </aside>

      <div className="dashboard-layout__content">
        <header className="dashboard-layout__header">
          <button
            type="button"
            className="dashboard-layout__menu-btn"
            onClick={toggleSidebar}
            aria-label="Toggle sidebar"
          >
            ☰
          </button>
          <div className="dashboard-layout__user">
            {user && (
              <span>
                {user.first_name} {user.last_name}
              </span>
            )}
          </div>
        </header>
        <main className="dashboard-layout__main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
