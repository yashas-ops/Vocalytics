"""Dynamic confidence-weighted blending between head pose and iris gaze.

Provides continuous sigmoid-based fallback weighting: when iris/gaze
confidence is low, the system smoothly shifts reliance toward head pose.
When gaze confidence is high, gaze estimation takes priority.

This replaces the binary fallback threshold (cut-and-switch) in the
original _compute_combined_score with a continuous transition,
reducing edge-case discontinuities around the threshold boundary.
"""

from typing import Optional, Tuple

import numpy as np

from modules.gaze_estimation import gaze_is_looking_at_camera

# ---------------------------------------------------------------------------
# Thresholds (same defaults as eye_contact_enhanced for consistent behavior)
# ---------------------------------------------------------------------------
HEAD_YAW_THRESHOLD = 18.0
HEAD_PITCH_THRESHOLD = 12.0
GAZE_THRESHOLD = 18.0

# ---------------------------------------------------------------------------
# Weight bounds
# ---------------------------------------------------------------------------
# When gaze_confidence = 0: 100% head pose weight
# When gaze_confidence = 1: GAZE_WEIGHT_MAX% gaze, (1 - GAZE_WEIGHT_MAX)% head
GAZE_WEIGHT_MAX = 0.65


def _sigmoid_weight(
    confidence: float,
    midpoint: float = 0.35,
    steepness: float = 10.0,
) -> float:
    """Smooth transition weight from head-dominant to gaze-dominant.

    Args:
        confidence: Gaze estimation confidence (0.0-1.0).
        midpoint: Confidence value where weight is at half-maximum.
        steepness: Steepness of the transition curve.

    Returns:
        Gaze weight in [0.0, GAZE_WEIGHT_MAX].
    """
    raw = 1.0 / (1.0 + np.exp(-steepness * (confidence - midpoint)))
    return float(raw * GAZE_WEIGHT_MAX)


def _head_pose_contact(yaw: Optional[float], pitch: Optional[float]) -> bool:
    """Head-pose-only eye contact check."""
    if yaw is None:
        return False
    return abs(yaw) <= HEAD_YAW_THRESHOLD and abs(pitch) <= HEAD_PITCH_THRESHOLD


def _head_pose_confidence(yaw: float, pitch: float) -> float:
    """Confidence from head pose centeredness (0.0-1.0)."""
    deviation = max(abs(yaw) / HEAD_YAW_THRESHOLD, abs(pitch) / HEAD_PITCH_THRESHOLD)
    return max(0.0, min(1.0, 1.0 - deviation))


def dynamic_combined_score(
    yaw: Optional[float],
    pitch: Optional[float],
    gaze_angle_x: Optional[float],
    gaze_angle_y: Optional[float],
    gaze_confidence: float,
) -> Tuple[bool, float]:
    """Combine head pose and gaze with smooth confidence-weighted blending.

    Unlike the binary fallback (cut gaze off entirely below a threshold),
    this uses a sigmoid function to smoothly interpolate between
    head-dominant and gaze-dominant weighting:

        gaze_confidence = 0.0  →  100% head pose (no gaze data trusted)
        gaze_confidence = 0.35 →  50/50 blend of head and gaze
        gaze_confidence = 1.0  →  65% gaze, 35% head pose

    This eliminates the discontinuity at the binary threshold boundary.

    Args:
        yaw: Head yaw in degrees, or None if PnP failed.
        pitch: Head pitch in degrees, or None if PnP failed.
        gaze_angle_x: Horizontal gaze angle in degrees, or None.
        gaze_angle_y: Vertical gaze angle in degrees, or None.
        gaze_confidence: Gaze estimate confidence (0.0-1.0).

    Returns:
        (is_looking, combined_confidence):
            is_looking: Whether the subject appears to be looking at camera.
            combined_confidence: Blended score in [0.0, 1.0].
    """
    head_looking = _head_pose_contact(yaw, pitch)
    head_conf = _head_pose_confidence(yaw, pitch) if yaw is not None else 0.0

    gaze_available = gaze_angle_x is not None
    gaze_looking = (
        gaze_is_looking_at_camera(gaze_angle_x, gaze_angle_y, GAZE_THRESHOLD)
        if gaze_available
        else False
    )
    gaze_conf = gaze_confidence if gaze_available else 0.0

    # --- Fallback: pure head pose when gaze is completely unavailable ---
    if not gaze_available:
        return head_looking, head_conf

    # --- Fallback: pure gaze when head pose failed ---
    if yaw is None:
        return gaze_looking, gaze_conf

    # --- Continuous blending ---
    gaze_weight = _sigmoid_weight(gaze_confidence)
    head_weight = 1.0 - gaze_weight

    head_score = 1.0 if head_looking else 0.0
    gaze_score = 1.0 if gaze_looking else 0.0

    combined_score = head_weight * head_score + gaze_weight * gaze_score
    is_looking = combined_score >= 0.5

    combined_confidence = head_weight * head_conf + gaze_weight * gaze_conf

    return is_looking, combined_confidence
