"""Visual analysis engine: keyframe extraction, eye contact, and emotion detection.

This module provides:
- Keyframe extraction from video files (downscaled to 640×480)
- Eye contact detection via MediaPipe Face Mesh with PnP head pose estimation
- Emotion analysis via DeepFace with soft-voting aggregation
- analyze_visual() integration function for the complete pipeline

Per D-04 through D-18 from the phase context.
"""

from collections import Counter
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from modules.models import (EmotionResult, EyeContactResult, FrameEyeContact)

# ---------------------------------------------------------------------------
# 3D Face Model for PnP Head Pose
# ---------------------------------------------------------------------------
# Canonical face model coordinates (in mm) for 6 key MediaPipe landmarks.
# Used by cv2.solvePnP to estimate head rotation relative to camera.
#
# Landmark indices:
#   1   — Nose tip
#   199 — Chin
#   33  — Left eye left corner
#   263 — Right eye right corner
#   61  — Left mouth corner
#   291 — Right mouth corner

MODEL_POINTS_3D = np.array([
    (0.0, 0.0, 0.0),           # Nose tip
    (0.0, -330.0, -65.0),      # Chin
    (-225.0, 170.0, -135.0),   # Left eye left corner
    (225.0, 170.0, -135.0),    # Right eye right corner
    (-150.0, -150.0, -125.0),  # Left mouth corner
    (150.0, -150.0, -125.0),   # Right mouth corner
], dtype=np.float64)

# Indices of the 6 key MediaPipe landmarks used for PnP
KEY_LANDMARK_INDICES = [1, 199, 33, 263, 61, 291]

# Default thresholds for eye contact classification (D-08)
DEFAULT_YAW_THRESHOLD = 15.0   # ±15 degrees
DEFAULT_PITCH_THRESHOLD = 10.0  # ±10 degrees

# Emotion confidence threshold (D-12) — exclude if dominant emotion ≤ 50%
EMOTION_CONFIDENCE_THRESHOLD = 50.0

# ---------------------------------------------------------------------------
# Keyframe Extraction
# ---------------------------------------------------------------------------


def extract_keyframes(
    video_path: str,
    max_frames: int = 20,
) -> Tuple[List[np.ndarray], List[int]]:
    """Extract evenly-spaced keyframes from a video file.

    Args:
        video_path: Path to the video file.
        max_frames: Maximum number of frames to extract (default 20, per D-04).

    Returns:
        Tuple of (frames, frame_indices):
            frames: List of downscaled frames (640×480, BGR format).
            frame_indices: Original frame index for each extracted frame.

    Handles errors gracefully — returns ([], []) for missing/invalid videos.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return [], []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        return [], []

    # Time-based interval sampling (D-05): max(1, total_frames // max_frames)
    interval = max(1, total_frames // max_frames)

    frames: List[np.ndarray] = []
    frame_indices: List[int] = []

    for i in range(0, total_frames, interval):
        if len(frames) >= max_frames:
            break

        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            continue

        # Downscale to 640×480 (D-06)
        resized = cv2.resize(frame, (640, 480))
        frames.append(resized)
        frame_indices.append(i)

    cap.release()
    return frames, frame_indices


# ---------------------------------------------------------------------------
# Head Pose Estimation (PnP)
# ---------------------------------------------------------------------------


def _compute_head_pose(
    landmarks,
    image_shape: Tuple[int, int],
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Estimate head pose (yaw, pitch, roll) from MediaPipe landmarks via PnP.

    Uses 6 key facial landmarks and cv2.solvePnP with the canonical 3D face
    model to compute rotation angles.

    Args:
        landmarks: MediaPipe landmark list-like object (478 points, each with
                   .x, .y, .z in normalized coordinates 0–1).
        image_shape: (height, width) of the source image.

    Returns:
        (yaw, pitch, roll) in degrees, or (None, None, None) if PnP fails.
    """
    h, w = image_shape

    # Extract 2D positions of the 6 key landmarks (convert normalized → pixel)
    image_points_2d = []
    for idx in KEY_LANDMARK_INDICES:
        lm = landmarks[idx]
        image_points_2d.append([lm.x * w, lm.y * h])
    image_points_2d = np.array(image_points_2d, dtype=np.float64)

    # Camera matrix (focal_length = image_width, center at image center)
    focal_length = w
    camera_matrix = np.array([
        [focal_length, 0, w / 2.0],
        [0, focal_length, h / 2.0],
        [0, 0, 1],
    ], dtype=np.float64)

    dist_coeffs = np.zeros((4, 1), dtype=np.float64)

    # Solve PnP
    success, rvec, tvec = cv2.solvePnP(
        MODEL_POINTS_3D,
        image_points_2d,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )

    if not success:
        return None, None, None

    # Convert rotation vector → rotation matrix
    rotation_matrix, _ = cv2.Rodrigues(rvec)

    # Use OpenCV's decomposeProjectionMatrix for robust Euler angle extraction.
    # Handles all rotation orders and gimbal lock cases that manual trig would miss.
    projection_matrix = np.hstack((
        rotation_matrix,
        np.zeros((3, 1), dtype=np.float64),
    ))
    _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(
        projection_matrix
    )

    # OpenCV decomposeProjectionMatrix returns euler angles as 3x1 array
    # containing: [pitch, yaw, roll] in degrees
    # (convention: X=pitch, Y=yaw, Z=roll).
    pitch = float(euler_angles[0, 0])
    yaw = float(euler_angles[1, 0])
    roll = float(euler_angles[2, 0])

    return yaw, pitch, roll


