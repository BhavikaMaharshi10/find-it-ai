import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ROUTES } from '../utils/constants';
import './LandingPage.scss';

export default function LandingPage() {
  return (
    <div className="landing">
      <section className="landing__hero">
        <div className="container">
          <motion.div
            className="landing__hero-content"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="landing__title">
              Find Your Dream Job with <span>AI</span>
            </h1>
            <p className="landing__subtitle">
              FindItAI analyzes your resume, matches you with relevant opportunities,
              identifies skill gaps, and generates personalized career recommendations
              using advanced AI and semantic search.
            </p>
            <div className="landing__cta">
              <Link to={ROUTES.REGISTER} className="btn btn--primary btn--lg">
                Get Started Free
              </Link>
              <Link to={ROUTES.LOGIN} className="btn btn--secondary btn--lg">
                Sign In
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="landing__features section">
        <div className="container">
          <h2 className="text-center">Powered by AI</h2>
          <div className="landing__features-grid">
            {[
              {
                title: 'Smart Resume Analysis',
                desc: 'Upload your resume and let AI extract skills, experience, and strengths.',
              },
              {
                title: 'Semantic Job Matching',
                desc: 'RAG-powered recommendations with explainable match scores.',
              },
              {
                title: 'Skill Gap Analysis',
                desc: 'Identify missing skills and get personalized learning roadmaps.',
              },
              {
                title: 'Application Tracker',
                desc: 'Kanban board and list views to manage your job search pipeline.',
              },
            ].map((feature, i) => (
              <motion.div
                key={feature.title}
                className="card landing__feature-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
              >
                <h3>{feature.title}</h3>
                <p className="text-secondary">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
