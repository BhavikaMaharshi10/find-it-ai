import { Outlet, Link } from 'react-router-dom';
import { ROUTES } from '../utils/constants';
import './PublicLayout.scss';

export default function PublicLayout() {
  return (
    <div className="public-layout">
      <header className="public-layout__header">
        <div className="container public-layout__header-inner">
          <Link to={ROUTES.HOME} className="public-layout__logo">
            FindIt<span>AI</span>
          </Link>
          <nav className="public-layout__nav" aria-label="Main navigation">
            <Link to={ROUTES.LOGIN} className="btn btn--ghost">
              Log in
            </Link>
            <Link to={ROUTES.REGISTER} className="btn btn--primary">
              Get Started
            </Link>
          </nav>
        </div>
      </header>
      <main className="public-layout__main">
        <Outlet />
      </main>
      <footer className="public-layout__footer">
        <div className="container">
          <p>&copy; {new Date().getFullYear()} FindItAI. AI-Powered Job Search.</p>
        </div>
      </footer>
    </div>
  );
}
