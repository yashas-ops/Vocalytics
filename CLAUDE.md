<!-- GSD:project-start source:PROJECT.md -->
## Project

**AI Interview Analyzer**

A fully local AI-powered web application that analyzes mock interview videos. Users upload or record video interviews, and the system evaluates speech-to-text, speaking speed, filler words, eye contact, facial expressions, and confidence — generating a comprehensive feedback report. Built for interview practice and as a portfolio-ready MVP.

**Core Value:** A user can record or upload a mock interview and immediately get actionable, data-driven feedback on their communication and presentation skills — all running locally with no cloud dependencies.

### Constraints

- **Tech Stack**: Streamlit + Python only — strictly enforced
- **AI/ML**: Only open-source local models — Whisper, OpenCV, MediaPipe, DeepFace/FER, spaCy
- **Storage**: Local SQLite only — no external databases
- **Hardware**: CPU-only, must run on typical laptop specs
- **Timeline**: Working MVP within the week
- **No Paid Services**: Zero cloud API costs — fully self-contained
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->
## Technology Stack

## Recommended Stack
### Core Technologies
| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.10–3.12 | Application runtime | Streamlit requires >=3.10; spaCy 3.8 supports 3.9–3.14; MediaPipe supports 3.9–3.12. Python 3.11 is the sweet spot (faster than 3.10, most libraries have wheels). Avoid 3.13 until MediaPipe 0.10.x explicitly ships wheels for it. |
| Streamlit | 1.57.0 | Full frontend framework | Fastest path to a data dashboard in Python. Built-in file uploader, chart integration, layout components. No separate frontend framework needed. Entire app in one Python file. |
| faster-whisper | 1.2.1 | Speech-to-text transcription | **4x faster than openai/whisper on CPU** using CTranslate2 inference engine. INT8 quantization reduces memory by ~40% with negligible accuracy loss. Uses PyAV for audio decoding (no system ffmpeg required). |
| OpenCV | 4.13.0.92 | Video frame processing, face detection | Industry standard for computer vision. CPU-only wheels ship with every release. Use `opencv-python-headless` variant to avoid unnecessary GUI dependencies. Haar cascades + frame resizing are lightweight on CPU. |
| MediaPipe | 0.10.35 | Face mesh landmark detection | Provides 468 3D face landmarks including eye contours for eye contact detection. Runs efficiently on CPU for single-face tracking. The legacy `mp.solutions.face_mesh` API (deprecated 2023 but still functional) is simpler for this use case than the newer Tasks API. |
| DeepFace | 0.0.100 | Emotion/facial expression analysis | Most actively maintained FER library (latest release May 2026). Supports multiple detection backends — use `opencv` backend on CPU for speed. Provides emotion predictions (angry, disgust, fear, happy, sad, surprise, neutral) plus age/gender/race. |
| spaCy | 3.8.14 | NLP for filler word detection, text analysis | Industrial-strength NLP with fast CPU tokenization. Use `en_core_web_sm` model (~12MB) for POS tagging and token-level analysis. Simpler than NLTK, faster than transformers. No GPU needed. |
| SQLite | 3.53.1 (bundled with Python) | Local persistent storage | Zero-config, serverless, ships with Python's standard library. WAL mode enables concurrent reads during analysis. Perfect for single-user app with structured interview history data. |
| Plotly | 6.7.0 | Interactive charts (emotion timeline, confidence, WPM) | Native Streamlit integration via `st.plotly_chart()`. Interactive zoom, hover, and filtering. Better than matplotlib for dashboard UX. Plotly Express API makes chart creation concise. |
### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| numpy | >=1.22 | Array operations for audio/image processing | Required by OpenCV, DeepFace, and faster-whisper internally. Pin latest compatible version. |
| pandas | >=2.0 | Data manipulation for analysis results | Used to structure analysis data before plotting or storing. Also used by DeepFace internally. |
| ffmpeg-python | 0.2.0 | Audio extraction from video (alternative) | If you need more control than ffmpeg subprocess. Builds an FFmpeg command graph in Python. Use raw subprocess for simple extraction (simpler). |
| streamlit-webrtc | latest | Webcam recording in browser | **Required for "record via webcam" feature.** Provides real-time video capture from browser to Python via WebRTC. Without this, you can't do live recording in Streamlit. |
| pydub | 0.25.1 | Audio format conversion/splitting | Optional — if you need to segment audio before feeding to Whisper. Simpler API than raw ffmpeg for audio slicing. |
| dataclasses (stdlib) | — | Structured analysis results | Python stdlib. No install needed. Use for type-safe result objects (transcript, emotion scores, etc.). |
### Development Tools
| Tool | Purpose | Notes |
|------|---------|-------|
| pip | Package management | Use `requirements.txt` with pinned versions for reproducibility. Avoid `pip freeze` dumping. |
| venv | Virtual environment isolation | Mandatory — DeepFace and faster-whisper have heavy dependency chains. Isolate per project. |
| ruff | Linting + formatting | Fast Python linter written in Rust. Catches common mistakes without slowing down. |
| pytest | Testing | Lightweight test framework. Use for unit-testing individual analysis components. |
## Installation
# Core stack
# Supporting
# Webcam recording support
# Download spaCy English model
# Database (stdlib — no install needed)
# SQLite ships with Python
## Alternatives Considered
| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| faster-whisper (CTranslate2) | openai/whisper (original) | If you need the absolute latest Whisper model the day it releases before CTranslate2 conversion exists. Trade: 4x slower on CPU. |
| DeepFace (OpenCV backend) | FER library | If you want a simpler API and don't need age/gender/race analysis. FER has been stable but less actively developed (last release Oct 2025 vs DeepFace May 2026). |
| DeepFace (OpenCV backend) | MediaPipe Face Detection + custom emotion model | If you need real-time (>15 FPS) emotion detection. DeepFace is heavy even on CPU; MediaPipe face detection + a lightweight ONNX emotion model would be faster but more complex to build. |
| ffmpeg subprocess (via subprocess.run) | moviepy | If you need more than just audio extraction (video compositing, effects). MoviePy 2.x has breaking changes from 1.x and loads frames into numpy arrays (memory-heavy). For audio-only extraction, raw ffmpeg is simpler and uses less memory. |
| spaCy (en_core_web_sm) | regex + Counter from stdlib | If you only need filler word counting and WPM calculation. Simple string matching (`re.findall(r'\b(um|uh|like)\b', text)` + `len(words)/duration`) requires no ML. spaCy is overkill for this but gives you flexibility for future NLP features. |
| Plotly | Altair (built into Streamlit via `st.line_chart`) | For dead-simple charts where interactivity isn't critical. Altair is Streamlit's native chart backend, but Plotly offers richer interactivity (zoom, hover details, subplots). |
| SQLite (stdlib) | TinyDB / JSON file storage | If your data model is purely document-based with no relations. Trade: loss of SQL queries, indexing, and structured history browsing. |
## What NOT to Use
| Avoid | Why | Use Instead |
|-------|-----|-------------|
| openai/whisper (vanilla) | 4x slower than faster-whisper on CPU with same accuracy. Uses more memory. Requires system ffmpeg install. | faster-whisper 1.2.1 |
| Full DeepFace with RetinaFace/MTCNN backend | RetinaFace is accurate but ~10x slower than OpenCV backend on CPU. Will tank performance on keyframe analysis. | DeepFace with `detector_backend='opencv'` |
| moviepy for audio extraction | MoviePy loads entire video into numpy arrays. For a 10-min 1080p video, that's ~1.2GB of RAM just for frame data when you only need the audio track. | Raw ffmpeg subprocess or ffmpeg-python |
| FER library (emotion detection) | Last release Oct 2025. Depends on TensorFlow (heavy). Less accurate than DeepFace on FER2013 benchmark. | DeepFace (actively maintained, MIT license, multiple backends) |
| Cloud APIs (OpenAI Whisper API, Google Cloud Speech, AWS Transcribe) | Violates the "fully local" constraint. Requires internet, costs money, sends video data to third parties. | faster-whisper (runs locally) |
| Large language models (LLaMA, GPT4All) for feedback generation | Massive CPU overhead (10+ GB RAM, slow inference). No benefit for template-based feedback. | Template-based feedback (string formatting) or spaCy rule-based matching |
| Docker / containerization | Unnecessary for a single-user desktop app. Adds complexity. Included in project Out of Scope. | Direct Python virtual environment |
## CPU Optimization Patterns
### faster-whisper on CPU
# CRITICAL: INT8 quantization + CPU device
# Use VAD filter to skip silence, reducing processing time by 30-50%
- `tiny` (39M params): ~1x real-time on typical laptop
- `base` (74M params): ~0.5x real-time (recommended balance)
- `small` (244M params): ~0.25x real-time (use for challenging audio only)
### DeepFace emotion detection on CPU
# CRITICAL: Use OpenCV detector backend (fastest on CPU)
# Avoid RetinaFace (accurate but 10x slower on CPU)
- Sample 1 frame per 30 seconds of video (not every frame)
- Downscale frames to 640x480 before passing to DeepFace
- Process frames in a background thread (not blocking the UI thread)
- Cache face detection results: if MediaPipe already found a face region, crop to that ROI before DeepFace
### MediaPipe Face Mesh on CPU
# CRITICAL: Configure for CPU performance
- Use iris landmarks (468 + 10 = 478 landmarks with `refine_landmarks=True`)
- Compute eye gaze direction from iris position relative to eye corners
- Classify as "looking at camera" if gaze vector points toward camera within a threshold
### Audio extraction with ffmpeg (lightweight)
## Version Compatibility
| Package | Compatible With | Notes |
|---------|----------------|-------|
| streamlit 1.57.0 | Python >=3.10 | Requires Python 3.10+. Streamlit 1.57 drops Python 3.9 support. |
| faster-whisper 1.2.1 | Python >=3.9, <3.12 | No 3.12 wheel yet. Must use Python 3.9–3.11. **Critical: don't install with Python 3.12+** |
| mediapipe 0.10.35 | Python 3.9–3.12 | Ships pre-built wheels for win_amd64, manylinux, macOS arm64 + x86_64. |
| deepface 0.0.100 | Python >=3.7 | Broad compatibility. Heavy TF dependency tree (~800MB). |
| spacy 3.8.14 | Python >=3.9, <3.15 | `en_core_web_sm` model is model version 3.8.0, compatible with spaCy 3.8.x. |
| opencv-python-headless 4.13.0.92 | Python >=3.6 | Ships pre-built wheels for all platforms. |
| plotly 6.7.0 | Python >=3.8 | Streamlit 1.57 ships with native Plotly chart support. |
| numpy | All listed packages | Pin to >=1.22 (avoid deprecated percentile alias that Plotly 6.7 warns about). |
| **Python 3.11** | All of the above | **Recommended Python version.** faster-whisper works (3.9–3.11), spaCy works (3.9–3.14), MediaPipe works (3.9–3.12), Streamlit works (3.10+). Python 3.11 is the intersection with best performance. |
### Python Version Decision Tree
## Critical Gotchas
### 1. faster-whisper Python version limit
### 2. DeepFace first-run model download
### 3. MediaPipe legacy API
### 4. Streamlit file upload size limit
### 5. Windows-specific: ffmpeg on PATH
### 6. Memory management with multiple ML models
- **Unload models after use:** Delete references and call `gc.collect()` between pipeline stages
- **Process sequentially:** Transcribe first → save text → unload Whisper → load DeepFace for frames
- **Frame-by-frame processing:** Don't load all frames into memory. Process one keyframe at a time.
## Stack Patterns by Variant
- Upgrade Whisper model from `base` to `small`
- Set `beam_size=5` for better accuracy (slower)
- Trade: 4x slower transcription for ~15% WER improvement
- Use Whisper `tiny` model (39M params, ~1GB RAM)
- Use `opencv` detector for DeepFace (fastest/lightest)
- Process frames at 1/minute instead of 1/30s
- Consider skipping DeepFace entirely — use MediaPipe landmarks alone for basic affect detection
- Use Whisper `tiny.en` (English-only, faster than multilingual tiny)
- Set `beam_size=1` and `vad_filter=True`
- Extract 5 keyframes only (beginning, 25%, 50%, 75%, end)
- Use OpenCV face detection instead of DeepFace for emotion (less accurate but instant)
- Switch from `tiny.en`/`base.en` to multilingual `tiny`/`base`
- spaCy supports 70+ languages for filler word detection
- DeepFace emotion detection is language-independent (facial expressions are universal)
## Non-Stack Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Model storage | Download on first run, cache in `~/.cache/` | Most models auto-download. Clear cache to force re-download. |
| Analysis pipeline | Sequential pipeline: extract audio → transcribe → extract frames → analyze face → aggregate results | Each step feeds the next. Parallel processing adds complexity with minimal benefit for single-user app. |
| Error handling | Graceful degradation | If DeepFace fails (no face), still show transcript + speed results. Never crash on missing data. |
| Streamlit caching | Use `@st.cache_data` for analysis results | Re-running the same video shouldn't repeat analysis. Cache with TTL. |
| Data persistence | SQLite with WAL mode | `PRAGMA journal_mode=WAL` enables concurrent reads during analysis writes. |
## Sources
- PyPI release pages for all listed packages — version numbers verified against latest stable releases
- [faster-whisper GitHub/docs](https://github.com/SYSTRAN/faster-whisper) — CPU benchmarks with INT8 quantization confirmed
- [DeepFace GitHub](https://github.com/serengil/deepface) — detector backend performance characteristics
- [MediaPipe Face Mesh docs](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker) — legacy solution status
- [OpenAI Whisper model comparison](https://github.com/openai/whisper) — model sizes and CPU vs GPU performance
- [Streamlit file uploader docs](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader) — upload size limits
- [spaCy 3.8 release notes](https://github.com/explosion/spaCy) — Python version compatibility
- [context7](https://context7.com) — version verification for major packages
- CPU benchmarks across Whisper implementations — MEDIUM confidence, from multiple community benchmarks agreeing on ~4x speedup
- Package versions: HIGH (verified on PyPI)
- CPU performance claims: HIGH (faster-whisper benchmarks published, community-validated)
- DeepFace vs FER comparison: MEDIUM (based on release cadence + feature comparison, not head-to-head benchmark)
- Python version compatibility: HIGH (verified from each package's PyPI classifiers and setup.py metadata)
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
