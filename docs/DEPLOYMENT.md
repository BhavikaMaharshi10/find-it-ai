# FindItAI — Deployment Guide

Deployment targets: **Vercel** (frontend), **Render** (backend), **Neon** (PostgreSQL).

---

## Database (Neon)

1. Create a project at [neon.tech](https://neon.tech)
2. Create a database named `finditai`
3. Enable the pgvector extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

4. Copy the connection string (format: `postgresql://user:pass@host/db?sslmode=require`)

---

## Backend (Render)

### Option A: Blueprint (`render.yaml`)

The repo includes a Render blueprint. Connect the repo and set these **manual** env vars:

| Variable | Example |
|----------|---------|
| `ALLOWED_HOSTS` | `finditai-api.onrender.com` |
| `DATABASE_URL` | Neon connection string |
| `CORS_ALLOWED_ORIGINS` | `https://your-app.vercel.app` |
| `GEMINI_API_KEY` | Your Google Gemini API key |

The blueprint auto-configures:

- Production Django settings
- `collectstatic` + `migrate` on build
- Gunicorn with **180s timeout** (required for live job search / AI matching)
- Health check at `/api/v1/health/`

### Option B: Manual Web Service

- **Root Directory:** `backend`
- **Build Command:**

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput
```

- **Start Command:**

```bash
gunicorn config.wsgi:application -c gunicorn.conf.py
```

- **Health Check Path:** `/api/v1/health/`

### Environment Variables

| Variable | Value |
|----------|-------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `SECRET_KEY` | Generate a secure random key |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `your-app.onrender.com` |
| `DATABASE_URL` | Neon connection string |
| `CORS_ALLOWED_ORIGINS` | `https://your-app.vercel.app` |
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-001` |
| `GEMINI_CHAT_MODEL` | `gemini-2.5-flash` |
| `EMBEDDING_DIMENSIONS` | `768` |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | `30` |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | `7` |
| `GUNICORN_TIMEOUT` | `180` |
| `RATELIMIT_ENABLE` | `True` |

### Post-deploy

```bash
python manage.py createsuperuser
```

---

## Frontend (Vercel)

### 1. Import Project

- **Framework Preset:** Vite
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`

### 2. Environment Variables

| Variable | Value |
|----------|-------|
| `VITE_API_BASE_URL` | `https://your-app.onrender.com/api/v1` |

### 3. `vercel.json`

SPA routing and asset caching are configured in `frontend/vercel.json`.

---

## Production Checklist

- [ ] `SECRET_KEY` is a unique, secure random string
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` includes your Render domain
- [ ] `CORS_ALLOWED_ORIGINS` includes your Vercel domain
- [ ] Neon pgvector extension is enabled
- [ ] Database migrations run on deploy (included in build command)
- [ ] Static files collected (`collectstatic`)
- [ ] Gemini API key is set with usage limits
- [ ] Health check returns `200` at `/api/v1/health/`
- [ ] HTTPS enforced (Render + Vercel handle this)

---

## Rate Limits (enabled by default)

| Endpoint | Limit |
|----------|-------|
| Login / Register | 20/min, 10/min per IP |
| Live job search | 30/hour per user |
| Generate recommendations | 15/hour per user |
| Resume upload | 10/hour per user |
| Learning roadmap | 30/hour per user |

---

## Known Production Notes

- **Long requests:** Live job search and AI recommendations can take 30–90 seconds. Gunicorn timeout is set to 180s.
- **Resume PDFs:** Parsed text and embeddings are stored in the database. Original PDF files use local disk on Render (ephemeral). Re-upload after redeploy if you need the file again.
- **CI:** GitHub Actions runs backend unit tests and frontend build on push/PR.

---

## Generating a Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Environment Variables Reference

### Backend (production)

```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<generate-secure-key>
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
DATABASE_URL=postgresql://user:pass@host/finditai?sslmode=require
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app
GEMINI_API_KEY=your-gemini-api-key
GUNICORN_TIMEOUT=180
RATELIMIT_ENABLE=True
```

### Frontend

```env
VITE_API_BASE_URL=https://your-app.onrender.com/api/v1
```
