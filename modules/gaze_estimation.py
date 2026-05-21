"""Iris-based gaze estimation using MediaPipe Face Mesh iris landmarks.

Provides functions to compute gaze direction from iris position relative
to eye corners. Used by eye_contact_enhanced for improved eye contact detection.

Iris landmarks (indices 468-477) are part of the MediaPipe 478-landmark model
and are available when using the standard face_landmarker.task model.
"""

from typing import Tuple, Optional

import numpy as np

# Iris landmark indices (MediaPipe Face Mesh 478-landmark model)
LEFT_IRIS_CENTER = 468
RIGHT_IRIS_CENTER = 473

# Eye corner landmark indices
# 33 = outer corner (near ear), 133 = inner corner (near nose)
LEFT_EYE_OUTER = 33
LEFT_EYE_INNER = 133
RIGHT_EYE_INNER = 263
RIGHT_EYE_OUTER = 362

# Eye top / bottom for vertical gaze estimation
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
RIGHT_EYE_TOP = 386
RIGHT_EYE_BOTTOM = 374

# Maximum plausible gaze deviation from center (degrees)
MAX_GAZE_ANGLE = 30.0


def _safe_unit_axis(start: np.ndarray, end: np.ndarray) -> tuple[np.ndarray | None, float]:
    """Return the unit axis and span length when the two eye points are usable."""
    span = float(np.linalg.norm(end - start))
    if span < 1.0:
        return None, span
    return (end - start) / span, span


def _fallback_horizontal_gaze(
    iris: np.ndarray,
    top: np.ndarray,
    bottom: np.ndarray,
    reference_width: float,
) -> float | None:
    """Estimate horizontal iris position when an eye corner pair collapses."""
    if reference_width < 1.0:
        return None

    eye_center_x = float((top[0] + bottom[0]) / 2.0)
    normalized_offset = (float(iris[0]) - eye_center_x) / reference_width
    return float(np.clip(0.5 + normalized_offset, 0.0, 1.0))


