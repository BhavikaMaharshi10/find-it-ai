# FindItAI — Deployment Guide

Deployment targets: **Vercel** (frontend), **Render** (backend), **Neon** (PostgreSQL). No Docker required.

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

### 1. Create Web Service

- **Repository:** Connect your GitHub repo
- **Root Directory:** `backend`
- **Runtime:** Python 3
- **Build Command:**

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

- **Start Command:**

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

### 2. Environment Variables

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
| `GEMINI_CHAT_MODEL` | `gemini-2.0-flash` |
| `EMBEDDING_DIMENSIONS` | `768` |
| `CORS_ALLOWED_ORIGINS` | `https://your-app.vercel.app` |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | `30` |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | `7` |

### 3. Run Migrations

After first deploy, open the Render shell:

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. render.yaml (Optional)

A `render.yaml` blueprint is included in the repo root for infrastructure-as-code deployment.

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

### 3. vercel.json

Routing is configured via `frontend/vercel.json` for SPA fallback.

---

## Production Checklist

- [ ] `SECRET_KEY` is a unique, secure random string
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` includes your Render domain
- [ ] `CORS_ALLOWED_ORIGINS` includes your Vercel domain
- [ ] Neon pgvector extension is enabled
- [ ] Database migrations are applied
- [ ] Static files collected (`collectstatic`)
- [ ] Gemini API key is set with usage limits
- [ ] HTTPS enforced (Render + Vercel handle this)

---

## Environment Variables Reference

### Backend (.env)

```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<generate-secure-key>
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
DATABASE_URL=postgresql://user:pass@host/finditai?sslmode=require
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app
GEMINI_API_KEY=your-gemini-api-key
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_CHAT_MODEL=gemini-2.0-flash
EMBEDDING_DIMENSIONS=768
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app
```

### Frontend (.env)

```env
VITE_API_BASE_URL=https://your-app.onrender.com/api/v1
```

---

## Generating a Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
