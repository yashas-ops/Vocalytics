# Phase 4: Visual Analysis — Eye Contact & Emotion - Context

**Gathered:** 2026-05-16
**Status:** Ready for planning

<domain>
## Phase Boundary

System analyzes video frames for eye contact percentage (MediaPipe Face Mesh with PnP head pose estimation) and emotion frequency distribution (DeepFace on max 20 keyframes). Integrates as Step 5 in the existing Upload pipeline. Results stored in existing Pydantic models and displayed on Dashboard with placeholder→live-data conditional rendering.

**Depends on:** Phase 2 (needs uploaded video path and audio extraction) — runs independently of transcript.
**Does NOT include:** Confidence scoring (Phase 5), dashboard chart polishing (Phase 5), SQLite persistence of visual results (Phase 5), report generation (Phase 5).

</domain>

<decisions>
## Implementation Decisions

### Pipeline Integration
- **D-01:** Visual analysis runs as Step 5 in the Upload pipeline, after speech analysis (Step 4). Sequential — matches existing pattern with progress bar + status messages.
- **D-02:** Uses `st.progress(85-95)` step progression and `st.status()` with try/error per sub-step (keyframe extraction → eye contact → emotion analysis).
- **D-03:** Results stored in `st.session_state.last_eye_contact` and `st.session_state.last_emotion`.

### Keyframe Sampling
- **D-04:** Time-based sampling — extract 1 frame every N seconds, soft cap at 20 frames total. If video is shorter, cap at video duration / sample interval.
- **D-05:** Sample interval = max(1, total_duration / 20) seconds, guaranteeing at most 20 frames regardless of video length.
- **D-06:** Frames downscaled to 640x480 before DeepFace analysis (per STACK.md optimization).

### Eye Contact Detection
- **D-07:** Use MediaPipe Face Mesh legacy API (`mp.solutions.face_mesh`) with `static_image_mode=True`, `max_num_faces=1`, `refine_landmarks=True` (already configured in `utils/helpers.py`).
- **D-08:** Eye contact determined by PnP head pose estimation (yaw ±15°, pitch ±10°) using MediaPipe landmarks + OpenCV `solvePnP`. NOT mere face detection.
- **D-09:** Convert BGR→RGB before passing frames to MediaPipe (OpenCV reads BGR, MediaPipe expects RGB).
- **D-10:** Results stored in existing `EyeContactResult` and `FrameEyeContact` models from `modules/models.py`.

### Emotion Analysis
- **D-11:** Use DeepFace with `detector_backend='opencv'`, `enforce_detection=False`, `actions=['emotion']` (per STACK.md optimization).
- **D-12:** Apply confidence threshold: only report an emotion if DeepFace confidence > 50%. Otherwise mark as "uncertain".
- **D-13:** Soft voting across all keyframes for final emotion frequency distribution (not per-frame dominant).
- **D-14:** Results stored in existing `EmotionResult` and `EmotionScores` models from `modules/models.py`.
- **D-15:** If MediaPipe already found a face region, crop to that ROI before passing to DeepFace (caching face detection results).

### Error Handling
- **D-16:** If no face detected in any frame: show "No face detected — ensure you're visible on camera" on Dashboard, mark visual analysis as unavailable, pipeline continues without failure.
- **D-17:** If DeepFace fails on individual frames (e.g., ambiguous detection), skip that frame's emotion analysis and continue with remaining frames.
- **D-18:** If MediaPipe fails on individual frames, mark that frame as `has_face=False, looking_at_camera=False` and include in total_frames count.

### Dashboard Display
- **D-19:** Eye contact shown as percentage metric card (replacing existing "—" placeholder) + brief text annotation (e.g., "Good — maintained eye contact 72% of the time").
- **D-20:** Emotion displayed as dominant emotion badge + frequency distribution (horizontal bar chart or small table).
- **D-21:** Use Plotly for charts if interactivity desired; otherwise use `st.bar_chart` for simplicity (per D-11 dark theme — Plotly supports dark theme natively).
- **D-22:** Dashboard shows placeholder state when no visual analysis data exists (matches Phase 3 conditional rendering pattern).

