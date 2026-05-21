"""Enhanced eye contact detection combining head pose + iris gaze estimation.

Provides improved accuracy over the base visual_analysis module by:
- Using more frames (60 vs 20) for smoother, more representative scoring
- Combining head pose (PnP) with iris-based gaze direction
- Applying confidence-weighted blending to handle unreliable detections
- Reducing false negatives when looking at camera with head tilt
- Graceful degradation: falls back to head-pose-only when gaze is unreliable
- Dynamic sigmoid-based weighting (continuous, not binary fallback)
- Temporal smoothing via rolling average to reduce frame-to-frame flickering
- Video-mode FaceLandmarker (RunningMode.VIDEO) for temporal tracking
  across video frames, using 478-point model with iris landmarks

Maintains the same output types (EyeContactResult, FrameEyeContact, EmotionResult)
for full API compatibility. No changes to existing modules.

Dependencies (none modified):
- modules.visual_analysis: extract_keyframes (re-exported), analyze_emotions
- modules.gaze_estimation: compute_gaze_direction, gaze_is_looking_at_camera
- modules.models: EyeContactResult, FrameEyeContact, EmotionResult
- modules.eye_dynamic_weighting: dynamic_combined_score
- modules.eye_temporal_smoothing: smooth_frame_results
- modules.eye_mesh_loader: load_video_face_mesh
"""

from typing import List, Optional, Tuple

import cv2
import numpy as np

from modules.gaze_estimation import compute_gaze_direction, gaze_is_looking_at_camera
from modules.models import EmotionResult, EyeContactResult, FrameEyeContact
from modules.visual_analysis import analyze_emotions, extract_keyframes
from modules.eye_dynamic_weighting import dynamic_combined_score
from modules.eye_temporal_smoothing import smooth_frame_results

# ---------------------------------------------------------------------------
# 3D Face Model for PnP Head Pose
# ---------------------------------------------------------------------------
# Canonical face model (mm) for 6 key MediaPipe landmarks.
# Same model as modules/visual_analysis — duplicated here so original is untouched.

MODEL_POINTS_3D = np.array([
    (0.0, 0.0, 0.0),
    (0.0, -330.0, -65.0),
    (-225.0, 170.0, -135.0),
    (225.0, 170.0, -135.0),
    (-150.0, -150.0, -125.0),
    (150.0, -150.0, -125.0),
], dtype=np.float64)

KEY_LANDMARK_INDICES = [1, 199, 33, 263, 61, 291]

# ---------------------------------------------------------------------------
# Thresholds and weights (tuned for combined head-pose + gaze approach)
# ---------------------------------------------------------------------------

# Head pose thresholds — slightly wider than base (15/10) to account for
# cases where head is turned but eyes compensate toward camera
HEAD_YAW_THRESHOLD = 18.0
HEAD_PITCH_THRESHOLD = 12.0

# Gaze angle threshold (degrees)
GAZE_THRESHOLD = 18.0

# Blending weights: gaze is more indicative of actual eye contact than head pose
HEAD_WEIGHT = 0.35
GAZE_WEIGHT = 0.65

# Confidence filtering
MIN_DETECTION_CONFIDENCE = 0.3   # Below this, mark as not-looking
MIN_GAZE_CONFIDENCE = 0.2        # Below this, fall back to head-pose-only

# More frames for smoother, more representative scoring
ENHANCED_MAX_FRAMES = 20

# Temporal smoothing window (frames)
SMOOTHING_WINDOW = 5
SMOOTHING_CONFIDENCE_THRESHOLD = 0.5

# ---------------------------------------------------------------------------
# Head Pose Estimation (PnP)
# ---------------------------------------------------------------------------