def compute_gaze_direction(
    landmarks,
    image_shape: Tuple[int, int],
) -> Tuple[Optional[float], Optional[float], float]:
    """Compute gaze direction from iris position relative to eye corners.

    Uses MediaPipe iris landmarks (468-477) to determine where the subject
    is looking. When looking at camera, the iris is centered in the eye.
    When looking away, the iris shifts toward one side.

    Args:
        landmarks: MediaPipe landmark list-like (478 points, each with
                   .x, .y, .z in normalized coordinates 0-1).
        image_shape: (height, width) of the source image.

    Returns:
        (gaze_angle_x, gaze_angle_y, confidence):
            gaze_angle_x: Horizontal angle in degrees (negative=left, positive=right).
            gaze_angle_y: Vertical angle in degrees (negative=up, positive=down).
            confidence: Detection confidence (0.0-1.0) based on inter-eye agreement.
        Returns (None, None, 0.0) if iris landmarks are unavailable.
    """
    h, w = image_shape

    try:
        left_iris = np.array([
            landmarks[LEFT_IRIS_CENTER].x * w,
            landmarks[LEFT_IRIS_CENTER].y * h,
        ])
        right_iris = np.array([
            landmarks[RIGHT_IRIS_CENTER].x * w,
            landmarks[RIGHT_IRIS_CENTER].y * h,
        ])

        left_inner = np.array([
            landmarks[LEFT_EYE_INNER].x * w,
            landmarks[LEFT_EYE_INNER].y * h,
        ])
        left_outer = np.array([
            landmarks[LEFT_EYE_OUTER].x * w,
            landmarks[LEFT_EYE_OUTER].y * h,
        ])
        right_inner = np.array([
            landmarks[RIGHT_EYE_INNER].x * w,
            landmarks[RIGHT_EYE_INNER].y * h,
        ])
        right_outer = np.array([
            landmarks[RIGHT_EYE_OUTER].x * w,
            landmarks[RIGHT_EYE_OUTER].y * h,
        ])

        left_top = np.array([
            landmarks[LEFT_EYE_TOP].x * w,
            landmarks[LEFT_EYE_TOP].y * h,
        ])
        left_bottom = np.array([
            landmarks[LEFT_EYE_BOTTOM].x * w,
            landmarks[LEFT_EYE_BOTTOM].y * h,
        ])
        right_top = np.array([
            landmarks[RIGHT_EYE_TOP].x * w,
            landmarks[RIGHT_EYE_TOP].y * h,
        ])
        right_bottom = np.array([
            landmarks[RIGHT_EYE_BOTTOM].x * w,
            landmarks[RIGHT_EYE_BOTTOM].y * h,
        ])
    except (IndexError, AttributeError):
        return None, None, 0.0

    axis_l, eye_width_l = _safe_unit_axis(left_inner, left_outer)
    axis_r, eye_width_r = _safe_unit_axis(right_outer, right_inner)
    eye_height_l = max(np.linalg.norm(left_bottom - left_top), 1e-6)
    eye_height_r = max(np.linalg.norm(right_bottom - right_top), 1e-6)

    # Horizontal position: project iris onto eye axis
    # Left eye: 0 = outer, 1 = inner (reversed so both map same direction)
    left_h = (
        float(np.clip(np.dot(left_iris - left_inner, axis_l) / eye_width_l, 0.0, 1.0))
        if axis_l is not None
        else _fallback_horizontal_gaze(left_iris, left_top, left_bottom, eye_width_r)
    )
    right_h_same_convention = axis_r is None
    right_h = (
        _fallback_horizontal_gaze(right_iris, right_top, right_bottom, eye_width_l)
        if right_h_same_convention
        else float(np.clip(np.dot(right_iris - right_outer, axis_r) / eye_width_r, 0.0, 1.0))
    )

    if left_h is None or right_h is None:
        return None, None, 0.0

    # Vertical position: 0 = top, 1 = bottom
    vaxis_l = (left_bottom - left_top) / eye_height_l
    vaxis_r = (right_bottom - right_top) / eye_height_r
    left_v = np.clip(np.dot(left_iris - left_top, vaxis_l) / eye_height_l, 0.0, 1.0)
    right_v = np.clip(np.dot(right_iris - right_top, vaxis_r) / eye_height_r, 0.0, 1.0)

    # Left eye h: 0 = inner (looking LEFT), 1 = outer (looking RIGHT)
    # Right eye h: 0 = outer (looking RIGHT), 1 = inner (looking LEFT) — inverted
    # Convert right eye to same convention: 0 = looking LEFT, 1 = looking RIGHT
    left_gaze = left_h
    right_gaze = right_h if right_h_same_convention else 1.0 - right_h

    # Average both eyes (now with consistent gaze direction mapping)
    avg_h = float((left_gaze + right_gaze) / 2.0)
    avg_v = float((left_v + right_v) / 2.0)

    # Convert to angles: map 0.0-1.0 to -MAX_GAZE_ANGLE to +MAX_GAZE_ANGLE
    gaze_angle_x = (avg_h - 0.5) * 2.0 * MAX_GAZE_ANGLE
    gaze_angle_y = (avg_v - 0.5) * 2.0 * MAX_GAZE_ANGLE

    # Confidence: inter-eye agreement (lower when one eye is occluded)
    # Use gaze-direction values (not raw h) so both eyes agree when looking same way
    h_agreement = 1.0 - min(1.0, abs(left_gaze - right_gaze) * 2.0)
    v_agreement = 1.0 - min(1.0, abs(left_v - right_v) * 2.0)
    confidence = float((h_agreement + v_agreement) / 2.0)

    return gaze_angle_x, gaze_angle_y, confidence


def gaze_is_looking_at_camera(
    gaze_angle_x: Optional[float],
    gaze_angle_y: Optional[float],
    threshold: float = 18.0,
) -> bool:
    """Determine if gaze is directed at the camera.

    Args:
        gaze_angle_x: Horizontal gaze angle in degrees, or None.
        gaze_angle_y: Vertical gaze angle in degrees, or None.
        threshold: Maximum absolute angle for "looking at camera" (degrees).

    Returns:
        True if gaze is within threshold of camera center.
    """
    if gaze_angle_x is None:
        return False
    return abs(gaze_angle_x) <= threshold and abs(gaze_angle_y) <= threshold
