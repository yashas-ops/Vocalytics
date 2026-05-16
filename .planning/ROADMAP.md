# Roadmap: AI Interview Analyzer

## Overview

A fully local AI-powered Streamlit app that analyzes mock interview videos. The user uploads a video, and the system processes it through a sequential pipeline: audio extraction → faster-whisper transcription → filler word & WPM analysis → MediaPipe eye contact detection → DeepFace emotion analysis → confidence scoring → feedback report generation — all displayed on a polished dashboard with history. Built in 5 dependency-driven phases, each delivering a coherent, verifiable capability.

## Phases

- [ ] **Phase 1: Core Infrastructure & Data Models** - Project skeleton, shared types, SQLite schema, file management, Streamlit shell with dark theme, and cached model loading
- [ ] **Phase 2: Video Upload, Audio Pipeline & Transcription** - Video upload, ffmpeg audio extraction, VAD preprocessing, faster-whisper transcription with timestamped segments
- [x] **Phase 3: Speech & Text Analysis** - Filler word detection (spaCy POS-tagging), WPM calculation, speed classification (completed 2026-05-16)
- [x] **Phase 4: Visual Analysis — Eye Contact & Emotion** - Keyframe extraction, MediaPipe eye contact with head pose estimation, DeepFace emotion analysis (completed 2026-05-16)
- [ ] **Phase 5: Scoring, Feedback & Dashboard** - Confidence score, template-based feedback report, full dashboard with charts, SQLite persistence, history browser

## Phase Details

### Phase 1: Core Infrastructure & Data Models
**Goal**: Foundation for the entire app — shared data contracts, database schema, file management, Streamlit entrypoint with dark theme, and model caching infrastructure
**Depends on**: Nothing (first phase)
**Requirements**: UI-01
**Success Criteria** (what must be TRUE):
  1. User can launch the app with `streamlit run app.py` and see a dark-themed interface with working page navigation (Upload, Dashboard, History)
  2. Shared Pydantic data models (`modules/models.py`) define every pipeline stage's input/output types and are importable without circular dependencies
  3. SQLite database initializes with the correct schema on first run (WAL mode enabled)
  4. File management utilities save uploaded videos to `uploads/` immediately (never kept in memory) and clean up `temp/` after pipeline completes
  5. ML model loading uses `@st.cache_resource` so faster-whisper, spaCy, MediaPipe, and DeepFace each load exactly once per session
**Plans**: 2 plans
**UI hint**: yes

Plans:
- [ ] 01-01-PLAN.md — Project skeleton, Pydantic data models, SQLite database init
- [ ] 01-02-PLAN.md — Utilities, Streamlit app shell, dark theme CSS

### Phase 2: Video Upload, Audio Pipeline & Transcription
**Goal**: Users can upload videos and get timestamped transcripts — the critical audio-to-text pipeline validated early
**Depends on**: Phase 1
**Requirements**: VID-01, VID-02, AUD-01, AUD-02, STT-01, STT-02
**Success Criteria** (what must be TRUE):
  1. User can upload mp4/mov/avi video via the Upload page and see it saved to `uploads/` with a confirmation message
  2. System extracts 16kHz mono WAV audio from uploaded video using ffmpeg subprocess (not moviepy arrays) and saves to `temp/`
  3. System transcribes speech to text using faster-whisper (tiny or base model, INT8 quantization) producing word-timestamped segments
  4. System shows progress feedback during the pipeline (status messages: "Extracting audio...", "Transcribing...", estimated time) using `st.progress()`/`st.status()`
**Plans**: 2 plans
**UI hint**: yes

Plans:
- [ ] 02-01-PLAN.md — Audio extraction + faster-whisper transcription engine modules
- [ ] 02-02-PLAN.md — Upload page pipeline integration with progress feedback

