---
phase: 04-visual-analysis-eye-contact-emotion
plan: 01
subsystem: visual-analysis
tags: [mediapipe, deepface, opencv, pnp, head-pose, emotion, tdd]

# Dependency graph
requires:
  - phase: 01-core-infrastructure-data-models
    provides: EyeContactResult, FrameEyeContact, EmotionResult, EmotionScores, FaceMesh loader, DeepFace sentinel
  - phase: 02-video-upload-audio-pipeline-transcription
    provides: Video upload pipeline (video_path input for analyze_visual)
provides:
  - Keyframe extraction from video (max 20 frames, 640x480 downscale)
  - Eye contact detection via MediaPipe PnP head pose estimation (yaw ±15°, pitch ±10°)
  - Emotion analysis via DeepFace with soft-voting aggregation (50% confidence threshold)
  - analyze_visual() integration function
affects: Phase 4 plan 02, Phase 5 scoring/dashboard

# Tech tracking
tech-stack:
  added: []
  patterns:
    - MockMediaPipe-landmarks for head pose unit testing
    - Modular visual analysis pipeline: frames → eye contact → emotion
    - Soft voting with confidence threshold for emotion aggregation

key-files:
  created:
    - modules/visual_analysis.py
    - tests/test_visual_analysis.py
  modified: []

key-decisions:
  - "PnP head pose estimation using cv2.solvePnP with 6-key face landmarks and cv2.decomposeProjectionMatrix for Euler angles"
  - "Emotion confidence checked as dominant emotion score value > 50% (DeepFace returns 0-100 scale)"
  - "Helper imports (load_mediapipe_face_mesh, load_deepface_model) lazy-loaded inside analyze_visual to avoid @st.cache_resource triggering at module import time"
  - "camera_matrix focal_length = image_width, center = (w/2, h/2) per standard head pose estimation convention"

patterns-established:
  - "Visual analysis follows same modular structure as speech_analysis.py: private helpers prefixed with _, public API functions, one integration function"
  - "MediaPipe landmarks mocked as simple objects with x/y/z attributes for unit testing without the real model"

requirements-completed: [VIS-01, VIS-02, VIS-03]

# Metrics
duration: 12min
completed: 2026-05-16
---

# Phase 4: Visual Analysis — Eye Contact & Emotion Summary

**Keyframe extraction via OpenCV, MediaPipe PnP head pose eye contact detection, and DeepFace emotion analysis with soft-voting aggregation — tested via TDD with 10 unit tests**

## Performance

- **Duration:** 12 min
- **Started:** 2026-05-16T07:20:00Z
- **Completed:** 2026-05-16T07:32:31Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files modified:** 2

## Accomplishments
- `extract_keyframes()` — OpenCV-based keyframe extraction from video files with configurable max_frames (default 20), even-interval sampling, and automatic 640x480 downscaling. Handles missing files gracefully.
- `_compute_head_pose()` — PnP head pose estimation using 6 MediaPipe key landmarks (nose tip, chin, eyes corners, mouth corners) with cv2.solvePnP and cv2.decomposeProjectionMatrix for robust Euler angle extraction.
- `check_eye_contact()` — Yaw/pitch thresholding (default ±15° yaw, ±10° pitch) determines if subject is looking at camera.
- `analyze_eye_contact()` — Per-frame eye contact analysis with confidence scoring based on how centered the head pose is (normalized deviation from center).
- `_aggregate_emotions()` — Soft voting across DeepFace results with 50% confidence threshold exclusion. Tie-breaking: alphabetically first.
- `analyze_emotions()` — DeepFace emotion analysis with detector_backend='opencv', face ROI cropping from MediaPipe landmarks for speed, graceful skip on failed frames.
- `analyze_visual()` — Integration function composing all sub-modules: loads models, extracts keyframes, runs eye contact + emotion analysis, returns both results.

## Task Commits

Each task was committed atomically:

1. **Task 1: RED — Write failing tests** — `a329dd4` (test)
2. **Task 1: GREEN — Implement module** — `f167c30` (feat)

**Plan metadata:** *(pending metadata commit)*