# ---------------------------------------------------------------------------
# Eye Contact Classification
# ---------------------------------------------------------------------------


def check_eye_contact(
    yaw: Optional[float],
    pitch: Optional[float],
    roll: Optional[float],
    yaw_threshold: float = DEFAULT_YAW_THRESHOLD,
    pitch_threshold: float = DEFAULT_PITCH_THRESHOLD,
) -> bool:
    """Determine if subject is looking at camera based on head pose angles.

    Per D-08: Only yaw and pitch are used for thresholding (roll is ignored).

    Args:
        yaw: Horizontal head rotation in degrees (None if pose unknown).
        pitch: Vertical head rotation in degrees.
        roll: Tilt (ignored in threshold, kept for API completeness).
        yaw_threshold: Maximum absolute yaw for "looking at camera" (default 15°).
        pitch_threshold: Maximum absolute pitch (default 10°).

    Returns:
        True if the subject is looking at the camera, False otherwise.
    """
    if yaw is None:
        return False
    return abs(yaw) <= yaw_threshold and abs(pitch) <= pitch_threshold


def _compute_eye_confidence(
    yaw: float,
    pitch: float,
    yaw_threshold: float = DEFAULT_YAW_THRESHOLD,
    pitch_threshold: float = DEFAULT_PITCH_THRESHOLD,
) -> float:
    """Compute per-frame eye contact confidence (0.0–1.0).

    Based on how centered the head pose is:
    confidence = max(0, 1 - max(|yaw|/yaw_threshold, |pitch|/pitch_threshold))

    Returns:
        Float in [0.0, 1.0].
    """
    normalized_deviation = max(
        abs(yaw) / yaw_threshold,
        abs(pitch) / pitch_threshold,
    )
    return max(0.0, min(1.0, 1.0 - normalized_deviation))


# ---------------------------------------------------------------------------
# Eye Contact Analysis
# ---------------------------------------------------------------------------


