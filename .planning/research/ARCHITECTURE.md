# Architecture Research

**Domain:** Local AI Interview Analyzer (video-based)
**Researched:** 2026-05-16
**Confidence:** HIGH

## Standard Architecture

### System Overview

The system follows a **sequential pipeline architecture** where each stage is an independent module that transforms data and passes it forward. The pipeline is the backbone — every stage reads from the previous stage's output and writes structured data for the next.

```
┌──────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                             │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                 Streamlit (Single Frontend)                    │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────────┐ │    │
│  │  │ Upload / │ │ Analysis │ │ History  │ │ Dashboard /     │ │    │
│  │  │ Record   │ │ Status   │ │ Browser  │ │ Feedback Report │ │    │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬────────┘ │    │
│  └───────┼─────────────┼────────────┼────────────────┼──────────┘    │
└──────────┼─────────────┼────────────┼────────────────┼───────────────┘
           │             │            │                │
           ▼             ▼            ▼                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         PIPELINE LAYER                                │
│                                                                       │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌─────────────┐  │
│  │  Audio     │   │ Transcribe │   │  Speech    │   │  Feedback   │  │
│  │ Extraction │──▶│ (Whisper)  │──▶│  Analysis  │──▶│  Generation │  │
│  │ (moviepy)  │   │            │   │ (filler,   │   │ (template)  │  │
│  └────────────┘   └────────────┘   │ WPM)       │   └─────────────┘  │
│                                    └────────────┘                    │
│  ┌────────────┐   ┌────────────────────────────────────────────┐     │
│  │  Frame     │   │         Visual Analysis                     │     │
│  │ Extraction │──▶│  ┌──────────────┐  ┌─────────────────────┐ │     │
│  │ (OpenCV)   │   │  │ Eye Contact  │  │ Emotion Detection  │ │     │
│  └────────────┘   │  │ (MediaPipe)  │  │ (DeepFace/FER)     │ │     │
│                   │  └──────────────┘  └─────────────────────┘ │     │
│                   └────────────────────────────────────────────┘     │
│                                    │                                 │
│                                    ▼                                 │
│                          ┌──────────────────┐                        │
│                          │ Confidence       │                        │
│                          │ Scorer           │                        │
│                          │ (weighted        │                        │
│                          │  heuristic)      │                        │
│                          └──────────────────┘                        │
└──────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         PERSISTENCE LAYER                             │
│  ┌────────────────────────────────────┐  ┌─────────────────────────┐ │
│  │       SQLite Database              │  │   File System           │ │
│  │  ├─ interviews(id, date, ...)      │  │   ├─ uploads/           │ │
│  │  ├─ transcript_segments            │  │   ├─ audio/             │ │
│  │  ├─ filler_word_counts             │  │   ├─ frames/            │ │
│  │  ├─ frame_analyses                 │  │   └─ output_reports/    │ │
│  │  └─ feedback_reports               │  │                         │ │
│  └────────────────────────────────────┘  └─────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|---------------|------------------------|
| **Audio Extractor** | Extracts audio track from uploaded video, converts to 16kHz WAV | `moviepy` or `ffmpeg-python` subprocess |
| **Transcriber** | Converts audio waveform to text with word-level timestamps | `faster-whisper` (tiny or base model, int8 quantized) |
| **Speech Analyzer** | Detects filler words (um, uh, like, etc.), calculates speaking speed (WPM) | Pure Python on transcript text + timestamps |
| **Face Analyzer** | Processes video frames for eye contact (MediaPipe Face Mesh) and emotion (DeepFace keyframe sampling) | `mediapipe` for face landmarks, `deepface`/`fer` for emotions |
| **Frame Extractor** | Samples video frames at configurable intervals for visual analysis | `opencv-python` VideoCapture |
| **Confidence Scorer** | Combines all metrics into a 0-100 confidence score via weighted heuristic | Pure Python scoring function |
| **Feedback Generator** | Produces structured feedback report from all analysis results | Template-based (fstrings + conditional logic + spaCy for NLP) |
| **History Manager** | Persists and retrieves past interview analysis records | SQLite via `sqlite3` module |
| **Dashboard** | Displays analysis results: video player, charts, scores, transcript, feedback | Streamlit components (`st.video`, `st.line_chart`, `st.metric`, etc.) |

## Recommended Project Structure

```
ctracker/
├── .planning/                  # Project planning docs (excluded from pip)
│
├── streamlit_app.py            # Entrypoint: router + shared UI frame
│
├── app_pages/                  # Streamlit pages (NOT "pages/" — avoids auto-discovery conflicts)
│   ├── __init__.py
│   ├── upload.py               # Video upload / webcam record page
│   ├── analysis.py             # Pipeline execution status + progress
│   ├── dashboard.py            # Results display (charts, scores, transcript)
│   ├── history.py              # Past interview browser
│   └── settings.py             # Model selection, sampling rates, etc.
│
├── modules/                    # Core analysis pipeline modules
│   ├── __init__.py
│   ├── models.py               # Pydantic data models (shared types)
│   ├── audio_extractor.py      # video → audio (moviepy or ffmpeg)
│   ├── transcriber.py          # audio → transcript (faster-whisper)
│   ├── speech_analyzer.py      # transcript → filler words, WPM
│   ├── frame_extractor.py      # video → sampled frames (OpenCV)
│   ├── face_analyzer.py        # frames → eye contact, emotions
│   ├── confidence_scorer.py    # all metrics → 0-100 score
│   └── feedback_generator.py   # all metrics → feedback report
│
├── db/                         # Database layer
│   ├── __init__.py
│   ├── schema.py               # CREATE TABLE statements
│   ├── connection.py           # SQLite connection manager
│   └── repository.py           # CRUD operations
│
├── utils/                      # Shared utilities
│   ├── __init__.py
│   ├── file_ops.py             # Temp file management, cleanup
│   └── video_utils.py          # Format validation, metadata extraction
│
├── data/                       # Runtime data (git-ignored)
│   ├── uploads/                # Raw uploaded videos
│   ├── audio/                  # Extracted WAV files
│   ├── frames/                 # Sampled keyframes
│   ├── reports/                # Generated feedback reports
│   └── interview_history.db    # SQLite database file
│
├── tests/                      # Test suite
│   ├── test_audio_extractor.py
│   ├── test_transcriber.py
│   ├── test_speech_analyzer.py
│   ├── test_face_analyzer.py
│   ├── test_confidence_scorer.py
│   └── test_feedback_generator.py
│
├── requirements.txt
└── README.md
```

### Structure Rationale

- **`app_pages/` instead of `pages/`:** Streamlit's `st.navigation` API (v1.36+) ignores the legacy `pages/` auto-discovery when used. Naming it `app_pages/` avoids any future confusion and keeps the intent explicit. Pages are registered in `streamlit_app.py` via `st.Page()`.

- **`modules/` is the pipeline backbone:** Each module is a **pure function** (or close to it) — takes defined inputs, returns defined outputs, no side effects. This makes each stage independently testable and debuggable. Modules do NOT import streamlit — they're CLI/testable Python code.

- **`db/` is a thin persistence layer:** Kept separate from the pipeline modules because it's an orthogonal concern. The pipeline produces data; the DB layer stores and retrieves it. This prevents pipeline code from being coupled to storage decisions.

- **`data/` is git-ignored:** Video files, audio, and frames are large binary blobs. Storing paths in SQLite, not the blobs themselves. The `data/` directory is created at runtime.

- **Modules vs Pages separation:** Pages import and call modules, never the reverse. This enforces a clean dependency direction: UI → Pipeline → Data, never circular.

## Architectural Patterns

### Pattern 1: Sequential Pipeline with Cached Stages

**What:** Each pipeline stage is a function that reads its input (from a previous stage or file), processes it, and writes structured output to a known location. Stages can be skipped if their output already exists (resume/cache support).

**When to use:** This project — strictly sequential analysis with clear data dependencies. Not suitable for real-time or streaming scenarios.

**Trade-offs:**
- + Simple to reason about, debug, and test
- + Natural failure isolation (stage N fails, stages 1..N-1 are cached)
- + Enables "resume from stage N" if a later stage crashes
- − Sequential means no parallelism between stages (but acceptably fast for CPU analysis)
- − Must process full stage before seeing any results (not streaming)

**Example:**
```python
# modules/pipeline_orchestrator.py (conceptual — not a separate file, called from pages)