_Note: TDD task had separate RED (test) and GREEN (feat) commits. REFACTOR phase skipped — code clean, edge cases handled, no changes needed._

## Files Created/Modified

### Created
- `modules/visual_analysis.py` (531 lines) — Visual analysis engine with 7 public/private functions:
  - `extract_keyframes` — Keyframe extraction
  - `_compute_head_pose` — PnP head pose estimation (private)
  - `check_eye_contact` — Yaw/pitch threshold classification
  - `analyze_eye_contact` — Per-frame eye contact analysis
  - `_aggregate_emotions` — Soft voting emotion aggregation (private)
  - `analyze_emotions` — DeepFace emotion analysis
  - `analyze_visual` — Integration function

- `tests/test_visual_analysis.py` (294 lines) — 10 unit tests covering:
  - Keyframe count, dimensions, and missing-video error handling
  - PnP head pose with forward-facing synthetic landmarks
  - Eye contact thresholding (within/outside bounds)
  - Emotion soft voting and confidence threshold
  - Integration with mocked sub-functions

## Decisions Made
- Used `cv2.decomposeProjectionMatrix` for Euler angle extraction from rotation matrix instead of manual trigonometric formulas. OpenCV's built-in decomposition handles rotation order conventions and gimbal lock cases robustly.
- DeepFace emotion scores are 0-100 scale (percentages), not 0-1 probabilities. The 50% confidence threshold check is `score > 50.0`.
- Helper imports (`load_mediapipe_face_mesh`, `load_deepface_model`) lazy-loaded inside `analyze_visual()` to avoid triggering `@st.cache_resource` decorators at module import time — critical for testability without Streamlit runtime.
- Mock landmarks for head pose tests computed as perspective projection of the canonical 3D face model with identity rotation at distance t=2000mm — ensures solvePnP returns rotation angles ≈ 0° for forward-facing mock faces.

## Deviations from Plan

**None — plan executed exactly as written.** No bugs found, no missing critical functionality, no blocking issues requiring deviation.

## Issues Encountered
- **PnP Euler angle formula** — Initial manual trigonometric formulas (pitch=-arcsin(R[2,1]), yaw=arctan2(R[2,0], R[2,2]), roll=arctan2(R[0,1], R[1,1])) produced incorrect results (180° yaw) with approximate mock landmarks. Switched to `cv2.decomposeProjectionMatrix` which handles rotation order conventions robustly.
- **Emotion score scale** — Mock test data used 0-1 probability values but DeepFace returns 0-100 percentages. Fixed test data to use realistic DeepFace output format (80.0, 70.0, 60.0, etc.).
- **Helper imports** — Integration test tried to patch `modules.visual_analysis.load_mediapipe_face_mesh` but the import is lazy (inside `analyze_visual`). Fixed by patching `utils.helpers.load_mediapipe_face_mesh` instead.

## User Setup Required

None — no external service configuration required. Dependencies were already in requirements.txt (opencv-python-headless, mediapipe, deepface).

## Next Phase Readiness
- Visual analysis engine complete — ready for Plan 04-02 (pipeline integration + dashboard display)
- `analyze_visual(video_path)` provides the single-entry-point API for the Upload pipeline to call during analysis
- All Pydantic models for eye contact and emotion results were already defined in Phase 1 — no model changes needed
- Pipeline will need to call `analyze_visual(video_path)` after transcription/audio analysis, passing the video file path

## Self-Check: PASSED
- [x] `modules/visual_analysis.py` exists (531 lines, 4 exports)
- [x] `tests/test_visual_analysis.py` exists (294 lines, 10 tests)
- [x] Commit `a329dd4` — RED phase test file
- [x] Commit `f167c30` — GREEN phase implementation
- [x] All 22 tests pass (10 visual analysis + 12 speech analysis)
- [x] Module imports cleanly: `from modules.visual_analysis import extract_keyframes, analyze_eye_contact, analyze_emotions, analyze_visual`
- [x] Models compatible: EyeContactResult and EmotionResult construct without errors

---
*Phase: 04-visual-analysis-eye-contact-emotion*
*Plan: 01*
*Completed: 2026-05-16*
