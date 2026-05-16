# Project Research Summary

**Project:** ctracker — AI Interview Analyzer
**Domain:** Local CPU-only Video Interview Analysis & Communication Coaching
**Researched:** 2026-05-16
**Confidence:** HIGH

## Executive Summary

**ctracker is a privacy-first, fully-local interview practice tool** that analyzes uploaded or webcam-recorded videos for speech patterns (filler words, speaking speed), non-verbal cues (eye contact, facial expressions), and generates actionable feedback reports — all without cloud APIs, accounts, or GPU requirements. The research across stack, features, architecture, and pitfalls converges on a clear recommendation: a **sequential pipeline architecture** on Python 3.11 using Streamlit (UI), faster-whisper (transcription), MediaPipe (face/eye tracking), DeepFace (emotion analysis), and spaCy (NLP), with SQLite for persistence. The key competitive insight is that **no major competitor combines emotion analysis + eye contact + fully local processing** in a single free tool — this is a genuine market gap.

**The recommended approach is to build in dependency order:** infrastructure first (models, DB, file management), then the audio pipeline (upload → transcribe), then text analytics (filler words, WPM), then visual analysis (eye contact, emotion on keyframes only), then scoring and feedback, and finally the polished dashboard. **The biggest technical risks are: (1)** Whisper hallucinating on silence (mitigated by mandatory VAD preprocessing from day one), **(2)** DeepFace consuming hours of CPU time per video (mitigated by aggressive keyframe sampling — max 20 frames), and **(3)** Streamlit's rerun model causing full pipeline re-execution (mitigated by `@st.cache_resource` for models and `@st.cache_data` for results, designed from Phase 1, not retrofitted). The most common failure pattern in this domain is building the pipeline without memory management and progress feedback, then discovering the app is unusable on a typical 8GB laptop.

## Key Findings

### Recommended Stack

The stack is well-defined and opinionated. **Python 3.11 is non-negotiable** — faster-whisper requires 3.9–3.11, Streamlit requires ≥3.10, and 3.11 is the intersection with best performance. Use `faster-whisper` (not `openai/whisper`) with INT8 quantization for 4x CPU speedup. Use Streamlit's `st.Page`/`st.navigation` for multi-page structure, not the legacy `pages/` auto-discovery.

**Core technologies:**
- **Python 3.11**: The only version supported by all key libraries (faster-whisper, Streamlit, MediaPipe, spaCy)
- **Streamlit 1.57.0**: Full frontend framework — file upload, charts, layout, navigation in a single Python file
- **faster-whisper 1.2.1**: Speech-to-text — 4x faster than openai/whisper on CPU via CTranslate2 + INT8 quantization
- **OpenCV 4.13.0 (headless)**: Video frame extraction, face detection pre-filter (Haar cascades)
- **MediaPipe 0.10.35**: 468-point face landmark detection for eye contact (via head pose PnP), runs efficiently on CPU
- **DeepFace 0.0.100**: Emotion/facial expression analysis — use `opencv` detector backend, not RetinaFace (10x slower)
- **spaCy 3.8.14 + en_core_web_sm**: POS-tagging-based filler word detection (not naive substring matching)
- **SQLite**: Zero-config persistence with WAL mode for concurrent reads during analysis
- **Plotly 6.7.0**: Interactive emotion timelines and WPM charts via native Streamlit integration

### Expected Features

**Feature landscape** is well-mapped from competitor analysis (Yoodli, Huru, Genius Interview, MirrorAI). The competitive differentiator is clear: every major competitor uploads to the cloud; ctracker is fully local. Emotion analysis is genuinely unique in this space.

