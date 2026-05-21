# Hugging Face Spaces Deployment Guide

## Goal
Deploy the ctracker interview analyzer (FastAPI + React + ML models) on Hugging Face Spaces free tier for a public portfolio demo — $0 cost, no credit card required.

## Architecture

```
User ──HTTPS──→ HF Spaces Proxy ──→ Docker Container ──→ Uvicorn (port $PORT)
                                      │              │
                                      │   uvicorn    │
                                      │   api.server │
                                      │   :app       │
                                      └──────┬───────┘
                                      ┌──────┴───────┐
                                      │  /data/       │  ← persistent volume
                                      │  ├── app.db   │  (survives restarts)
                                      │  ├── uploads/ │
                                      │  ├── temp/    │
                                      │  └── reports/ │
                                      └──────────────┘
                                      ┌──────────────┐
                                      │ ~/.cache/     │  ← ML models persisted
                                      │ (HF managed)  │
                                      └──────────────┘
```

### Database Persistence (Key Detail)

HF Spaces mounts a **persistent volume at `/data`** that survives container restarts and sleep/wake cycles. The app uses this for:
- **SQLite database** → `/data/app.db`
- **Uploaded videos** → `/data/uploads/`
- **Temp files** → `/data/temp/`
- **Report files** → `/data/reports/`

ML model caches (`~/.cache/`) are also persisted by HF Spaces, so model downloads only happen on the first deploy.

**What gets wiped:** Only a Docker rebuild (code push) triggers a full reset. Simple restarts or sleep/wake keep `/data` intact.

## Step-by-Step

### 1. Code Changes (Already Applied)

The following changes are already in the repo:

**a) Port configurable** via `PORT` env var in `api/server.py:__main__`:
```python
port = int(os.getenv("PORT", 8000))
```

**b) Database path configurable** via `DATABASE_PATH` env var in `database/init.py`:
```python
DB_PATH = os.getenv("DATABASE_PATH", "/app/database/app.db")
```

**c) Storage dirs configurable** via `UPLOAD_DIR`, `TEMP_DIR`, `REPORTS_DIR` env vars in `utils/file_manager.py`:
```python
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", ...))
```

**d) Dockerfile** at project root — multi-stage build (Node → Python), uses `/data` for persistence:
- Stage 1: `node:20-alpine` — builds React frontend
- Stage 2: `python:3.11-slim` — ffmpeg + pip deps + `en_core_web_sm` + runs uvicorn on `$PORT`
- Sets `DATABASE_PATH=/data/app.db`, `UPLOAD_DIR=/data/uploads`, etc.

All you need to do is push the code to GitHub and create the HF Space.

### 2. Create HF Space

1. Sign up at [huggingface.co](https://huggingface.co) (free, no credit card)
2. Click your avatar → **New Space**
3. Space name: `ctracker` (or whatever you choose)
4. License: `MIT`
5. Space SDK: **Docker**
6. Hardware: **CPU basic** (free, 2 vCPU, 16GB RAM)
7. Click **Create Space**
8. Go to **Settings** → set **Sleep time** to **1 hour** (or whatever you prefer — free spaces sleep after 48h by default, but you can set shorter to avoid inactivity charges if they ever introduce them)

### 3. Connect GitHub Repo

In your HF Space settings:
1. **Repository** → **Link to GitHub repository**
2. Authorize Hugging Face to access your GitHub
3. Select your ctracker repo
4. Branch: `main` (or whichever branch)
5. Enable **Automatic builds** — HF will rebuild on every push

Alternatively, push directly to HF's Git:
```bash
git remote add hf https://huggingface.co/spaces/<YOUR_USER>/ctracker
git push hf main
```

### 4. First Build

After connecting or pushing:
1. HF Spaces builds the Docker image (takes 5-10 min first time — caching speeds up subsequent builds)
2. The ML models (Whisper, DeepFace) download on first startup (~2-3 min cold start)
3. Once running, your app is live at `https://<YOUR_USER>-ctracker.hf.space`

**Configure Space to not sleep (optional):**
HF free spaces sleep after 48h of inactivity. You can:
- Accept the ~1-2 min cold start when someone visits after sleep
- Upgrade to $0 "no sleep" isn't available on free tier, but you can ping the space periodically with a cron job or uptime monitor

### 5. Maintenance

| Task | How |
|------|-----|
| Update app | Push to GitHub → HF auto-builds |
| View logs | HF Space → **Logs** tab |
| Restart | HF Space → **Settings** → **Restart** |
| Check resource usage | HF Space → **Settings** → **Resource usage** |
| Clear storage | HF Space → **Settings** → **Factory restart** (wipes everything) |

## Important Notes

### Storage IS Persistent (Mostly)
- `/data/` directory is a **persistent volume** — survives restarts and sleep/wake cycles
- ML model cache at `~/.cache/` is also persisted by HF Spaces
- **Only a Docker rebuild** (pushing new code) wipes the persistent storage
- So user accounts, interviews, and uploaded videos survive across visits

### Storage Limits
- HF Spaces free tier: shared 50GB across all your spaces
- Video uploads can fill this up. The app's cleanup script helps, but you may need to occasionally purge old videos

### Processing Limits
- Free CPU: 2 vCPU, 16GB RAM
- Whisper `base` model fits comfortably (~1GB RAM loaded)
- DeepFace + TensorFlow is the heaviest component (~2-3GB)
- Total memory usage during full analysis: ~4-5GB (well within 16GB limit)

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Container crashes on start | OOM during model load | Check HF Space logs; may need to optimize model loading order |
| `PORT` not set | HF env not passed | Verify Dockerfile uses `$PORT` not hardcoded port |
| Build fails (no space) | Docker layer too large | Check `docker build` output; reduce pip cache |
| Space won't build | Dockerfile error | Use HF Space **Logs → Build** tab to see build output |
| Slow first request | Models downloading | Wait 2-3 min; subsequent requests are fast |

## Costs

- **Hugging Face Free Tier:** $0/mo (2 vCPU, 16GB RAM, 50GB storage)
- **GitHub Free:** $0/mo (public repo)
- **Domain:** `*.hf.space` subdomain is free
- **Total:** $0

## What You DON'T Need

- No credit card
- No cloud account
- No domain purchase
- No reverse proxy config
- No systemd service
- No SSL setup