def analyze_eye_contact(
    frames: List[np.ndarray],
    face_mesh,
    frame_indices: Optional[List[int]] = None,
    image_shape: Optional[Tuple[int, int]] = None,
) -> EyeContactResult:
    """Analyze eye contact across a list of video frames.

    Per D-08: Uses PnP head pose estimation (yaw ±15°, pitch ±10°),
    Not mere face detection boolean.
    Per D-09: Converts BGR→RGB before passing to MediaPipe.
    Per D-18: If MediaPipe fails on individual frame, marks has_face=False.

    Args:
        frames: List of BGR frames (each as numpy array).
        face_mesh: Loaded MediaPipe FaceMesh instance.
        frame_indices: Original frame indices (defaults to sequential 0..N-1).
        image_shape: Image dimensions (height, width). If None, inferred from
                     the first frame.

    Returns:
        EyeContactResult with aggregated statistics.
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

    frame_results: List[FrameEyeContact] = []
    contact_count = 0

    import mediapipe as mp

    for frame, idx in zip(frames, frame_indices):
        # Convert BGR → RGB (D-09)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = face_mesh.detect(mp_image)

        if results.face_landmarks:
            landmarks = results.face_landmarks[0]
            yaw, pitch, roll = _compute_head_pose(landmarks, image_shape)

            if yaw is not None:
                looking = check_eye_contact(yaw, pitch, roll)
                confidence = _compute_eye_confidence(yaw, pitch)
            else:
                looking = False
                confidence = 0.0

            if looking:
                contact_count += 1

            frame_results.append(FrameEyeContact(
                frame_index=idx,
                has_face=True,
                looking_at_camera=looking,
                confidence=confidence,
            ))
        else:
            # D-18: No face detected
            frame_results.append(FrameEyeContact(
                frame_index=idx,
                has_face=False,
                looking_at_camera=False,
                confidence=0.0,
            ))

    total = len(frame_results)
    percentage = (contact_count / total * 100.0) if total > 0 else 0.0

    return EyeContactResult(
        contact_percentage=round(percentage, 1),
        total_frames=total,
        contact_frames=contact_count,
        frame_results=frame_results,
    )


# ---------------------------------------------------------------------------
# Emotion Aggregation (Soft Voting)
# ---------------------------------------------------------------------------


def _aggregate_emotions(
    deepface_results: List[Dict],
) -> Tuple[str, Dict[str, float]]:
    """Aggregate per-frame DeepFace emotion results via soft voting.

    Per D-12: Frames where dominant emotion confidence ≤ 50% are excluded.
    Per D-13: Soft voting — count how many valid frames had each emotion.
    Tie-break: Alphabetically first emotion is chosen.

    Args:
        deepface_results: List of DeepFace.analyze() result dicts, each
                          containing "emotion" dict and "dominant_emotion" str.

    Returns:
        Tuple of (dominant_emotion, emotion_distribution_dict).
        If no valid frames, returns ("uncertain", {}).
    """
    valid_emotions: List[str] = []

    for result in deepface_results:
        dominant = result.get("dominant_emotion", "")
        emotion_scores = result.get("emotion", {})
        confidence = emotion_scores.get(dominant, 0.0)

        # D-12: Exclude if confidence ≤ 50%
        if confidence > EMOTION_CONFIDENCE_THRESHOLD:
            valid_emotions.append(dominant)

    if not valid_emotions:
        return "uncertain", {}

    # Soft voting: count frequency per emotion
    counter = Counter(valid_emotions)
    total = len(valid_emotions)
    distribution = {emotion: count / total for emotion, count in counter.items()}

    # Dominant: most frequent; tie-break alphabetically first
    max_count = max(counter.values())
    top_emotions = sorted([e for e, c in counter.items() if c == max_count])
    dominant_emotion = top_emotions[0]

    return dominant_emotion, distribution


# ---------------------------------------------------------------------------
# Emotion Analysis
# ---------------------------------------------------------------------------


def _crop_face_roi(
    frame: np.ndarray,
    landmarks,
    margin: float = 0.2,
) -> np.ndarray:
    """Crop frame to face bounding box from MediaPipe landmarks.

    Per D-15: Crop to face ROI before DeepFace for faster processing.

    Args:
        frame: BGR image as numpy array.
        landmarks: MediaPipe landmark list (478 points).
        margin: Extra margin around face bounding box (fraction of size).

    Returns:
        Cropped BGR frame.
    """
    h, w = frame.shape[:2]
    xs = [lm.x * w for lm in landmarks]
    ys = [lm.y * h for lm in landmarks]

    x_min, x_max = int(min(xs)), int(max(xs))
    y_min, y_max = int(min(ys)), int(max(ys))

    # Add margin
    box_w = x_max - x_min
    box_h = y_max - y_min
    margin_x = int(box_w * margin)
    margin_y = int(box_h * margin)

    x_min = max(0, x_min - margin_x)
    x_max = min(w, x_max + margin_x)
    y_min = max(0, y_min - margin_y)
    y_max = min(h, y_max + margin_y)

    return frame[y_min:y_max, x_min:x_max]


def analyze_emotions(
    frames: List[np.ndarray],
    face_mesh,
    frame_indices: Optional[List[int]] = None,
) -> EmotionResult:
    """Analyze emotions across a list of video frames using DeepFace.

    Per D-11: DeepFace with detector_backend='opencv', enforce_detection=False,
              actions=['emotion'].
    Per D-15: Crop to face ROI (from MediaPipe) before DeepFace.
    Per D-17: If DeepFace fails on a single frame, skip and continue.

    Args:
        frames: List of BGR frames.
        face_mesh: Loaded MediaPipe FaceMesh instance (used for ROI cropping).
        frame_indices: Original frame indices (unused in computation, reserved
                       for API consistency).

    Returns:
        EmotionResult with dominant emotion and frequency distribution.
    """
    from deepface import DeepFace

    deepface_results: List[Dict] = []

    import mediapipe as mp

    for frame in frames:
        # Convert to RGB for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = face_mesh.detect(mp_image)

        # Determine image to pass to DeepFace
        if results.face_landmarks:
            # D-15: Crop to face ROI for faster DeepFace processing
            landmarks = results.face_landmarks[0]
            analysis_frame = _crop_face_roi(frame, landmarks)
        else:
            analysis_frame = frame

        try:
            # D-11: DeepFace with opencv backend
            df_result = DeepFace.analyze(
                analysis_frame,
                actions=["emotion"],
                detector_backend="opencv",
                enforce_detection=False,
                silent=True,
            )
            # DeepFace returns a list; take first element
            if isinstance(df_result, list):
                df_result = df_result[0]
            deepface_results.append(df_result)
        except Exception:
            # D-17: Skip failed frames
            continue

    dominant_emotion, distribution = _aggregate_emotions(deepface_results)

    return EmotionResult(
        dominant_emotion=dominant_emotion,
        emotion_distribution=distribution,
        frames_analyzed=len(deepface_results),
    )


# ---------------------------------------------------------------------------
# Integration: analyze_visual
# ---------------------------------------------------------------------------


def analyze_visual(
    video_path: str,
) -> Tuple[EyeContactResult, EmotionResult]:
    """Run the complete visual analysis pipeline on a video file.

    Pipeline:
        1. Load MediaPipe Face Mesh (cached)
        2. Trigger DeepFace model download (cached)
        3. Extract keyframes at even intervals (max 20)
        4. Analyze eye contact via PnP head pose
        5. Analyze emotions via DeepFace with soft voting
        6. Return both results

    Args:
        video_path: Path to the video file to analyze.

    Returns:
        Tuple of (EyeContactResult, EmotionResult).
    """
    # Lazy imports to avoid triggering @st.cache_resource at module load
    from utils.helpers import load_deepface_model, load_mediapipe_face_mesh

    face_mesh = load_mediapipe_face_mesh()
    load_deepface_model()  # Trigger download before processing

    frames, frame_indices = extract_keyframes(video_path, max_frames=20)

    if not frames:
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

    eye_result = analyze_eye_contact(frames, face_mesh, frame_indices)
    emotion_result = analyze_emotions(frames, face_mesh, frame_indices)

    return eye_result, emotion_result