**Must have (table stakes) for v1:**
- Video upload (mp4/mov/avi) + webcam recording via `st.camera_input` — entry point
- Speech-to-text (faster-whisper tiny/base) — foundation of all text analysis
- Filler word detection (#1 most actionable metric per user reviews) — spaCy POS-tagging, not regex
- WPM / speaking speed analysis — simple word count ÷ duration
- Eye contact detection (MediaPipe with head pose estimation) — key differentiator
- Emotion analysis (DeepFace on keyframes, max 20 frames) — unique differentiator vs competitors
- Transparent confidence score with component breakdown — build trust via formula visibility
- Template-based feedback report (strengths, weaknesses, tips) — no LLM dependency
- Session dashboard + SQLite history — "view past sessions" is table stakes

**Should have (competitive — v1.x):**
- Trend charts (filler words and WPM over time) — Yoodli's highest-rated feature
- PDF export of reports — shareable artifact
- Custom filler word lists — industry-specific words
- Transcript search / keyword highlight
- Video scrubber with metric sync ("show me where I lost eye contact")

**Defer (v2+):**
- Posture analysis (MediaPipe Pose), speaker diarization, accent analysis, question generation, topic modeling

### Architecture Approach

The architecture is a **sequential pipeline with cached stages**, cleanly separated into three layers: **Presentation** (Streamlit pages in `app_pages/`), **Pipeline** (pure-function modules in `modules/` that never import Streamlit), and **Persistence** (SQLite via Repository pattern in `db/`). Modules communicate through **Pydantic models** defined in a single `models.py` — every stage declares its input and output types explicitly, making each stage independently testable and the pipeline debuggable without spinning up the full app.

**Major components:**
1. **Audio Extractor** — ffmpeg subprocess (not moviepy `np.array`) to extract 16kHz mono WAV
2. **Transcriber** — faster-whisper (tiny/base, int8, VAD filter ON) producing word-timestamped segments
3. **Speech Analyzer** — spaCy POS-tagging for filler words + pure-Python WPM calculation
4. **Frame Extractor** — OpenCV VideoCapture sampling at configurable intervals (1-2 fps)
5. **Face Analyzer** — MediaPipe Face Mesh for eye contact (PnP head pose) + DeepFace keyframe emotion
6. **Confidence Scorer** — Weighted heuristic with per-component breakdown (eye contact 30%, speed 20%, fillers 20%, emotion 15%, clarity 15%)
7. **Feedback Generator** — Template-based (f-strings + conditional logic + spaCy NLP patterns)
8. **History Manager** — SQLite Repository for CRUD operations on interview records

### Critical Pitfalls

13 documented pitfalls across 4 phases. The 5 most critical require preemptive action in Phase 0-1:

1. **Whisper hallucination on silence** — Without VAD preprocessing, silent gaps in interviews produce hallucinated text ("Thank you for watching" × 50+), destroying WPM and filler metrics. **Fix:** Always pre-process audio with VAD (webrtcvad/silero-vad), check `no_speech_prob` per segment, use `temperature=0`. Phase 1.

2. **Frame-by-frame DeepFace destroys CPU** — Naively running DeepFace on every frame of a 10-min video (18,000 frames at 30fps) = 5-25 hours of CPU time. **Fix:** Mandatory keyframe sampling — max 1 frame per 15-30 seconds (10-20 frames total for a 5-min video). Use OpenCV Haar cascade as pre-filter. Phase 2.

3. **Streamlit OOM from large files** — `st.file_uploader` keeps entire video in memory. A 500MB upload balloons to 3-4GB working set on an 8GB laptop → OOM crash. **Fix:** Save uploaded file to disk immediately via `tempfile.NamedTemporaryFile`, never keep in `st.session_state`. Phase 1.

4. **Eye contact = face detected (wrong metric)** — MediaPipe detects the face even when looking 30° away, so 100% "eye contact" is actually 100% "face detected." **Fix:** Implement Perspective-n-Point (PnP) head pose estimation with MediaPipe landmarks + OpenCV `solvePnP`. Define eye contact as yaw ±15°, pitch ±10° + iris centering. Phase 2.

5. **Full pipeline reruns on every UI interaction** — Streamlit's execution model re-runs the entire script on any widget change. Without caching, clicking a checkbox triggers re-transcription and re-analysis (10+ minute wait). **Fix:** Use `@st.cache_resource` for ML models (loaded once), `@st.cache_data` for analysis results (cache per video hash), session state for progress tracking. Design caching architecture in Phase 1, not retrofitted in Phase 4.

## Implications for Roadmap

Based on dependency analysis from all four research files, the project should be built in **5 ordered phases**:

### Phase 1: Core Infrastructure & Data Models
**Rationale:** Foundation for everything. Models, DB schema, and file management have zero dependencies. Pydantic contracts must exist before any pipeline code.
**Delivers:** Project skeleton, shared data types, DB connection, file utilities, requirements.txt, Streamlit entrypoint with page routing.
**Addresses:** Infrastructure setup (all pipeline stages will import `modules/models.py`)
**Uses:** Python 3.11, Pydantic, SQLite, `streamlit_app.py` with `st.Page`/`st.navigation`
**Avoids:** Pitfall 2 (wrong Whisper backend — pin `faster-whisper` in requirements.txt), Pitfall 11 (wrong MediaPipe API — pin `mediapipe==0.10.35`, decide legacy vs tasks API), Pitfall 9 (temp file strategy — design `data/` directory + cleanup from day one)
**Research flag:** Standard patterns — skip research-phase

### Phase 2: Video Upload, Audio Pipeline & Transcription
**Rationale:** The critical bottleneck (Whisper on CPU) must be validated early. Audio processing is the prerequisite for all text analysis. VAD must be built in from the start — retrofitting it means re-transcribing everything.
**Delivers:** Video upload page, webcam recording, ffmpeg audio extraction (16kHz WAV monochannel), VAD preprocessing, faster-whisper transcription with progress feedback.
**Uses:** faster-whisper 1.2.1 (int8, tiny/base), ffmpeg subprocess, OpenCV (`opencv-python-headless`), `st.file_uploader` with disk-based storage
**Architecture:** `modules/audio_extractor.py`, `modules/transcriber.py`, `app_pages/upload.py`
**Avoids:** Pitfall 1 (Whisper hallucination — VAD filter ON, `no_speech_prob` check), Pitfall 4 (Streamlit OOM — write to disk immediately), Pitfall 9 (temp file leaks — `try/finally` cleanup)
**Research flag:** Needs deeper research on VAD library selection (webrtcvad vs silero-vad vs pyannote-audio) and optimal Whisper parameters (model size, beam size, threshold tuning). Use `/gsd-research-phase` during planning.

### Phase 3: Speech & Text Analysis
**Rationale:** These are fast, no-model dependencies (once spaCy is downloaded). They depend on the transcript from Phase 2. Building them early gives immediate visible results and validates the pipeline end-to-end with text-only features.
**Delivers:** Filler word detection (spaCy POS-tagging — not naive substring matching), WPM calculation, speed classification (slow/good/fast), basic transcript display with timestamps.
**Uses:** spaCy 3.8.14 + `en_core_web_sm` (enable only `tagger` and `tokenizer` pipelines — saves 40-60% inference time)
**Architecture:** `modules/speech_analyzer.py`, `modules/models.py` (SpeechMetrics)
**Avoids:** Pitfall 12 (naive filler word detection — use spaCy `Matcher`/`PhraseMatcher` with POS tagging; "like" as verb ≠ filler; `\bum\b` not substring match)
**Research flag:** Standard patterns — well-documented spaCy NLP, skip research-phase

### Phase 4: Visual Analysis — Eye Contact & Emotion
**Rationale:** Independent of text pipeline (processes same video, but in parallel conceptually). Requires careful frame sampling strategy to avoid CPU meltdown. Highest-value differentiator (no competitor does local emotion + eye contact).
**Delivers:** Keyframe extraction (OpenCV), eye contact detection (MediaPipe Face Mesh + PnP head pose), emotion analysis (DeepFace on max 20 keyframes), per-frame results, aggregate summaries.
**Uses:** OpenCV VideoCapture, MediaPipe 0.10.35 (legacy `mp.solutions.face_mesh`), DeepFace 0.0.100 (opencv backend, `enforce_detection=False`, `actions=['emotion']`)
**Architecture:** `modules/frame_extractor.py`, `modules/face_analyzer.py`, `modules/models.py` (FrameAnalysis, FaceResults)
**Avoids:** Pitfall 3 (frame-by-frame DeepFace — max 20 frames total), Pitfall 6 (wrong eye contact — PnP head pose, not EAR/face-detected boolean), Pitfall 8 (emotion misses transitions — soft voting across frames, confidence threshold >50%)
**Research flag:** Needs deeper research on MediaPipe PnP head pose implementation (3D face model landmarks, `solvePnP` parameters) and optimal keyframe sampling strategy. Use `/gsd-research-phase` during planning.

### Phase 5: Scoring, Feedback & Dashboard
**Rationale:** Depends on ALL metrics from Phases 2-4. The confidence score is a reduction of all prior outputs. The feedback report reads everything. The dashboard displays it all. SQLite persistence happens after analysis is complete.
**Delivers:** Confidence score with transparent component breakdown, template-based feedback report (strengths/weaknesses/tips), Streamlit dashboard (metrics, charts, transcript, feedback), SQLite session persistence, history browser page.
**Uses:** Plotly 6.7.0 (emotion timeline, WPM charts), Streamlit (`st.metric`, `st.line_chart`, `st.markdown`, `st.expander`), SQLite (WAL mode)
**Architecture:** `modules/confidence_scorer.py`, `modules/feedback_generator.py`, `db/schema.py`, `db/connection.py`, `db/repository.py`, `app_pages/dashboard.py`, `app_pages/history.py`
**Avoids:** Pitfall 5 (full pipeline rerun — `@st.cache_resource` for models, `@st.cache_data` for results, `st.session_state` for pipeline state), Pitfall 7 (opaque scoring — component-visible breakdown: "Eye Contact: 16/25, Fillers: 8/25..."), Pitfall 13 (no progress feedback — `st.progress()` + `st.status()` with stage names and estimated time)
**Research flag:** Standard patterns for Streamlit caching and dashboard design — skip research-phase. But heuristic weight calibration needs real data; plan for a calibration pass after Phase 5 MVP is working.

### Phase Ordering Rationale

- **Dependency-driven:** Phase 1 (infrastructure) → Phases 2-4 (pipeline stages in order of dependency depth) → Phase 5 (aggregation + display). Each phase produces outputs consumed by subsequent phases.
- **Risk mitigation:** Phase 2 (Whisper) is the biggest CPU unknown — validate early. Phase 4 (DeepFace) is the biggest performance trap — frame sampling strategy must be designed, not optimized later.
- **Parallelism possibility:** Phase 3 (speech analysis) has no dependency on Phase 4 (visual analysis). They can be built in parallel once Phase 2 (transcription) and Phase 1 (infrastructure) are complete. However, for single-developer velocity, sequential execution is recommended.
- **Pitfall avoidance:** The most expensive pitfalls (no VAD → hallucinated transcripts, frame-by-frame DeepFace → hours of processing, no caching → full pipeline reruns) are prevented by architectural decisions made in Phases 1-2, not retrofitted later.

### Research Flags

Phases needing deeper research during planning:
- **Phase 2:** VAD library selection (webrtcvad vs silero-vad vs pyannote-audio); Whisper model size benchmarks on target hardware; optimal `no_speech_prob` threshold tuning
- **Phase 4:** MediaPipe FaceMesh PnP implementation details (correct 3D face model coordinates for `solvePnP`); DeepFace keyframe sampling strategy validation; determining whether to use legacy or tasks MediaPipe API

Phases with standard patterns (skip research-phase):
- **Phase 1:** Python project structure, Pydantic models, SQLite schema, Streamlit page routing — all well-documented patterns
- **Phase 3:** spaCy POS-tagging for filler words, regex with word boundaries — standard NLP patterns
- **Phase 5:** Streamlit dashboard components, caching with `@st.cache_resource`/`@st.cache_data`, Plotly charting — well-documented

### Post-MVP Enhancement Path (v1.x)

After the 5-phase MVP is stable, the following v1.x features are natural extensions (each is a bounded enhancement):
1. **Trend charts** (once ≥3 sessions exist) — add to history page
2. **PDF export** — `reportlab` or `pdfkit` integration on the feedback report
3. **Custom filler word list** — settings UI + config parameter
4. **Transcript search** — simple text search on existing transcript data
5. **Video scrubber with metric sync** — high UX value but requires timestamp mapping; research-phase recommended
6. **Side-by-side comparison** — dual-session render; straightforward once history exists

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versions verified against PyPI; compatibility matrix cross-checked for Python 3.11; performance claims from published benchmarks (faster-whisper 4x, DeepFace keyframe strategy) |
| Features | HIGH | Competitor analysis from 10+ sources (Yoodli, Huru, Genius Interview, MirrorAI, Final Round AI); table stakes consistent across all sources; differentiation validated by market gap (no local tool combines emotion + eye contact) |
| Architecture | HIGH | Sequential pipeline with Pydantic contracts is established pattern for multi-stage video analysis; Streamlit multipage + caching patterns from official docs; MediaPipe + OpenCV integration documented in multiple reference projects |
| Pitfalls | HIGH | All 13 pitfalls confirmed across multiple independent sources — official docs (Whisper, MediaPipe, Streamlit), GitHub issues, community benchmarks, academic papers; recovery strategies costed out |

**Overall confidence:** HIGH

### Gaps to Address

- **Whisper model size on target hardware:** The research recommends `tiny` or `base` models, but the actual performance on a representative 4-core/8GB laptop needs real measurement during Phase 2 implementation. Plan for a benchmarking step.
- **Heuristic weight calibration:** The confidence score weights (eye contact 30%, speed 20%, fillers 20%, emotion 15%, clarity 15%) are educated guesses from competitor research. Plan a calibration pass after Phase 5 using 5-10 mock interviews to tune weights against human judgment.
- **DeepFace model caching:** First-use model download (~200MB) must be redirected to a local project directory via `DEEPFACE_HOME`. This environment variable setup needs to be documented in setup instructions during Phase 4.
- **Streamlit 1.57 behavior with st.camera_input:** Webcam recording via Streamlit needs to be tested on the target Windows environment. The research assumes `st.camera_input` returns a file-like object compatible with the pipeline, but this needs validation during Phase 2.

## Sources

### Primary (HIGH confidence)
- PyPI release pages for Streamlit, faster-whisper, opencv-python-headless, mediapipe, deepface, spacy, plotly — version verification and compatibility
- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper) — CPU benchmarks, INT8 quantization, model sizes
- [MediaPipe Face Mesh official docs](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker) — API versions, landmark indices, legacy solution status
- [Streamlit Multipage Apps docs](https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation) — `st.Page` and `st.navigation` API
- [Streamlit caching docs](https://docs.streamlit.io/develop/concepts/architecture/caching) — `@st.cache_resource` vs `@st.cache_data` patterns
- [DeepFace GitHub](https://github.com/serengil/deepface) — detector backend performance, API reference
- [OpenCV solvePnP tutorial](https://docs.opencv.org/4.x/d5/d1f/calib3d_solvePnP.html) — head pose estimation for eye contact

### Secondary (MEDIUM confidence)
- Whisper hallucination reports — OpenAI Whisper GitHub community issues, whisper.cpp issue #1724, ArXiv 2505.12969
- DeepFace CPU performance — GitHub issues #937, Stack Overflow reports (~3.6s per detection on CPU)
- Streamlit memory issues — GitHub issues #9218, #9460; Discuss thread #75511
- Yoodli, Huru, Genius Interview, MirrorAI feature analysis — product pages, techraisal.com, aidemos.com, interviewsidekick.com comparison articles
- [PRVIA: Pre-Recorded Video Interview Analysis](https://github.com/Mohamed-samy2/Video-Interview-Analysis) — reference architecture
- [Video-Understanding-Local (Streamlit + Whisper pipeline)](https://github.com/circuminds/End-To-End-Video-Understanding) — reference architecture

### Tertiary (LOW confidence)
- MediaPipe Face Mesh performance on specific CPU configurations — GitHub issue #2784 (community reports vary)
- Heuristic confidence weight effectiveness — no published benchmark; needs empirical calibration
- Sander de Snaijer's MediaPipe landmark reference — single-source, no official equivalent for 478-point model

---

*Research completed: 2026-05-16*
*Ready for roadmap: yes*
