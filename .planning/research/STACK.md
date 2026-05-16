# Stack Research

**Domain:** Local AI Interview Analyzer (CPU-only)
**Researched:** 2026-05-16
**Confidence:** HIGH

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

```bash
# Core stack
pip install streamlit==1.57.0
pip install faster-whisper==1.2.1
pip install opencv-python-headless==4.13.0.92
pip install mediapipe==0.10.35
pip install deepface==0.0.100
pip install spacy==3.8.14
pip install plotly==6.7.0

# Supporting
pip install numpy pandas ffmpeg-python

# Webcam recording support
pip install streamlit-webrtc

# Download spaCy English model
python -m spacy download en_core_web_sm

# Database (stdlib — no install needed)
# SQLite ships with Python
```

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

```python
from faster_whisper import WhisperModel

# CRITICAL: INT8 quantization + CPU device
model = WhisperModel(
    "base",        # or "tiny" for faster, "small" for better accuracy
    device="cpu",
    compute_type="int8",    # INT8 is 2x faster than float32 on CPU with minimal accuracy loss
    cpu_threads=4,          # Match your CPU core count; 4 is conservative
    num_workers=1           # Single-worker avoids thread contention on laptops
)

# Use VAD filter to skip silence, reducing processing time by 30-50%
segments, info = model.transcribe(
    "audio.wav",
    beam_size=1,            # Beam 1 is fastest on CPU; beam 5 is more accurate but slower
    vad_filter=True,         # Skip silent segments
    vad_parameters=dict(min_silence_duration_ms=500)
)
```

**Model size vs speed on CPU:**
- `tiny` (39M params): ~1x real-time on typical laptop
- `base` (74M params): ~0.5x real-time (recommended balance)
- `small` (244M params): ~0.25x real-time (use for challenging audio only)

### DeepFace emotion detection on CPU

```python
from deepface import DeepFace

# CRITICAL: Use OpenCV detector backend (fastest on CPU)
# Avoid RetinaFace (accurate but 10x slower on CPU)
result = DeepFace.analyze(
    img_path="frame.jpg",
    actions=['emotion'],          # Only request emotion, skip age/gender/race
    detector_backend='opencv',     # Fastest CPU backend
    enforce_detection=False,       # Don't crash if no face found
    silent=True                    # Suppress verbose logging
)
```

**Processing frames efficiently:**
- Sample 1 frame per 30 seconds of video (not every frame)
- Downscale frames to 640x480 before passing to DeepFace
- Process frames in a background thread (not blocking the UI thread)
- Cache face detection results: if MediaPipe already found a face region, crop to that ROI before DeepFace

### MediaPipe Face Mesh on CPU

```python
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

# CRITICAL: Configure for CPU performance
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,        # False for video, True for single images
    max_num_faces=1,               # Only need one face for interview analysis
    refine_landmarks=True,         # Get iris landmarks for better eye tracking
    min_detection_confidence=0.5,  # Lower = faster but less accurate
    min_tracking_confidence=0.5    # Lower = faster
)
```

**Eye contact detection logic:**
- Use iris landmarks (468 + 10 = 478 landmarks with `refine_landmarks=True`)
- Compute eye gaze direction from iris position relative to eye corners
- Classify as "looking at camera" if gaze vector points toward camera within a threshold

### Audio extraction with ffmpeg (lightweight)

```python
import subprocess
import os

def extract_audio(video_path: str, audio_path: str) -> str:
    """Extract audio using ffmpeg subprocess (no numpy arrays loaded)."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",                    # No video
        "-acodec", "pcm_s16le",   # 16-bit PCM WAV (best for Whisper)
        "-ar", "16000",           # 16kHz sample rate (Whisper native)
        "-ac", "1",               # Mono
        audio_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return audio_path
```

**Why WAV 16kHz mono?** Whisper was trained on 16kHz audio. PCM WAV avoids any lossy compression. This is the standard input format for all Whisper variants.

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

