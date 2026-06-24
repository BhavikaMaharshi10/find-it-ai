import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ROUTES } from '../utils/constants';
import DashboardPreview from '../components/landing/DashboardPreview';
import { IconBrain, IconSparkles, IconTarget, IconTrending, IconZap } from '../components/common/Icons';
import './LandingPage.scss';

const FEATURES = [
  {
    icon: IconBrain,
    title: 'Smart Resume Analysis',
    desc: 'Upload your resume and let AI extract skills, experience, and strengths with semantic understanding.',
  },
  {
    icon: IconSparkles,
    title: 'Semantic Job Matching',
    desc: 'RAG-powered recommendations with explainable match scores and confidence indicators.',
  },
  {
    icon: IconTarget,
    title: 'Skill Gap Analysis',
    desc: 'Identify missing skills and get personalized learning roadmaps tailored to your goals.',
  },
  {
    icon: IconTrending,
    title: 'Application Tracker',
    desc: 'Kanban board and list views to manage your job search pipeline with precision.',
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.4, 0, 0.2, 1] as const },
  },
};

export default function LandingPage() {
  return (
    <div className="landing">
      <div className="landing__orbs" aria-hidden="true">
        <div className="landing__orb landing__orb--1" />
        <div className="landing__orb landing__orb--2" />
        <div className="landing__orb landing__orb--3" />
      </div>

      <section className="landing__hero">
        <div className="container landing__hero-grid">
          <motion.div
            className="landing__hero-content"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <motion.div variants={itemVariants} className="landing__eyebrow">
              <IconZap size={14} />
              <span>AI-Powered Career Intelligence</span>
            </motion.div>

            <motion.h1 variants={itemVariants} className="landing__title">
              Find opportunities that{' '}
              <span className="gradient-text">actually fit.</span>
            </motion.h1>

            <motion.p variants={itemVariants} className="landing__subtitle">
              AI-powered job matching, career intelligence, and personalized growth
              recommendations.
            </motion.p>

            <motion.div variants={itemVariants} className="landing__cta">
              <Link to={ROUTES.REGISTER} className="btn btn--primary btn--lg">
                Get Started Free
              </Link>
              <Link to={ROUTES.LOGIN} className="btn btn--secondary btn--lg">
                Sign In
              </Link>
            </motion.div>

            <motion.div variants={itemVariants} className="landing__trust">
              <span>Semantic matching</span>
              <span className="landing__trust-dot" />
              <span>Explainable AI</span>
              <span className="landing__trust-dot" />
              <span>Skill roadmaps</span>
            </motion.div>
          </motion.div>

          <div className="landing__hero-visual">
            <DashboardPreview />
          </div>
        </div>
      </section>

      <section className="landing__features section">
        <div className="container">
          <motion.div
            className="landing__features-header"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <span className="ai-badge">Powered by AI</span>
            <h2>Everything you need to land your next role</h2>
            <p className="text-secondary">
              From resume analysis to application tracking — one intelligent platform.
            </p>
          </motion.div>

          <div className="landing__features-grid">
            {FEATURES.map((feature, i) => (
              <motion.div
                key={feature.title}
                className="landing__feature-card"
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <div className="landing__feature-icon">
                  <feature.icon size={22} />
                </div>
                <h3>{feature.title}</h3>
                <p className="text-secondary">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="landing__cta-section">
        <div className="container">
          <motion.div
            className="landing__cta-card"
            initial={{ opacity: 0, scale: 0.98 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <h2>Ready to find your perfect match?</h2>
            <p className="text-secondary">
              Join FindItAI and let intelligence guide your career journey.
            </p>
            <Link to={ROUTES.REGISTER} className="btn btn--primary btn--lg">
              Start for free
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
