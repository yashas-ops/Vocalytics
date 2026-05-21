# Vocalytics

AI-powered interview analyzer. Upload or record mock interviews and get instant feedback on speaking pace, filler words, eye contact, facial expressions, and confidence — all running locally with open-source models.

## Tech Stack

- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Backend:** FastAPI (Python)
- **ML:** faster-whisper, MediaPipe, DeepFace, spaCy
- **Storage:** SQLite

## Local Development

```bash
# Backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m uvicorn api.server:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` (Vite dev server proxies API to port 8000).

## Deployment

Deployed on Hugging Face Spaces: `https://yashas-ops-Vocalytics.hf.space`

See `docs/superpowers/specs/2026-05-21-huggingface-spaces-deployment.md` for setup details.