def run_pipeline(video_path: str, config: AnalysisConfig) -> AnalysisResult:
    """Run full analysis pipeline with caching."""
    pipeline_dir = Path(config.working_dir)

    # Stage 1: Audio extraction (cache key: audio WAV)
    audio_path = pipeline_dir / "audio.wav"
    if not audio_path.exists():
        audio_path = extract_audio(video_path, audio_path)

    # Stage 2: Transcription (cache key: transcript JSON)
    transcript_path = pipeline_dir / "transcript.json"
    if not transcript_path.exists():
        transcript = transcribe(audio_path, model_size=config.whisper_model)
        transcript_path.write_text(transcript.model_dump_json())

    # Stage 3: Speech analysis (fast, always re-run on latest transcript)
    transcript_data = Transcript.model_validate_json(transcript_path.read_text())
    speech_metrics = analyze_speech(transcript_data)

    # Stage 4: Frame extraction (cache key: frames directory)
    frames_dir = pipeline_dir / "frames"
    if not frames_dir.exists():
        extract_frames(video_path, frames_dir, fps=config.frame_sample_rate)

    # Stage 5: Face analysis (cache key: face_results JSON)
    face_path = pipeline_dir / "face_results.json"
    if not face_path.exists():
        face_results = analyze_faces(frames_dir, config.min_detection_confidence)
        face_path.write_text(face_results.model_dump_json())

    # Stage 6: Aggregate & score
    face_data = FaceResults.model_validate_json(face_path.read_text())
    confidence = compute_confidence(speech_metrics, face_data)
    feedback = generate_feedback(speech_metrics, face_data, confidence)

    return AnalysisResult(
        transcript=transcript_data,
        speech_metrics=speech_metrics,
        face_results=face_data,
        confidence=confidence,
        feedback=feedback
    )
