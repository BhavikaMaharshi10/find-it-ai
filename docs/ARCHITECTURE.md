# FindItAI — System Architecture

## Overview

FindItAI is a full-stack AI-powered job search platform built with a **Clean Architecture** approach, separating concerns across presentation, application, domain, and infrastructure layers.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENT (React + Vite)                           │
│  Pages → Components → Hooks → Store (Zustand) → API Services (Axios)  │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ REST API (JWT)
┌──────────────────────────────────▼──────────────────────────────────────┐
│                    API LAYER (Django REST Framework)                   │
│  Views → Serializers → Permissions → Pagination → Versioning (/v1/)   │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│                      SERVICE LAYER (Business Logic)                    │
│  ResumeAnalysis │ Embedding │ Recommendation │ RAG │ Learning          │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│                    REPOSITORY LAYER (Data Access)                      │
│  BaseRepository → App-specific repositories → Django ORM               │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────┐
│              INFRASTRUCTURE (PostgreSQL + pgvector + Gemini)           │
│  Structured Data │ Vector Embeddings │ AI Completions │ File Storage  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Architectural Decisions

### 1. Modular Django Apps

Each domain concern is isolated into its own Django app:

| App | Responsibility |
|-----|----------------|
| `accounts` | User model, JWT auth, password management |
| `profiles` | User profile, preferences, avatar |
| `resumes` | PDF upload, parsing, structured extraction |
| `jobs` | Job listings, search, filters, saved jobs |
| `recommendations` | AI matching, skill gaps, learning paths |
| `applications` | Application tracker (Kanban + list) |
| `analytics` | Dashboard metrics and charts |

**Why:** Enables independent development, testing, and deployment of each domain. Follows Django's "reusable apps" philosophy while maintaining clear boundaries.

### 2. Service Layer Pattern

Business logic lives in `backend/services/`, not in views or models.

```
View → Serializer (validation) → Service (logic) → Repository (data) → Model
```

**Why:** Views stay thin (HTTP concerns only). Services are unit-testable without HTTP. Logic is reusable across API endpoints, management commands, and Celery tasks.

### 3. Repository Pattern

`core/repositories.py` provides a generic `BaseRepository` with CRUD operations. App-specific repositories extend it for complex queries.

**Why:** Decouples data access from business logic. Makes it easy to swap ORM queries or add caching without touching services.

### 4. RAG Pipeline Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  INGESTION   │───▶│  RETRIEVAL   │───▶│  GENERATION  │
│              │    │              │    │              │
│ PDF → Text   │    │ Query Embed  │    │ Context +    │
│ → Embed      │    │ → Top-K      │    │ Prompt →     │
│ → pgvector   │    │ → Similarity │    │ OpenAI →     │
│              │    │              │    │ Response     │
└──────────────┘    └──────────────┘    └──────────────┘
```

- **Ingestion:** Resume PDFs and job descriptions are embedded via Gemini `gemini-embedding-001` (768 dimensions) and stored in pgvector columns.
- **Retrieval:** Cosine similarity search (`<=>` operator) retrieves top-K relevant jobs for a user's resume embedding.
- **Generation:** Retrieved context + structured prompts generate explainable recommendations, skill gap analysis, and learning roadmaps.

### 5. API Versioning

All endpoints are prefixed with `/api/v1/`. URL path versioning allows breaking changes in future versions without disrupting existing clients.

### 6. Environment-Based Configuration

Settings are split into `base.py`, `development.py`, `production.py`, and `test.py`. The active module is selected via `DJANGO_SETTINGS_MODULE`.

### 7. Frontend Architecture

```
src/
├── api/          → Axios instances, interceptors, endpoint definitions
├── components/   → Reusable UI (common, dashboard, jobs, profile, forms)
├── hooks/        → Custom React hooks (auth, queries, theme)
├── layouts/      → Page layouts (Auth, Dashboard, Public)
├── pages/        → Route-level page components
├── routes/       → React Router configuration + guards
├── services/     → Business logic wrappers around API calls
├── store/        → Zustand stores (auth, theme, UI state)
├── styles/       → SCSS architecture (abstracts, base, components, themes)
├── types/        → TypeScript interfaces and types
└── utils/        → Helpers (formatting, validation, constants)
```

**State management strategy:**
- **Server state:** TanStack Query (caching, refetching, optimistic updates)
- **Client state:** Zustand (auth tokens, theme, UI preferences)
- **Form state:** React Hook Form (validation, submission)

### 8. Security Architecture

| Layer | Mechanism |
|-------|-----------|
| Authentication | JWT (access + refresh tokens with rotation) |
| Authorization | DRF permissions + `IsOwner` object-level checks |
| Password | Django's PBKDF2 hasher + validation rules |
| API | Rate limiting, input validation, CORS whitelist |
| Secrets | Environment variables only (`.env`, never committed) |
| Production | HTTPS, HSTS, secure cookies, XSS protection |

## Database Schema (Preview — Phase 2)

```
users ──┬── profiles
        ├── resumes ── resume_embeddings
        ├── saved_jobs ── jobs ── job_embeddings
        ├── applications
        ├── recommendations ── skill_gaps
        └── ai_logs
```

See [ER-DIAGRAM.md](./ER-DIAGRAM.md) for the full entity-relationship diagram.

## Deployment Architecture

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

## Technology Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Vector DB | pgvector (not Pinecone/Weaviate) | Single database for structured + vector data; simpler ops |
| Embeddings | gemini-embedding-001 | 768 dims, strong semantic quality via Google Gemini |
| Auth | JWT (not sessions) | Stateless API; works with SPA + mobile clients |
| State | Zustand (not Redux) | Minimal boilerplate; sufficient for this app's complexity |
| Styling | SCSS modules | Design tokens, theming, component-scoped styles |
| No Docker | Vercel + Render + Neon | Simpler deployment; managed services handle infra |

## Phase Roadmap

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Architecture & folder structure | ✅ Current |
| 2 | Database models & migrations | Pending |
| 3 | Backend REST APIs | Pending |
| 4 | JWT authentication | Pending |
| 5 | RAG + pgvector + Gemini | Pending |
| 6 | React frontend pages | Pending |
| 7 | Dashboard & analytics | Pending |
| 8 | Testing | Pending |
| 9 | Deployment | Pending |