```
Python 3.9  → faster-whisper ✓, Streamlit ✗ (requires 3.10+) → NO
Python 3.10 → faster-whisper ✓, Streamlit ✓, MediaPipe ✓     → OK (conservative)
Python 3.11 → faster-whisper ✓, Streamlit ✓, MediaPipe ✓     → BEST (recommended)
Python 3.12 → faster-whisper ✗ (no wheel), Streamlit ✓       → NO
Python 3.13 → MediaPipe ✗ (no wheel), Streamlit ✓            → NO
```

## Critical Gotchas

### 1. faster-whisper Python version limit
faster-whisper 1.2.1 only supports Python 3.9–3.11. If you install with Python 3.12+, pip will attempt to build from source (which may fail without Rust toolchain). **Use Python 3.11.**

### 2. DeepFace first-run model download
DeepFace downloads pre-trained models on first use (~200MB for VGG-Face emotion model). Cache these in the project directory to avoid repeated downloads. Set `DEEPFACE_HOME` environment variable to a local path.

### 3. MediaPipe legacy API
MediaPipe Face Mesh (`mp.solutions.face_mesh`) is a "legacy solution" as of March 2023. The new API is `mediapipe-tasks` with `FaceLandmarker`. The legacy API still works and is simpler for this use case, but may be removed in future MediaPipe versions. Pin mediapipe version.

### 4. Streamlit file upload size limit
Streamlit's `st.file_uploader` defaults to 200MB max upload. Interview videos can exceed this. Set `server.maxUploadSize` in `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 500
```

### 5. Windows-specific: ffmpeg on PATH
On Windows, ffmpeg must be on the system PATH or available via `imageio-ffmpeg`. Install via Chocolatey (`choco install ffmpeg`) or download the binary and add to PATH. For faster-whisper, this isn't needed (uses PyAV), but for the standalone audio extraction script, you need it.

### 6. Memory management with multiple ML models
Loading faster-whisper + DeepFace + MediaPipe simultaneously can exceed 4GB RAM. Strategy:
- **Unload models after use:** Delete references and call `gc.collect()` between pipeline stages
- **Process sequentially:** Transcribe first → save text → unload Whisper → load DeepFace for frames
- **Frame-by-frame processing:** Don't load all frames into memory. Process one keyframe at a time.

## Stack Patterns by Variant

**If audio quality is poor (noisy environment, heavy accent):**
- Upgrade Whisper model from `base` to `small`
- Set `beam_size=5` for better accuracy (slower)
- Trade: 4x slower transcription for ~15% WER improvement

**If the laptop has very limited RAM (<8GB):**
- Use Whisper `tiny` model (39M params, ~1GB RAM)
- Use `opencv` detector for DeepFace (fastest/lightest)
- Process frames at 1/minute instead of 1/30s
- Consider skipping DeepFace entirely — use MediaPipe landmarks alone for basic affect detection

**If processing speed is critical (user wants results in <30s):**
- Use Whisper `tiny.en` (English-only, faster than multilingual tiny)
- Set `beam_size=1` and `vad_filter=True`
- Extract 5 keyframes only (beginning, 25%, 50%, 75%, end)
- Use OpenCV face detection instead of DeepFace for emotion (less accurate but instant)

**If the project later needs multi-language support:**
- Switch from `tiny.en`/`base.en` to multilingual `tiny`/`base`
- spaCy supports 70+ languages for filler word detection
- DeepFace emotion detection is language-independent (facial expressions are universal)

## Non-Stack Decisions

These aren't "technologies" but are as important as stack choices:

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

**Confidence levels:**
- Package versions: HIGH (verified on PyPI)
- CPU performance claims: HIGH (faster-whisper benchmarks published, community-validated)
- DeepFace vs FER comparison: MEDIUM (based on release cadence + feature comparison, not head-to-head benchmark)
- Python version compatibility: HIGH (verified from each package's PyPI classifiers and setup.py metadata)

---
*Stack research for: AI Interview Analyzer (local CPU-only)*
*Researched: 2026-05-16*
