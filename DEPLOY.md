# Deployment Guide

## Required Environment Variables

Set these in your hosting platform:

- `SECRET_KEY` = long random secret key
- `GOOGLE_GEMINI_API_KEY` = your Gemini API key
- `GOOGLE_GEMINI_MODEL` = `gemini-2.5-flash-lite` (optional)
- `GOOGLE_GEMINI_API_BASE` = `https://generativelanguage.googleapis.com/v1beta/models` (optional)
- `USE_SQLITE` = `true` (for basic deployment) or `false` when using Postgres
- `DATABASE_URL` = Postgres URL when `USE_SQLITE=false`
- `PORT` = auto-set by most platforms

## Option 1: Deploy with Docker (any cloud VM/container service)

Build and run locally:

```bash
docker build -t fitfinder .
docker run --env-file .env -p 5000:5000 fitfinder
```

## Option 2: Render / Railway style deploy (Procfile)

Use these settings:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn -w ${GUNICORN_WORKERS:-2} -b 0.0.0.0:${PORT:-5000} app:app`

## Health Check

Use:

- `/api/health`

Expected example response:

```json
{
  "status": "healthy",
  "gemini": true,
  "gemini_api_key_loaded": true,
  "tryon_provider": "local"
}
```
