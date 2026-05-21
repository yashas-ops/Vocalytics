"""Unit tests for temporal smoothing module (eye_temporal_smoothing.py)."""

import numpy as np
import pytest

from modules.eye_temporal_smoothing import smooth_frame_results
from modules.models import FrameEyeContact


def _make_results(confidences, has_face=True):
    """Build FrameEyeContact list from confidence values."""
    return [
        FrameEyeContact(
            frame_index=i,
            has_face=has_face,
            looking_at_camera=c >= 0.5,
            confidence=c,
        )
        for i, c in enumerate(confidences)
    ]


class TestSmoothFrameResults:

    def test_empty_input(self):
        """Empty list returns empty list."""
        result = smooth_frame_results([])
        assert result == []

    def test_single_frame(self):
        """Single frame unchanged."""
        results = _make_results([0.8])
        smoothed = smooth_frame_results(results, window_size=3)
        assert len(smoothed) == 1
        assert smoothed[0].confidence == 0.8

    def test_average_of_identical(self):
        """All frames with same confidence should stay the same."""
        results = _make_results([0.7, 0.7, 0.7, 0.7, 0.7])
        smoothed = smooth_frame_results(results, window_size=3)
        for r in smoothed:
            assert r.confidence == pytest.approx(0.7, abs=0.01)

    def test_smoothing_reduces_extremes(self):
        """A single outlier frame should be pulled toward neighbors."""
        results = _make_results([0.9, 0.1, 0.9])
        smoothed = smooth_frame_results(results, window_size=3)
        assert smoothed[1].confidence > 0.1
        assert smoothed[1].confidence < 0.9

    def test_flicker_suppression(self):
        """Alternating high/low should be smoothed."""
        results = _make_results([0.9, 0.1, 0.9, 0.1, 0.9])
        smoothed = smooth_frame_results(results, window_size=3)
        confs = [r.confidence for r in smoothed]
        std = np.std(confs)
        unsmoothed_std = np.std([r.confidence for r in results])
        assert std < unsmoothed_std, (
            f"Expected smoothed std ({std:.3f}) < unsmoothed std ({unsmoothed_std:.3f})"
        )

    def test_window_size_one(self):
        """Window size 1 -> no change."""
        results = _make_results([0.2, 0.8, 0.5])
        smoothed = smooth_frame_results(results, window_size=1)
        for orig, s in zip(results, smoothed):
            assert s.confidence == orig.confidence

    def test_no_face_frames_not_reclassified(self):
        """Frames with has_face=False should stay has_face=False and not looking."""
        results = [
            FrameEyeContact(frame_index=0, has_face=True, looking_at_camera=True, confidence=0.9),
            FrameEyeContact(frame_index=1, has_face=False, looking_at_camera=False, confidence=0.0),
            FrameEyeContact(frame_index=2, has_face=True, looking_at_camera=True, confidence=0.9),
        ]
        smoothed = smooth_frame_results(results, window_size=3)
        assert smoothed[1].has_face is False
        assert smoothed[1].looking_at_camera is False

    def test_edge_at_boundary(self):
        """Edge frames (first and last) should still be smoothed, not biased."""
        results = _make_results([0.9, 0.9, 0.9, 0.9, 0.1])
        smoothed = smooth_frame_results(results, window_size=3)
        assert smoothed[-1].confidence < 0.9
        assert smoothed[-1].confidence > 0.1

    def test_large_window_on_small_input(self):
        """Window larger than input should handle gracefully."""
        results = _make_results([0.8, 0.2])
        smoothed = smooth_frame_results(results, window_size=10)
        assert len(smoothed) == 2
        assert 0.2 <= smoothed[0].confidence <= 0.8
        assert 0.2 <= smoothed[1].confidence <= 0.8

    def test_confidence_threshold_affects_looking(self):
        """Frames above threshold are looking, below are not."""
        results = _make_results([0.6, 0.6, 0.6])
        smoothed = smooth_frame_results(results, window_size=1, confidence_threshold=0.5)
        assert all(r.looking_at_camera for r in smoothed)

        smoothed2 = smooth_frame_results(results, window_size=1, confidence_threshold=0.7)
        assert not any(r.looking_at_camera for r in smoothed2)
