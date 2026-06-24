# FindItAI — AI-Powered Job Search Assistant

> **AI-Powered Job Search Assistant | React, Django, PostgreSQL, Gemini, RAG, pgvector**

An intelligent job search platform that analyzes resumes, semantically matches candidates with relevant jobs, identifies skill gaps, and generates personalized career recommendations using Large Language Models, Retrieval-Augmented Generation (RAG), vector embeddings, and semantic search.

![FindItAI Dashboard](docs/screenshots/dashboard.png)
*Screenshot placeholder — add after Phase 7*

---

## Features

- **Resume Management** — Upload PDF resumes, extract skills, education, experience, projects, and certifications
- **AI Resume Analysis** — Gemini-powered candidate summaries, strength evaluation, and skill detection
- **Semantic Job Matching** — RAG pipeline with pgvector embeddings for explainable recommendations
- **Skill Gap Analysis** — Identify missing skills with personalized learning roadmaps
- **Job Discovery** — Search, filter, and sort jobs by location, remote, skills, and experience
- **Application Tracker** — Kanban board and list views with status pipeline
- **Dashboard Analytics** — Match scores, skill gaps, application trends, and saved jobs
- **JWT Authentication** — Secure auth with refresh tokens, password reset, and profile management

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐
│   Vercel    │────▶│   Render    │────▶│  Neon PostgreSQL │
│  (Frontend) │     │  (Backend)  │     │  (+ pgvector)    │
└─────────────┘     └─────────────┘     └──────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Gemini API │
                    └─────────────┘
```

**Tech Stack:**

| Layer | Technologies |
|-------|-------------|
| Frontend | React 19, TypeScript, Vite, TanStack Query, Zustand, SCSS, Framer Motion |
| Backend | Python 3.12+, Django 5, Django REST Framework, JWT |
| Database | PostgreSQL, pgvector |
| AI | Google Gemini API, RAG, Vector Embeddings |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture decisions and [docs/ER-DIAGRAM.md](docs/ER-DIAGRAM.md) for the database schema.

---

## Project Structure

```
find-it-ai/
├── backend/
│   ├── apps/
│   │   ├── accounts/        # Auth & user management
│   │   ├── profiles/        # User profiles
│   │   ├── resumes/         # Resume upload & parsing
│   │   ├── jobs/            # Job listings & search
│   │   ├── recommendations/ # AI matching engine
│   │   ├── applications/    # Application tracker
│   │   └── analytics/       # Dashboard metrics
│   ├── core/                # Pagination, exceptions, repositories
│   ├── services/            # Business logic layer
│   ├── embeddings/          # pgvector utilities
│   ├── rag/                 # RAG pipeline
│   ├── prompts/             # Gemini prompt templates
│   ├── utils/               # Shared utilities
│   └── config/              # Django settings
├── frontend/
│   └── src/
│       ├── api/             # Axios client & endpoints
│       ├── components/      # Reusable UI components
│       ├── hooks/           # Custom React hooks
│       ├── layouts/         # Page layouts
│       ├── pages/           # Route pages
│       ├── routes/          # Router config & guards
│       ├── store/           # Zustand stores
│       ├── styles/          # SCSS architecture
│       ├── types/           # TypeScript types
│       └── utils/           # Helpers & constants
└── docs/                    # Architecture & deployment docs
```

---

## Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 15+ with [pgvector](https://github.com/pgvector/pgvector) extension
- Google Gemini API key ([Google AI Studio](https://aistudio.google.com/apikey))

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database and Gemini credentials

# Run migrations (PostgreSQL + pgvector required)
python scripts/enable_pgvector.py
python manage.py migrate

# Seed sample jobs (optional — for local dev without network)
python manage.py seed_jobs

# Sync live jobs from free public APIs (Remotive, Lever, Greenhouse — no API keys)
python manage.py sync_jobs

# Skip embeddings if Gemini quota is low (jobs sync, matching needs embeddings later)
python manage.py sync_jobs --skip-embeddings

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start development server
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies API requests to `http://localhost:8000`.

### Enable pgvector

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## API Documentation

All endpoints are versioned under `/api/v1/`:

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/register/` | User registration |
| `POST /api/v1/auth/login/` | JWT login |
| `POST /api/v1/auth/logout/` | Token blacklist logout |
| `POST /api/v1/auth/token/refresh/` | Refresh access token |
| `POST /api/v1/auth/security-question/` | Get security question for email |
| `POST /api/v1/auth/reset-password/` | Reset password with security answer |
| `POST /api/v1/auth/change-password/` | Change password |
| `GET  /api/v1/auth/me/` | Current user |
| `GET  /api/v1/profile/` | User profile |
| `GET  /api/v1/resume/` | Resume list |
| `POST /api/v1/resume/upload/` | Upload PDF resume |
| `GET  /api/v1/jobs/` | Search & filter jobs |
| `GET  /api/v1/recommendations/` | AI job recommendations |
| `GET  /api/v1/applications/` | Application tracker |
| `GET  /api/v1/dashboard/stats/` | Dashboard analytics |

Full API documentation will be available via DRF browsable API in development mode.

---

## Deployment

| Service | Platform | Guide |
|---------|----------|-------|
| Frontend | Vercel | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#frontend-vercel) |
| Backend | Render | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#backend-render) |
| Database | Neon PostgreSQL | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#database-neon) |

---

## Development Phases

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Architecture & folder structure | ✅ Complete |
| 2 | Database models & migrations | ✅ Complete |
| 3 | Backend REST APIs | ✅ Complete |
| 4 | JWT authentication | ✅ Complete |
| 5 | RAG + pgvector + Gemini | ✅ Complete |
| 6 | React frontend pages | ✅ Complete |
| 7 | Dashboard & analytics | ✅ Complete |
| 8 | Testing | ✅ Complete |
| 9 | Deployment | ✅ Complete |

---

## Resume-Ready Description

> **AI-Powered Job Search Assistant | React, Django, PostgreSQL, Gemini, RAG, pgvector**
>
> Built a full-stack AI job recommendation platform using React, Django REST Framework, and PostgreSQL.
> Implemented Retrieval-Augmented Generation (RAG) with pgvector embeddings for semantic job matching.
> Developed resume parsing, skill-gap analysis, and explainable job recommendations using Google Gemini APIs.
> Designed scalable REST APIs, authentication workflows, and personalized dashboards for job tracking and analytics.

---

## License

MIT
