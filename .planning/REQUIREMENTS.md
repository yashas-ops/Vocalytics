# Requirements: AI Interview Analyzer

**Defined:** 2026-05-16
**Core Value:** A user can record or upload a mock interview and immediately get actionable, data-driven feedback on their communication and presentation skills — all running locally with no cloud dependencies.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Video Input

- [ ] **VID-01**: User can upload video file (mp4, mov, avi) for analysis
- [ ] **VID-02**: System saves uploaded videos to local `uploads/` directory

### Audio Extraction

- [ ] **AUD-01**: System extracts audio from uploaded video using ffmpeg subprocess
- [ ] **AUD-02**: System saves extracted audio temporarily to `temp/` directory

### Transcription

- [ ] **STT-01**: System transcribes speech to text using faster-whisper (tiny/base model)
- [ ] **STT-02**: Transcript includes timestamped segments

### Speech Analysis

- [ ] **SPE-01**: System detects and counts filler words (um, uh, like, basically, literally, you know)
- [ ] **SPE-02**: System identifies most used filler word
- [ ] **SPE-03**: System calculates speaking speed in words per minute (WPM)
- [ ] **SPE-04**: System classifies WPM as slow (<110), good (110-160), or fast (>160)

### Visual Analysis

- [ ] **VIS-01**: System detects eye contact percentage using MediaPipe Face Mesh with head pose estimation
- [ ] **VIS-02**: System detects dominant emotion from video frames using DeepFace (keyframe-sampled, max 20 frames)
- [ ] **VIS-03**: System generates emotion frequency distribution

### Confidence Scoring

- [ ] **SCORE-01**: System computes confidence score (0-100) using weighted heuristic formula
- [ ] **SCORE-02**: System classifies score as Excellent, Good, or Needs Improvement
- [ ] **SCORE-03**: Heuristic considers eye contact, filler word frequency, and speaking pace

### Feedback Report

- [ ] **FDBK-01**: System generates detailed template-based feedback report
- [ ] **FDBK-02**: Report includes strengths, weaknesses, and specific improvement tips
- [ ] **FDBK-03**: Report generation uses template-based NLP (spaCy), no LLM/API calls

### Dashboard

- [ ] **DASH-01**: Dashboard displays uploaded video preview
- [ ] **DASH-02**: Dashboard displays transcript panel
- [ ] **DASH-03**: Dashboard displays confidence score card with classification
- [ ] **DASH-04**: Dashboard displays speaking speed card with WPM and classification
- [ ] **DASH-05**: Dashboard displays eye contact percentage chart
- [ ] **DASH-06**: Dashboard displays emotion analytics chart
- [ ] **DASH-07**: Dashboard displays filler word breakdown
- [ ] **DASH-08**: Dashboard displays final AI feedback report

### Database & History

- [ ] **DB-01**: System stores interview results in local SQLite database
- [ ] **DB-02**: Stored fields include: interview_id, transcript, confidence_score, filler_count, speaking_speed, eye_contact_score, dominant_emotion, generated_feedback, timestamp
- [ ] **DB-03**: User can view past interview results from history

### UI/UX

- [ ] **UI-01**: Application uses dark theme with modern startup-style design
- [ ] **UI-02**: Dashboard uses cards, progress bars, and charts for data visualization
- [ ] **UI-03**: Charts rendered with Plotly or Streamlit native charts

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Video Input

- **VID-03**: User can record video directly via webcam (streamlit-webrtc)

### Transcription

- **STT-03**: Voice Activity Detection (VAD) preprocessing before Whisper to prevent hallucination on silence
- **STT-04**: Support for longer videos with progress tracking during transcription

### Visual Analysis

- **VIS-04**: Real-time face tracking during webcam recording

### Feedback

- **FDBK-04**: Downloadable PDF reports

### Features

- **GEN-01**: Multi-session comparison (compare progress across multiple interviews)
- **GEN-02**: Export transcript and metrics as JSON/CSV

## Out of Scope

| Feature | Reason |
|---------|--------|
| User authentication | Local single-user app — no login needed |
| Payment systems | Not a commercial product |
| Cloud deployment | Fully local — no cloud dependency |
| Docker / containerization | Overkill for local Streamlit app |
| OpenAI / GPT APIs | User explicitly forbids paid APIs |
| Real-time co-pilot | Post-recording analysis only |
| Resume parser | Not related to interview analysis |
| Job board features | Outside project scope |
| Mobile app | Web-only (Streamlit) |
| Advanced gaze estimation | Practical heuristic sufficient |
| OAuth / SSO | No auth needed |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| VID-01 | Phase 2 | Pending |
| VID-02 | Phase 2 | Pending |
| AUD-01 | Phase 2 | Pending |
| AUD-02 | Phase 2 | Pending |
| STT-01 | Phase 2 | Pending |
| STT-02 | Phase 2 | Pending |
| SPE-01 | Phase 3 | Pending |
| SPE-02 | Phase 3 | Pending |
| SPE-03 | Phase 3 | Pending |
| SPE-04 | Phase 3 | Pending |
| VIS-01 | Phase 4 | Pending |
| VIS-02 | Phase 4 | Pending |
| VIS-03 | Phase 4 | Pending |
| SCORE-01 | Phase 5 | Pending |
| SCORE-02 | Phase 5 | Pending |
| SCORE-03 | Phase 5 | Pending |
| FDBK-01 | Phase 5 | Pending |
| FDBK-02 | Phase 5 | Pending |
| FDBK-03 | Phase 5 | Pending |
| DASH-01 | Phase 5 | Pending |
| DASH-02 | Phase 5 | Pending |
| DASH-03 | Phase 5 | Pending |
| DASH-04 | Phase 5 | Pending |
| DASH-05 | Phase 5 | Pending |
| DASH-06 | Phase 5 | Pending |
| DASH-07 | Phase 5 | Pending |
| DASH-08 | Phase 5 | Pending |
| DB-01 | Phase 5 | Pending |
| DB-02 | Phase 5 | Pending |
| DB-03 | Phase 5 | Pending |
| UI-01 | Phase 1 | Pending |
| UI-02 | Phase 5 | Pending |
| UI-03 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 33 total
- Mapped to phases: 33 ✓
- Unmapped: 0

---

*Requirements defined: 2026-05-16*
*Last updated: 2026-05-16 after initial definition*
