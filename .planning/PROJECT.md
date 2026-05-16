# AI Interview Analyzer

## What This Is

A fully local AI-powered web application that analyzes mock interview videos. Users upload or record video interviews, and the system evaluates speech-to-text, speaking speed, filler words, eye contact, facial expressions, and confidence — generating a comprehensive feedback report. Built for interview practice and as a portfolio-ready MVP.

## Core Value

A user can record or upload a mock interview and immediately get actionable, data-driven feedback on their communication and presentation skills — all running locally with no cloud dependencies.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] User can upload video (mp4, mov, avi) or record via webcam
- [ ] System extracts audio from video using moviepy/ffmpeg
- [ ] System converts speech to text using local Whisper (tiny/base model for CPU)
- [ ] System detects and counts filler words (um, uh, like, basically, literally, you know)
- [ ] System calculates speaking speed in WPM and classifies as slow/good/fast
- [ ] System detects eye contact percentage using MediaPipe Face Mesh
- [ ] System detects dominant emotion(s) using DeepFace or FER
- [ ] System computes a confidence score (0-100) using weighted heuristic
- [ ] System generates template-based feedback report (strengths, weaknesses, tips)
- [ ] Dashboard displays: video preview, transcript, confidence score, speed, eye contact chart, emotion analytics, filler breakdown, feedback report
- [ ] All analysis data stored in local SQLite database with interview history

### Out of Scope

- User authentication / login system — local single-user app
- Payment or subscription systems
- Cloud deployment or hosting
- Docker / containerization
- Any paid API usage (OpenAI, cloud services, etc.)
- Chatbot or conversational AI features
- Resume parsing or job search / job board features
- Real-time video processing (post-recording analysis only)
- Advanced gaze estimation research models

## Context

- Runs entirely on a laptop with no GPU assumed (CPU-only safe)
- Whisper tiny or base model for speech-to-text to balance accuracy vs performance
- DeepFace/FER may be slow on CPU — will process keyframes rather than full video
- MoviePy or ffmpeg-python for audio extraction
- Streamlit provides the entire frontend (no separate frontend framework)
- SQLite for local persistence — no database server needed
- Template-based NLP (spaCy) for feedback generation — no LLM APIs

## Constraints

- **Tech Stack**: Streamlit + Python only — strictly enforced
- **AI/ML**: Only open-source local models — Whisper, OpenCV, MediaPipe, DeepFace/FER, spaCy
- **Storage**: Local SQLite only — no external databases
- **Hardware**: CPU-only, must run on typical laptop specs
- **Timeline**: Working MVP within the week
- **No Paid Services**: Zero cloud API costs — fully self-contained

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| CPU-optimized Whisper model (tiny/base) | No GPU assumed, must run on laptop | — Pending |
| Keyframe-based emotion analysis | Full video emotion scan too slow on CPU | — Pending |
| Template-based feedback (no LLM) | Avoids API costs, keeps it local | — Pending |
| Heuristic confidence score | Simple, explainable, no ML needed | — Pending |
| SQLite over file-based storage | Structured queries, easy history tracking | — Pending |

---

*Last updated: 2026-05-16 after initialization*

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state