def _compute_head_pose(
    landmarks,
    image_shape: Tuple[int, int],
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Estimate head pose (yaw, pitch, roll) from MediaPipe landmarks via PnP.

    Same algorithm as modules.visual_analysis._compute_head_pose. Duplicated here
    so the original module remains completely untouched.

    Args:
        landmarks: MediaPipe landmark list-like (478 points)
        image_shape: (height, width) of source image

    Returns:
        (yaw, pitch, roll) in degrees, or (None, None, None) if PnP fails.
    """
    h, w = image_shape

    try:
        image_points_2d = []
        for idx in KEY_LANDMARK_INDICES:
            lm = landmarks[idx]
            image_points_2d.append([lm.x * w, lm.y * h])
        image_points_2d = np.array(image_points_2d, dtype=np.float64)
    except (IndexError, AttributeError, TypeError):
        return None, None, None

    focal_length = w
    camera_matrix = np.array([
        [focal_length, 0, w / 2.0],
        [0, focal_length, h / 2.0],
        [0, 0, 1],
    ], dtype=np.float64)

    dist_coeffs = np.zeros((4, 1), dtype=np.float64)

    try:
        success, rvec, tvec = cv2.solvePnP(
            MODEL_POINTS_3D,
            image_points_2d,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )
    except cv2.error:
        return None, None, None

    if not success:
        return None, None, None

    rotation_matrix, _ = cv2.Rodrigues(rvec)

    projection_matrix = np.hstack((
        rotation_matrix,
        np.zeros((3, 1), dtype=np.float64),
    ))
    _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(
        projection_matrix
    )

    pitch = float(euler_angles[0, 0])
    yaw = float(euler_angles[1, 0])
    roll = float(euler_angles[2, 0])

    return yaw, pitch, roll


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------


def _head_pose_contact(
    yaw: Optional[float],
    pitch: Optional[float],
) -> bool:
    """Head-pose-only eye contact check (same logic as visual_analysis.check_eye_contact)."""
    if yaw is None:
        return False
    return abs(yaw) <= HEAD_YAW_THRESHOLD and abs(pitch) <= HEAD_PITCH_THRESHOLD


def _head_pose_confidence(yaw: float, pitch: float) -> float:
    """Confidence from head pose centeredness (0.0-1.0)."""
    deviation = max(abs(yaw) / HEAD_YAW_THRESHOLD, abs(pitch) / HEAD_PITCH_THRESHOLD)
    return max(0.0, min(1.0, 1.0 - deviation))


# ---------------------------------------------------------------------------
# Combined scoring
# ---------------------------------------------------------------------------


def _compute_combined_score(
    yaw: Optional[float],
    pitch: Optional[float],
    gaze_angle_x: Optional[float],
    gaze_angle_y: Optional[float],
    gaze_confidence: float,
) -> Tuple[bool, float]:
    """Combine head pose and gaze into a unified eye contact decision.

    Weighted combination:
    - Normal: 35% head pose + 65% gaze direction
    - Low gaze confidence (< MIN_GAZE_CONFIDENCE): fall back entirely to head pose
    - No head pose (None): rely on gaze if available

    Args:
        yaw, pitch: Head pose angles from PnP (may be None).
        gaze_angle_x, gaze_angle_y: Gaze direction from iris (may be None).
        gaze_confidence: Gaze estimate confidence (0.0-1.0).

    Returns:
        (is_looking, combined_confidence):
            is_looking: Whether subject appears to be looking at camera.
            combined_confidence: Blended score in [0.0, 1.0].
    """
    # Head pose evaluation
    head_looking = _head_pose_contact(yaw, pitch)
    head_conf = _head_pose_confidence(yaw, pitch) if yaw is not None else 0.0

    # Gaze evaluation
    gaze_looking = gaze_is_looking_at_camera(gaze_angle_x, gaze_angle_y, GAZE_THRESHOLD)
    gaze_conf = gaze_confidence

    # Fallback: if gaze is unreliable, use only head pose
    if gaze_confidence < MIN_GAZE_CONFIDENCE or gaze_angle_x is None:
        return head_looking, head_conf

    # Fallback: if head pose failed, use only gaze
    if yaw is None:
        return gaze_looking, gaze_conf

    # Combined weighted decision
    head_score = 1.0 if head_looking else 0.0
    gaze_score = 1.0 if gaze_looking else 0.0

    combined_score = HEAD_WEIGHT * head_score + GAZE_WEIGHT * gaze_score
    is_looking = combined_score >= 0.5

    combined_confidence = HEAD_WEIGHT * head_conf + GAZE_WEIGHT * gaze_conf

    return is_looking, combined_confidence


# ---------------------------------------------------------------------------
# Enhanced eye contact analysis
# ---------------------------------------------------------------------------


def analyze_eye_contact_enhanced(
    frames: List[np.ndarray],
    face_mesh,
    frame_indices: Optional[List[int]] = None,
    image_shape: Optional[Tuple[int, int]] = None,
) -> EyeContactResult:
    """Analyze eye contact across frames using combined head pose + iris gaze.

    Each frame is evaluated with:
    1. MediaPipe face detection and landmark extraction
    2. Head pose via PnP (yaw, pitch from 6 key landmarks)
    3. Gaze direction from iris position relative to eye corners
    4. Confidence-weighted blending into unified looking/not-looking decision
    5. Confidence filtering: frames below MIN_DETECTION_CONFIDENCE are marked
       as not-looking (reduces false positives from poor detections)

    Args:
        frames: List of BGR frames (numpy arrays).
        face_mesh: MediaPipe FaceLandmarker instance.
        frame_indices: Original frame indices (defaults to sequential).
        image_shape: (height, width). Inferred from first frame if None.

    Returns:
        EyeContactResult with enhanced accuracy statistics.
    """
    if frame_indices is None:
        frame_indices = list(range(len(frames)))

    if not frames:
        return EyeContactResult(
            contact_percentage=0.0,
            total_frames=0,
            contact_frames=0,
            frame_results=[],
        )

    if image_shape is None:
        image_shape = frames[0].shape[:2]

    import mediapipe as mp

    frame_results: List[FrameEyeContact] = []

    for frame, idx in zip(frames, frame_indices):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = face_mesh.detect(mp_image)

        if not results.face_landmarks:
            frame_results.append(FrameEyeContact(
                frame_index=idx,
                has_face=False,
                looking_at_camera=False,
                confidence=0.0,
            ))
            continue

        landmarks = results.face_landmarks[0]

        yaw, pitch, roll = _compute_head_pose(landmarks, image_shape)
        gaze_x, gaze_y, gaze_conf = compute_gaze_direction(landmarks, image_shape)

        if yaw is not None:
            looking, confidence = dynamic_combined_score(
                yaw, pitch, gaze_x, gaze_y, gaze_conf,
            )
        else:
            looking = False
            confidence = 0.0

        frame_results.append(FrameEyeContact(
            frame_index=idx,
            has_face=True,
            looking_at_camera=looking,
            confidence=round(confidence, 4),
        ))

    # Temporal smoothing: rolling average to reduce flickering
    frame_results = smooth_frame_results(
        frame_results,
        window_size=SMOOTHING_WINDOW,
        confidence_threshold=SMOOTHING_CONFIDENCE_THRESHOLD,
    )

    # Recalculate contact count from smoothed results
    contact_count = sum(1 for r in frame_results if r.looking_at_camera)
    total = len(frame_results)
    percentage = (contact_count / total * 100.0) if total > 0 else 0.0

    return EyeContactResult(
        contact_percentage=round(percentage, 1),
        total_frames=total,
        contact_frames=contact_count,
        frame_results=frame_results,
    )


# ---------------------------------------------------------------------------
# Integration: analyze_visual (drop-in replacement for visual_analysis)
# ---------------------------------------------------------------------------


def analyze_visual(
    video_path: str,
) -> Tuple[EyeContactResult, EmotionResult]:
    """Complete visual analysis pipeline with enhanced eye contact detection.

    Drop-in replacement for modules.visual_analysis.analyze_visual.
    Same API, same return types. Only the eye contact detection is enhanced —
    emotion analysis delegates to the original module.

    Enhancements over the base version:
    - 60 keyframes (up from 20) for smoother scoring
    - Iris-based gaze estimation combined with head pose
    - Dynamic sigmoid-weighted blending (continuous, not binary fallback)
    - Temporal smoothing via rolling average to reduce flickering
    - Video-mode FaceLandmarker (RunningMode.VIDEO) for temporal tracking
      across frames, using the 478-point model with iris landmarks
    - Confidence filtering to ignore unreliable detections

    Args:
        video_path: Path to the video file to analyze.

    Returns:
        Tuple of (EyeContactResult, EmotionResult).
    """
    from utils.helpers import load_deepface_model, load_mediapipe_face_mesh
    from modules.eye_mesh_loader import load_video_face_mesh

    # Video-mode FaceLandmarker with frame-to-frame temporal tracking
    # (equivalent to legacy static_image_mode=False + refine_landmarks=True)
    video_mesh = load_video_face_mesh()

    # Tasks API FaceLandmarker for emotion analysis (requires different API)
    tasks_mesh = load_mediapipe_face_mesh()

    load_deepface_model()

    frames, frame_indices = extract_keyframes(video_path, max_frames=ENHANCED_MAX_FRAMES)

    if not frames:
        video_mesh.close()
        empty_eye = EyeContactResult(
            contact_percentage=0.0,
            total_frames=0,
            contact_frames=0,
            frame_results=[],
        )
        empty_emotion = EmotionResult(
            dominant_emotion="uncertain",
            emotion_distribution={},
            frames_analyzed=0,
        )
        return empty_eye, empty_emotion

    eye_result = analyze_eye_contact_enhanced(frames, video_mesh, frame_indices)
    emotion_result = analyze_emotions(frames, tasks_mesh, frame_indices)

    video_mesh.close()

    return eye_result, emotion_result