```

### Pattern 2: Repository Pattern for Persistence

**What:** All database operations go through a Repository class that encapsulates SQLite queries. The rest of the application never writes raw SQL.

**When to use:** Even for SQLite — keeps query logic in one place, makes schema changes manageable.

**Trade-offs:**
- + Single place to audit all DB interactions
- + Easy to mock for testing
- + Schema changes only affect one file
- − Slightly more boilerplate than inline queries (worth it for maintainability)

**Example:**
```python
# db/repository.py

class InterviewRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def save_interview(self, result: AnalysisResult) -> int:
        """Insert a new interview record, return its ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "INSERT INTO interviews (date, duration_seconds, confidence_score) VALUES (?, ?, ?)",
            (datetime.now().isoformat(), result.duration, result.confidence.score)
        )
        interview_id = cursor.lastrowid
        self._save_transcript(conn, interview_id, result.transcript)
        self._save_frame_analyses(conn, interview_id, result.face_results)
        conn.commit()
        conn.close()
        return interview_id

    def get_all_interviews(self) -> list[InterviewSummary]:
        """Return summary list of all interviews."""
        ...

    def get_interview_detail(self, interview_id: int) -> AnalysisResult | None:
        """Return full detail for one interview."""
        ...
```

### Pattern 3: Data Models with Pydantic (Single Source of Truth)

**What:** All data structures shared across the pipeline are defined as Pydantic BaseModel classes in `modules/models.py`. Every pipeline stage declares its input and output types explicitly.

**When to use:** Any multi-stage pipeline where data crosses module boundaries.

**Trade-offs:**
- + Self-documenting data contracts between stages
- + Validation at module boundaries catches corruption early
- + Easy serialization to JSON (for caching) and dict (for Streamlit display)
- − Requires discipline to keep models in sync with DB schema (use same field names/types)

**Example:**
```python
# modules/models.py

from pydantic import BaseModel
from enum import Enum

class SpeakingSpeed(str, Enum):
    SLOW = "slow"       # < 120 WPM
    GOOD = "good"       # 120-160 WPM
    FAST = "fast"       # > 160 WPM

class TranscriptSegment(BaseModel):
    start: float        # seconds
    end: float          # seconds
    text: str

class Transcript(BaseModel):
    segments: list[TranscriptSegment]
    full_text: str

class SpeechMetrics(BaseModel):
    total_words: int
    filler_word_count: dict[str, int]  # {"um": 3, "like": 5, ...}
    total_fillers: int
    wpm: float
    speed_classification: SpeakingSpeed

class FrameAnalysis(BaseModel):
    frame_index: int
    timestamp: float
    eye_contact: bool           # True if looking at camera
    dominant_emotion: str | None
    emotion_confidences: dict[str, float] | None

class FaceResults(BaseModel):
    total_frames_analyzed: int
    eye_contact_percentage: float
    emotion_summary: dict[str, float]   # {"happy": 45%, "neutral": 30%, ...}
    per_frame: list[FrameAnalysis]

class ConfidenceScore(BaseModel):
    score: float                # 0-100
    components: dict[str, float]  # {"eye_contact": 80, "speech_speed": 65, ...}

class FeedbackReport(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    tips: list[str]
    summary: str

class AnalysisResult(BaseModel):
    interview_id: int | None = None
    duration_seconds: float
    transcript: Transcript
    speech_metrics: SpeechMetrics
    face_results: FaceResults
    confidence: ConfidenceScore
    feedback: FeedbackReport
    created_at: str
```

## Data Flow

### Pipeline Data Flow

```
Upload/Record Video (MP4, MOV, AVI)
    │
    ▼
┌────────────────────────────────────────────┐
│ 1. Audio Extraction     ┌──────────────┐   │
│    Input:  video file   │ moviepy /    │   │
│    Output: 16kHz WAV    │ ffmpeg       │   │
│    Duration: ~0.1x video│ subprocess   │   │
│    (fast, ffmpeg)       └──────────────┘   │
└─────────────────────┬──────────────────────┘
                      │ audio.wav
                      ▼
┌────────────────────────────────────────────┐
│ 2. Transcription       ┌──────────────┐   │
│    Input:  audio WAV   │ faster-      │   │
│    Output: transcript   │ whisper      │   │
│    with segments       │ (tiny/base)  │   │
│    Duration: ~2-10x    └──────────────┘   │
│    audio length (CPU)                      │
│    ⚠ Bottleneck #1                         │
└─────────────────────┬──────────────────────┘
                      │ Transcript (segments + full_text)
                      ▼
┌────────────────────────────────────────────┐
│ 3. Speech Analysis    ┌──────────────┐   │
│    Input:  transcript │ Pure Python  │   │
│    Output: metrics    │ (no models)  │   │
│    (filler words,     └──────────────┘   │
│     WPM, speed class)                    │
│    Duration: instant                     │
└─────────────────────┬──────────────────────┘
                      │ SpeechMetrics
                      ▼
┌────────────────────────────────────────────┐
│ 4. Frame Extraction   ┌──────────────┐   │
│    Input:  video file │ OpenCV       │   │
│    Output: sampled    │ VideoCapture │   │
│    frames (images)    └──────────────┘   │
│    Sample rate: 1-2 fps                  │
│    (configurable)                        │
│    Frames saved as JPEG to temp dir      │
└─────────────────────┬──────────────────────┘
                      │ frame_*.jpg
                      ▼
┌────────────────────────────────────────────┐
│ 5a. Eye Contact       ┌──────────────┐   │
│     Input:  frames    │ MediaPipe    │   │
│     Output: per-frame │ Face Mesh    │   │
│     eye contact bool  └──────────────┘   │
│     Duration: ~20ms/frame (CPU)          │
├──────────────────────────────────────────┤
│ 5b. Emotion Detection ┌──────────────┐   │
│     Input:  frames    │ DeepFace or  │   │
│     Output: per-frame │ FER          │   │
│     emotion + conf    └──────────────┘   │
│     ⚠ Bottleneck #2                     │
│     Duration: 2-5s/frame (CPU)           │
│     Strategy: sample subset of frames    │
└─────────────────────┬──────────────────────┘
                      │ FaceResults
                      ▼
┌────────────────────────────────────────────┐
│ 6. Confidence Scoring ┌──────────────┐   │
│    Input:  all metrics│ Weighted     │   │
│    Output: 0-100 score│ heuristic    │   │
│    Components:        └──────────────┘   │
│    - Eye contact (30%)                    │
│    - Speaking speed (20%)                 │
│    - Filler words (20%)                   │
│    - Emotion / positivity (15%)           │
│    - Clarity / transcript quality (15%)   │
│    Duration: instant                      │
└─────────────────────┬──────────────────────┘
                      │ ConfidenceScore
                      ▼
┌────────────────────────────────────────────┐
│ 7. Feedback Generation ┌──────────────┐   │
│    Input:  all metrics +│ Template     │   │
│            confidence   │ engine       │   │
│    Output: report       │ + spaCy NLP  │   │
│    (strengths,          └──────────────┘   │
│     weaknesses, tips)                      │
│    Duration: instant                       │
└─────────────────────┬──────────────────────┘
                      │ FeedbackReport
                      ▼
┌────────────────────────────────────────────┐
│ 8. Persist & Display                       │
│    Store: SQLite (interview record + all   │
│           analysis results stored as JSON) │
│    Display: Streamlit dashboard            │
│    - st.video: side-by-side player         │
│    - st.metric: confidence, WPM, fillers   │
│    - st.line_chart: emotion timeline       │
│    - st.markdown: feedback report          │
│    - st.expander: full transcript          │
└────────────────────────────────────────────┘
```

### Key Data Flows

1. **Video → Audio → Text flow:** The critical sequential path. Audio extraction is fast (ffmpeg). Transcription is the #1 bottleneck on CPU. Must use `faster-whisper` with tiny/base model and int8 quantization. For a 5-minute video, expect 10-25 minutes for transcription on CPU.

2. **Video → Frames → Visual metrics flow:** Runs independently of the text pipeline. Can execute in parallel (but Streamlit single-thread means stages run sequentially in practice). Frame sampling rate directly controls total time:
   - 1 FPS for a 5-min video = 300 frames
   - MediaPipe on 300 frames ≈ 6-10 seconds (fast)
   - DeepFace on 300 frames ≈ 10-25 minutes (very slow)
   - **Strategy:** Run DeepFace on only 10-20 keyframes (every 15-30 frames or scene changes)

3. **Aggregate → Score → Feedback flow:** Instant. All metrics are already computed. The heuristic scorer and template engine are pure Python, no models.

## CPU Performance Considerations

### Bottleneck Analysis

| Pipeline Stage | CPU Time (5-min video) | Strategy |
|---------------|------------------------|----------|
| Audio extraction (ffmpeg) | ~15-30 seconds | Use subprocess, not Python loop |
| Transcription (faster-whisper tiny) | ~5-15 minutes | **Bottleneck #1.** Use `tiny` model, `int8` compute. Consider `base` only for accuracy needs. |
| Transcription (faster-whisper base) | ~10-25 minutes | Acceptable for MVP, warn user about long processing |
| MediaPipe face mesh (300 frames @ 1fps) | ~6-10 seconds | Well within bounds. CPU-efficient. |
| DeepFace emotion (300 frames) | ~10-25 minutes | **Bottleneck #2.** Sample max 20 frames. |
| DeepFace emotion (20 frames) | ~40-60 seconds | Acceptable. Sample evenly across video. |
| All other stages | <1 second total | Instant. No model involved. |

### CPU Optimization Rules

1. **Always use `faster-whisper` over `openai-whisper`** — it's 3-4x faster on CPU due to CTranslate2 backend with int8 quantization. Never use the reference `openai-whisper` package for CPU inference.

2. **Set `compute_type="int8"`** on `faster-whisper` — reduces memory bandwidth 4x with negligible accuracy loss for English transcription.

3. **Downscale video frames before MediaPipe** — 640x480 is sufficient for face landmark detection. Beyond 720p, downscale to save CPU.

4. **Sample frames at max 1-2 FPS** for face analysis — the interview scenario has slow head movement; 2 FPS captures it fine. For DeepFace, sample at most 1 frame per 15-30 seconds.

5. **Use `opencv-python-headless`** instead of `opencv-python` — avoids GUI dependency overhead on servers.

6. **Prefer `moviepy` for audio extraction** — it wraps ffmpeg cleanly and is well-maintained. Fallback to direct `ffmpeg-python` if moviepy has version conflicts.

7. **Cache everything** — Once a stage completes, save its output to a temp file. If the video hasn't changed, skip the stage on re-analysis. The pipeline should be idempotent.

### Impact on Build Order

The relative speed of stages determines the **phase ordering** recommendation:

| Phase | Focus | Rationale |
|-------|-------|-----------|
| 1 | Data models + DB schema + file management | No models, pure infrastructure |
| 2 | Audio extraction + Basic Streamlit upload | Fast, visual feedback loop — user can upload immediately |
| 3 | Speech analysis (filler words, WPM) | No heavy model — gives instant score from transcript |
| 4 | Transcription (faster-whisper) | Heavy model, but unlocks ALL text features. Do early enough to test CPU performance. |
| 5 | MediaPipe face mesh (eye contact) | Medium cost, high value metric. Independent of text pipeline. |
| 6 | Emotion detection + Confidence scorer | Heavy model but with keyframe sampling. Depends on face pipeline. |
| 7 | Feedback generation + Template engine | Pure text, depends on all metrics. Do last. |
| 8 | Full dashboard + History browser | Polish phase — all data available to display. |

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1 user (this project) | Current design is perfect. Single SQLite DB, single pipeline, all temp files local. |
| 10-100 users | Would need task queue (Celery/RQ), separate worker processes, multi-user DB. Out of scope. |
| 100+ users | Would need GPU workers, distributed storage, async architecture. Way out of scope. |

### Scaling Priorities

1. **First bottleneck:** CPU-bound Whisper transcription. Even at single-user, a 10-min interview takes 20+ mins to transcribe. Mitigation: use `tiny` model, show progress bar, make pipeline resumable.

2. **Second bottleneck:** DeepFace emotion detection on CPU. Mitigation: aggressive frame sampling (10-20 frames total), or skip emotion in MVP and add as enhancement.

## Anti-Patterns

### Anti-Pattern 1: Monolithic Streamlit App

**What people do:** Put all logic (upload, processing, display, DB) into a single `app.py` file 800+ lines long.

**Why it's wrong:** Impossible to test individual pipeline stages, impossible to reuse pipeline code outside Streamlit, debugging requires spinning up the full app.

**Do this instead:** Separate UI (`app_pages/`) from logic (`modules/`). Modules never import `streamlit`. They return Pydantic models. Pages call modules and render results. The pipeline runs independently of the UI.

### Anti-Pattern 2: Processing Full Frames for Emotion Detection

**What people do:** Feed every frame of a video to DeepFace, expecting it to process at video frame rate.

**Why it's wrong:** DeepFace on CPU takes 2-5 seconds PER FRAME. A 5-minute video at 30fps (9000 frames) would take 5-12 hours.

**Do this instead:** Sample frames aggressively:
- Eye contact: 1-2 fps (MediaPipe is fast enough for this)
- Emotion: 1 frame per 15-30 seconds (10-20 frames total for a 5-min video)
- Use frame quality filter: skip blurry frames, skip frames where face confidence < 0.7

### Anti-Pattern 3: Storing Binary Blobs in SQLite

**What people do:** Store video files, audio files, or large JSON blobs directly in SQLite BLOB columns.

**Why it's wrong:** SQLite with large blobs becomes slow to query and backup. Video files can be 100s of MB. The DB will balloon in size.

**Do this instead:** Store file paths in SQLite, put actual binary data in the `data/` filesystem directory. SQLite stores metadata and structured analysis results as JSON text. Only small structured data goes in the DB.

### Anti-Pattern 4: Blocking UI During Long Processing

**What people do:** Call a long-running pipeline function directly in a Streamlit callback, freezing the UI until processing completes.

**Why it's wrong:** Streamlit is single-threaded. A 25-minute transcription will lock the entire app. User sees a spinner and can't navigate away.

**Do this instead:** 
- Use `st.session_state` to track pipeline state (`idle → extracting → transcribing → analyzing → complete`)
- Use `st.progress` and `st.status` for feedback
- Break processing into steps, updating state + re-rendering between steps
- Each step does a small unit of work, then returns control to Streamlit's event loop
- Consider `st.rerun()` pattern to check if processing is done
- For MVP, accept the blocking UI but show detailed progress

### Anti-Pattern 5: Tightly Coupled Pipeline Stages

**What people do:** Stage 3 accesses Stage 1's internal data structures directly, or passes around raw dicts with string keys.

**Why it's wrong:** Any change to Stage 1's output silently breaks Stage 3. Impossible to test stages independently. Refactoring becomes painful.

**Do this instead:** Use Pydantic models as the contract between stages. Each stage declares `Input: ModelA, Output: ModelB`. If the contract changes, the type system catches it immediately. Each stage can be tested with mock inputs that match the Pydantic model.

## Integration Points

### External Tools

| Tool | Integration Pattern | Notes |
|------|--------------------|-------|
| ffmpeg | Subprocess call via `moviepy` or `ffmpeg-python` | Must be installed on system. Check at startup and warn user. |
| faster-whisper | Python library (`from faster_whisper import WhisperModel`) | Models download on first use (~140MB for tiny, ~290MB for base). Cache in `~/.cache/faster_whisper/`. |
| MediaPipe | Python library (`import mediapipe as mp`) | Models bundled with package. No separate download. |
| DeepFace | Python library (`from deepface import DeepFace`) | Downloads model weights on first use. Specify `models/` subdirectory to cache locally. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `app_pages/` ↔ `modules/` | Direct function calls, Pydantic model returns | Pages import and call modules. Modules never import pages. |
| `modules/` ↔ `db/` | Repository pattern | Pipeline calls `repository.save(result)` at end. Repository handles all SQL. |
| `modules/` ↔ `utils/` | Direct function calls | File management, path resolution, format checking. |
| `app_pages/` ↔ `db/` | Repository pattern | History page queries DB directly via repository. |

### Webcam Integration

Webcam recording uses `st.camera_input` in Streamlit. The resulting `uploaded_file` object is a BytesIO that gets saved to disk just like an uploaded file. The same pipeline processes both uploaded and recorded videos identically. No special handling needed — `st.camera_input` returns a file-like object that OpenCV can read.

## Streamlit App Architecture Details

### Entrypoint Router Pattern (streamlit_app.py)

```python
# streamlit_app.py

import streamlit as st

# Must be the first Streamlit command
st.set_page_config(page_title="Interview Analyzer", layout="wide")

# Initialize shared session state
if "pipeline_state" not in st.session_state:
    st.session_state.pipeline_state = "idle"  # idle | running | complete | error
if "current_result" not in st.session_state:
    st.session_state.current_result = None

# Define pages
upload_page = st.Page("app_pages/upload.py", title="Upload / Record", icon=":material/videocam:")
dashboard_page = st.Page("app_pages/dashboard.py", title="Dashboard", icon=":material/dashboard:")
history_page = st.Page("app_pages/history.py", title="History", icon=":material/history:")
settings_page = st.Page("app_pages/settings.py", title="Settings", icon=":material/settings:")

# Navigation — show all pages even before analysis
pg = st.navigation({
    "Record": [upload_page],
    "Analyze": [dashboard_page],
    "Browse": [history_page],
    "Config": [settings_page],
}, position="sidebar")

# Shared UI (runs before every page)
st.title(":material/quiz: AI Interview Analyzer")

# Run the selected page
pg.run()
```

### Pipeline State Machine (stored in session_state)

```
idle ──(upload)──▶ uploading ──(complete)──▶ extracted
  ▲                                                  │
  │                                         (start analysis)
  │                                                  ▼
  │                                              transcribing
  │                                                  │
  │                                         (complete or fail)
  │                                                  │
  │                                                  ▼
  │                                              analyzing_faces
  │                                                  │
  │                                         (complete or fail)
  │                                                  │
  │                                                  ▼
  │                                              scoring
  │                                                  │
  │                                         (complete or fail)
  │                                                  │
  │                                                  ▼
  │                                              complete ──(view results)──▶ dashboard
  │                                                  │
  └──────────────(new video)─────────────────────────┘
```

This state machine is the key to handling long-running processing in Streamlit. Each state transition is triggered by a button click or auto-rerun. The user sees progress updates between each state.

## Sources

- [Streamlit Multipage Apps with st.Page and st.navigation](https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation) — HIGH confidence (official docs)
- [MediaPipe Face Mesh CPU Performance](https://github.com/google/mediapipe/issues/2784) — MEDIUM confidence (GitHub issue, but representative)
- [faster-whisper CPU Performance](https://github.com/franckferman/whispr) — MEDIUM confidence (GitHub project with benchmarks)
- [Whisper CPU-Only Execution Guide](https://deepwiki.com/manzolo/openai-whisper-docker/4.3-running-cpu-only-transcriptions) — MEDIUM confidence (community documentation)
- [Building an AI Tennis Coach with MediaPipe (Streamlit + pipeline pattern)](https://gauravsarma1992.medium.com/building-an-ai-tennis-coach-with-mediapipe-and-claude-4d791a2dd278) — MEDIUM confidence (blog post, well-architected example)
- [Video-Understanding-Local (Streamlit + Whisper + CLIP + FAISS architecture)](https://github.com/circuminds/End-To-End-Video-Understanding) — MEDIUM confidence (GitHub project, similar domain)
- [PRVIA: Pre-Recorded Video Interview Analysis](https://github.com/Mohamed-samy2/Video-Interview-Analysis) — MEDIUM confidence (GitHub project, academic/commercial)
- [AI Video Content Analysis Pipeline (CODITECT)](https://docs.coditect.ai/research/lab/video-analysis-sdd) — MEDIUM confidence (system design doc)
- [Video Processing Pipeline Architecture (DEV Community)](https://dev.to/kyle_clipspeedai/the-architecture-behind-an-ai-video-processing-pipeline-2cdj) — MEDIUM confidence (production pipeline patterns)
- [MediaPipe Real-Time CV Framework](https://mediapipe.org/mediapipe-real-time-computer-vision-and-machine-learning-framework-2/) — HIGH confidence (official site)

---

*Architecture research for: AI Interview Analyzer*
*Researched: 2026-05-16*
