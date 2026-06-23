import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore, useUIStore } from '../store';
import { ROUTES } from '../utils/constants';
import {
  IconDashboard,
  IconSearch,
  IconSparkles,
  IconBookmark,
  IconClipboard,
  IconFile,
  IconUser,
  IconSettings,
  IconMenu,
} from '../components/common/Icons';
import './DashboardLayout.scss';

const NAV_ITEMS = [
  { to: ROUTES.DASHBOARD, label: 'Dashboard', icon: IconDashboard },
  { to: ROUTES.JOBS, label: 'Job Search', icon: IconSearch },
  { to: ROUTES.RECOMMENDATIONS, label: 'Recommendations', icon: IconSparkles },
  { to: ROUTES.SAVED_JOBS, label: 'Saved Jobs', icon: IconBookmark },
  { to: ROUTES.APPLICATIONS, label: 'Applications', icon: IconClipboard },
  { to: ROUTES.RESUME, label: 'Resume', icon: IconFile },
  { to: ROUTES.PROFILE, label: 'Profile', icon: IconUser },
  { to: ROUTES.SETTINGS, label: 'Settings', icon: IconSettings },
];

export default function DashboardLayout() {
  const { user, clearAuth } = useAuthStore();
  const { sidebarOpen, toggleSidebar } = useUIStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    clearAuth();
    navigate(ROUTES.LOGIN);
  };

  return (
    <div className={`dashboard-layout ${sidebarOpen ? '' : 'dashboard-layout--collapsed'}`}>
      <aside className="dashboard-layout__sidebar" aria-label="Sidebar navigation">
        <div className="dashboard-layout__sidebar-inner">
          <div className="dashboard-layout__sidebar-header">
            <span className="dashboard-layout__logo">
              <IconSparkles size={20} />
              FindIt<span className="gradient-text">AI</span>
            </span>
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
                <item.icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>

          <div className="dashboard-layout__sidebar-footer">
            <button type="button" className="btn btn--ghost dashboard-layout__logout" onClick={handleLogout}>
              Log out
            </button>
          </div>
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
            <IconMenu size={22} />
          </button>
          <div className="dashboard-layout__user">
            {user && (
              <div className="dashboard-layout__user-info">
                <div className="dashboard-layout__avatar">
                  {user.first_name?.[0]}{user.last_name?.[0]}
                </div>
                <span>
                  {user.first_name} {user.last_name}
                </span>
              </div>
            )}
          </div>
        </header>

        <main className="dashboard-layout__main">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.25 }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