### Phase 3: Speech & Text Analysis
**Goal**: System analyzes the transcript for filler word frequency and speaking speed metrics
**Depends on**: Phase 2
**Requirements**: SPE-01, SPE-02, SPE-03, SPE-04
**Success Criteria** (what must be TRUE):
  1. System detects and counts filler words (um, uh, like, basically, literally, you know) using spaCy POS-tagging (not naive substring matching — "like" as verb ≠ filler)
  2. System identifies the most used filler word in the transcript
  3. System calculates speaking speed in words per minute (WPM) and classifies as slow (&lt;110), good (110-160), or fast (&gt;160)
  4. Speech analysis results are stored in typed Pydantic models ready for dashboard display
**Plans**: 2 plans

Plans:
- [x] 03-01-PLAN.md — Speech analysis engine: filler word detection + WPM calculation (TDD)
- [x] 03-02-PLAN.md — Integrate speech analysis into Upload pipeline + Dashboard display

### Phase 4: Visual Analysis — Eye Contact & Emotion
**Goal**: System analyzes video frames for eye contact percentage and emotional expressions — the unique differentiator
**Depends on**: Phase 2 (needs uploaded video, runs independently of transcript)
**Requirements**: VIS-01, VIS-02, VIS-03
**Success Criteria** (what must be TRUE):
   1. System extracts keyframes from video at configurable intervals using OpenCV (max 20 frames for DeepFace to avoid CPU meltdown)
   2. System detects eye contact percentage using MediaPipe Face Mesh with PnP head pose estimation (yaw ±15°, pitch ±10°) — not mere face detection
   3. System detects dominant emotion per keyframe using DeepFace (opencv backend, `enforce_detection=False`) and generates emotion frequency distribution (e.g., "neutral 45%, happy 30%, ...")
   4. Visual analysis completes on CPU in reasonable time (bounded by max 20 DeepFace frames) and results are stored in typed models
**Plans**: 2 plans

Plans:
- [x] 04-01-PLAN.md — Visual analysis engine: keyframe extraction, eye contact (MediaPipe PnP), emotion detection (DeepFace) — TDD
- [x] 04-02-PLAN.md — Integrate visual analysis into Upload pipeline + Dashboard display

### Phase 5: Scoring, Feedback & Dashboard
**Goal**: Complete analysis pipeline — confidence score, feedback report, full dashboard with visualizations, and persistent history
**Depends on**: Phase 3, Phase 4
**Requirements**: SCORE-01, SCORE-02, SCORE-03, FDBK-01, FDBK-02, FDBK-03, DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06, DASH-07, DASH-08, DB-01, DB-02, DB-03, UI-02, UI-03
**Success Criteria** (what must be TRUE):
  1. System computes a confidence score (0-100) using weighted heuristic with per-component breakdown visible to user (eye contact, filler words, speaking pace, emotion, clarity)
  2. System classifies score as Excellent (≥80), Good (60-79), or Needs Improvement (&lt;60)
  3. System generates template-based feedback report listing strengths, weaknesses, and specific improvement tips — no LLM/API calls
  4. Dashboard displays all results: video preview, transcript panel, confidence score card, speaking speed card, eye contact percentage chart, emotion analytics chart, filler word breakdown, and feedback report
  5. All analysis results persist to SQLite; user can view past interview history from the History page, including any previous session's full report
**Plans**: 3 plans
**UI hint**: yes

Plans:
- [x] 05-01-PLAN.md — Scoring engine + feedback templates (TDD: compute_confidence, generate_feedback)
- [x] 05-02-PLAN.md — Pipeline Step 6 integration + SQLite persistence + DB fetch functions
- [ ] 05-03-PLAN.md — Dashboard finalization (Plotly charts, video, feedback) + History page

## Progress

**Execution Order:** 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Infrastructure | 2/2 | Complete | 2026-05-16 |
| 2. Upload, Audio & Transcription | 2/2 | Complete | 2026-05-16 |
| 3. Speech & Text Analysis | 2/2 | Complete   | 2026-05-16 |
| 4. Visual Analysis | 2/2 | Complete   | 2026-05-16 |
| 5. Scoring, Feedback & Dashboard | 0/3 | Not started | - |
