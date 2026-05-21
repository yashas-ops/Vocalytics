"""Unit tests for dynamic weighting module (eye_dynamic_weighting.py)."""

import pytest

from modules.eye_dynamic_weighting import dynamic_combined_score


class TestDynamicCombinedScore:

    def test_both_agree_looking(self):
        """Both head pose and gaze agree looking at camera."""
        looking, conf = dynamic_combined_score(
            yaw=5.0, pitch=3.0,
            gaze_angle_x=5.0, gaze_angle_y=3.0,
            gaze_confidence=0.8,
        )
        assert looking is True
        assert conf > 0.5

    def test_both_agree_not_looking(self):
        """Both agree NOT looking at camera."""
        looking, conf = dynamic_combined_score(
            yaw=30.0, pitch=20.0,
            gaze_angle_x=40.0, gaze_angle_y=50.0,
            gaze_confidence=0.8,
        )
        assert looking is False

    def test_gaze_overrides_head_with_high_confidence(self):
        """Gaze says looking but head says not -> combined looks (high gaze weight)."""
        looking, conf = dynamic_combined_score(
            yaw=20.0, pitch=5.0,
            gaze_angle_x=10.0, gaze_angle_y=5.0,
            gaze_confidence=0.8,
        )
        assert looking is True

    def test_head_dominant_when_gaze_unreliable(self):
        """Very low gaze confidence -> head pose dominates."""
        looking, conf = dynamic_combined_score(
            yaw=5.0, pitch=3.0,
            gaze_angle_x=50.0, gaze_angle_y=10.0,
            gaze_confidence=0.05,
        )
        assert looking is True
        assert conf > 0.0

    def test_head_none_falls_back_to_gaze(self):
        """Head pose failed -> rely entirely on gaze."""
        looking, conf = dynamic_combined_score(
            yaw=None, pitch=None,
            gaze_angle_x=5.0, gaze_angle_y=3.0,
            gaze_confidence=0.8,
        )
        assert looking is True
        assert conf == 0.8

    def test_gaze_none_falls_back_to_head(self):
        """Gaze unavailable -> rely entirely on head pose."""
        looking, conf = dynamic_combined_score(
            yaw=5.0, pitch=3.0,
            gaze_angle_x=None, gaze_angle_y=None,
            gaze_confidence=0.0,
        )
        assert looking is True
        assert conf > 0.0

    def test_both_unavailable(self):
        """Neither head pose nor gaze available -> not looking."""
        looking, conf = dynamic_combined_score(
            yaw=None, pitch=None,
            gaze_angle_x=None, gaze_angle_y=None,
            gaze_confidence=0.0,
        )
        assert looking is False
        assert conf == 0.0

    def test_confidence_smoothing_no_discontinuity(self):
        """Confidence scores should transition smoothly — no jump >0.1 between adjacent steps."""
        scores = []
        for gc in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            _, conf = dynamic_combined_score(
                yaw=10.0, pitch=5.0,
                gaze_angle_x=10.0, gaze_angle_y=5.0,
                gaze_confidence=gc,
            )
            scores.append(conf)
        for i in range(1, len(scores)):
            assert abs(scores[i] - scores[i - 1]) < 0.1, (
                f"Confidence jump at gaze_confidence={i/10}: "
                f"{scores[i-1]:.4f} -> {scores[i]:.4f}"
            )

    def test_edge_yaw_at_threshold(self):
        """Yaw equal to threshold -> head looking is borderline."""
        looking, conf = dynamic_combined_score(
            yaw=18.0, pitch=5.0,
            gaze_angle_x=5.0, gaze_angle_y=3.0,
            gaze_confidence=0.8,
        )
        assert looking is True

    def test_edge_yaw_just_beyond_threshold(self):
        """Yaw just beyond threshold -> gaze still compensates with high confidence."""
        looking, conf = dynamic_combined_score(
            yaw=19.0, pitch=5.0,
            gaze_angle_x=5.0, gaze_angle_y=3.0,
            gaze_confidence=0.9,
        )
        assert looking is True

    def test_gaze_can_compensate_for_head_turn(self):
        """Yaw beyond threshold but gaze within threshold -> looking (gaze compensates)."""
        looking, conf = dynamic_combined_score(
            yaw=25.0, pitch=5.0,
            gaze_angle_x=10.0, gaze_angle_y=5.0,
            gaze_confidence=0.9,
        )
        assert looking is True

    def test_both_head_and_gaze_far_beyond(self):
        """Both head pose and gaze far beyond threshold -> not looking."""
        looking, conf = dynamic_combined_score(
            yaw=45.0, pitch=5.0,
            gaze_angle_x=30.0, gaze_angle_y=20.0,
            gaze_confidence=0.9,
        )
        assert looking is False
