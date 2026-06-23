import { Link } from 'react-router-dom';
import { ROUTES } from '../utils/constants';

export default function NotFoundPage() {
  return (
    <div className="container text-center" style={{ paddingTop: '6rem' }}>
      <h1>404</h1>
      <p className="text-secondary" style={{ margin: '1rem 0 2rem' }}>
        The page you&apos;re looking for doesn&apos;t exist.
      </p>
      <Link to={ROUTES.HOME} className="btn btn--primary">
        Go Home
      </Link>
    </div>
  );
}