### the agent's Discretion
- Exact chart type and layout (bar chart vs dataframe) — keep consistent with dark navy theme.
- Color scheme for emotion chart labels.
- Whether to use a single `st.cache_data` call for the combined visual analysis or store per-substep results.
- File structure within `modules/` — single `visual_analysis.py` vs separate `eye_contact.py` + `emotion.py`.
- Error message wording for no-face and partial-results scenarios.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Research & Architecture
- `.planning/research/STACK.md` §CPU Optimization Patterns — MediaPipe and DeepFace CPU optimization code snippets, model configuration
- `.planning/research/PITFALLS.md` §Pitfall 3, §Pitfall 6, §Pitfall 8, §Pitfall 11 — Keyframe sampling, eye contact metric, emotion transition handling, MediaPipe API version
- `.planning/research/SUMMARY.md` §Phase 4 — Architecture summary for visual analysis phase

### Project Specs
- `.planning/ROADMAP.md` §Phase 4 — Phase goal, success criteria, dependencies
- `.planning/REQUIREMENTS.md` §Visual Analysis — VIS-01, VIS-02, VIS-03 definitions

### Existing Code Patterns
- `modules/models.py` — `EyeContactResult`, `FrameEyeContact`, `EmotionResult`, `EmotionScores` (existing models)
- `utils/helpers.py` — `load_mediapipe_face_mesh()`, `load_deepface_model()` (existing model loaders)
- `app.py` — Upload pipeline structure (Steps 1-4), Dashboard conditional rendering pattern
- `modules/speech_analysis.py` — Reference for module structure and error handling patterns

### Existing Research Artifacts
- `.planning/research/ARCHITECTURE.md` — Pipeline architecture and component boundaries
- `.planning/research/STACK.md` — Version compatibility, library choices

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `utils/helpers.py::load_mediapipe_face_mesh()` — Already configured with static_image_mode=True, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5
- `utils/helpers.py::load_deepface_model()` — Sentinel cached loader for DeepFace model download
- `modules/models.py::EyeContactResult`, `FrameEyeContact`, `EmotionResult`, `EmotionScores` — All Pydantic models defined and importable
- OpenCV (`opencv-python-headless`) already in requirements.txt
- MediaPipe (`mediapipe==0.10.35`) already in requirements.txt
- DeepFace (`deepface==0.0.100`) already in requirements.txt

### Established Patterns
- Sequential pipeline with progress bar (`st.progress()`) and status messages (`st.status()`) — established in Phases 2-3
- `try/except` per pipeline step with graceful error display (st.error + status.update)
- `@st.cache_resource` for ML model loaders in utils/helpers.py
- Session state storage pattern: `st.session_state.last_*`
- Dashboard conditional rendering: placeholder when no data, metrics when data exists (Phase 3)
- Independent module files in `modules/` with typed function signatures
- Tests in `tests/` with pytest

### Integration Points
- `app.py` Upload pipeline: insert Step 5 after speech analysis (after line 146, before session state storage)
- `app.py` Dashboard: replace "Eye Contact" and placeholder metrics with live data from session state
- Pipeline needs `video_path` (available from Step 1) — not the TranscriptResult
- Session state: `last_eye_contact` + `last_emotion` stored alongside `last_transcript` + `last_speech_analysis`

</code_context>

<specifics>
## Specific Ideas

- DeepFace model download on first run (~200MB) — should be documented in setup steps for Phase 4 to avoid surprise delays during analysis
- MediaPipe Face Mesh with PnP head pose is the gold standard for eye contact — not EAR (eye aspect ratio) which only detects blinking
- Emotion confidence threshold >50% prevents false precision on ambiguous expressions (from PITFALLS.md §Pitfall 8)
- OpenCV `cv2.VideoCapture` for frame extraction — lightweight, no moviepy memory overhead

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-visual-analysis-eye-contact-emotion*
*Context gathered: 2026-05-16*
