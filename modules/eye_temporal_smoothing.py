"""Temporal smoothing for eye contact frame results.

Applies a rolling average to per-frame confidence values to reduce
flickering and produce more stable eye contact predictions across
consecutive video frames. This mitigates frame-to-frame noise from
both head pose estimation and iris gaze estimation.
"""

from typing import List

import numpy as np

from modules.models import FrameEyeContact


def _rolling_average(values: List[float], window_size: int) -> np.ndarray:
    """Apply a centered rolling average with edge correction.

    For interior points, uses a symmetric window of size window_size.
    For boundary points (fewer elements available on one side), uses
    a progressively smaller window so the output stays length-matched
    without introducing bias from distant values.

    Args:
        values: 1-D list of float confidence values.
        window_size: Width of the rolling window (must be >= 1).

    Returns:
        np.ndarray of smoothed values, same length as input.
    """
    arr = np.array(values, dtype=np.float64)
    n = len(arr)
    if n <= 1 or window_size <= 1:
        return arr

    kernel = np.ones(window_size) / window_size
    smoothed = np.convolve(arr, kernel, mode="same")

    half = window_size // 2

    for i in range(half):
        usable = min(i + half + 1, n)
        smoothed[i] = np.mean(arr[:usable])

    for i in range(max(1, n - half), n):
        start = max(0, i - half)
        smoothed[i] = np.mean(arr[start:])

    return smoothed


def smooth_frame_results(
    frame_results: List[FrameEyeContact],
    window_size: int = 5,
    confidence_threshold: float = 0.5,
) -> List[FrameEyeContact]:
    """Apply temporal smoothing to a list of per-frame eye contact results.

    A centered rolling average is applied to the confidence values.
    A frame is classified as "looking at camera" if the smoothed
    confidence meets or exceeds the threshold AND the frame originally
    had a face detected (has_face keeps its original value).

    Frames where has_face=False retain has_face=False and are never
    reclassified as looking, regardless of smoothed confidence —
    smoothing leakage from surrounding frames is prevented.

    Args:
        frame_results: Original per-frame eye contact results.
        window_size: Number of frames in the rolling window (default 5).
        confidence_threshold: Minimum smoothed confidence to count as
                              looking (default 0.5).

    Returns:
        New list of FrameEyeContact with smoothed confidence and
        re-evaluated looking_at_camera. Same length as input.
    """
    if not frame_results:
        return []

    confidences = [r.confidence for r in frame_results]
    smoothed = _rolling_average(confidences, window_size)

    new_results: List[FrameEyeContact] = []
    for i, r in enumerate(frame_results):
        sc = float(smoothed[i])
        looking = r.has_face and sc >= confidence_threshold

        new_results.append(FrameEyeContact(
            frame_index=r.frame_index,
            has_face=r.has_face,
            looking_at_camera=looking,
            confidence=round(sc, 4),
        ))

    return new_results
