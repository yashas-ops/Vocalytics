"""Unit tests for gaze estimation and enhanced eye contact detection modules."""

from typing import Dict, List
from unittest.mock import patch

import numpy as np
import pytest

from modules.models import EmotionResult, EyeContactResult, FrameEyeContact


class MockLandmark:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


# Eye corner positions (normalized)
# landmark 33 = outer corner (near ear), 133 = inner corner (near nose)
# landmark 263 = inner corner, 362 = outer corner
LEFT_EYE_OUTER = (0.379, 0.621)   # landmark 33
LEFT_EYE_INNER = (0.44, 0.62)     # landmark 133
RIGHT_EYE_INNER = (0.621, 0.621)  # landmark 263
RIGHT_EYE_OUTER = (0.56, 0.62)    # landmark 362

LEFT_EYE_TOP = (0.41, 0.59)
LEFT_EYE_BOTTOM = (0.41, 0.65)
RIGHT_EYE_TOP = (0.59, 0.59)
RIGHT_EYE_BOTTOM = (0.59, 0.65)

# Eye spans for computing iris positions
LEFT_HALF_RANGE = (LEFT_EYE_INNER[0] - LEFT_EYE_OUTER[0]) / 2.0  # 0.0305
LEFT_CENTER_X = (LEFT_EYE_INNER[0] + LEFT_EYE_OUTER[0]) / 2.0    # 0.4095
RIGHT_HALF_RANGE = (RIGHT_EYE_OUTER[0] - RIGHT_EYE_INNER[0]) / 2.0  # 0.0305
RIGHT_CENTER_X = (RIGHT_EYE_INNER[0] + RIGHT_EYE_OUTER[0]) / 2.0    # 0.5905

# Iris vertical center
IRIS_CENTER_Y = 0.62
IRIS_VERT_HALF_RANGE = 0.03


def _build_face_landmarks(
    gaze_offset: float = 0.0,
    vert_offset: float = 0.0,
    disagree: bool = False,
) -> list:
    """Build 478 mock landmarks with adjustable gaze direction.

    Args:
        gaze_offset: Horizontal gaze (-1..1). 0=centered, negative=left, positive=right.
        vert_offset: Vertical gaze (-1..1). 0=centered, negative=up, positive=down.
        disagree: If True, left eye shifts opposite to right (for confidence tests).

    Returns:
        List of 478 MockLandmark objects.

    When gaze_offset=0: iris centered in both eyes → gaze angles ≈ 0.
    When gaze_offset<0: iris shifts left → negative gaze_x.
    When gaze_offset>0: iris shifts right → positive gaze_x.
    """
    right_offset = -gaze_offset if disagree else gaze_offset

    left_iris_x = LEFT_CENTER_X - gaze_offset * LEFT_HALF_RANGE
    right_iris_x = RIGHT_CENTER_X - right_offset * RIGHT_HALF_RANGE
    iris_y = IRIS_CENTER_Y + vert_offset * IRIS_VERT_HALF_RANGE

    # Head key points for PnP — fixed at original validated positions
    # (from test_visual_analysis.py). These are NOT the same as eye corner
    # landmarks used for gaze — PnP and gaze use different reference points.
    head: Dict[int, tuple] = {
        1:   (0.5, 0.5, 0.0),
        199: (0.5, 0.273, -0.1),
        33:  (0.379, 0.621, 0.1),    # PnP left eye reference
        263: (0.621, 0.621, 0.1),    # PnP right eye reference
        61:  (0.42, 0.393, -0.05),
        291: (0.58, 0.393, -0.05),
    }

    landmarks = []
    for i in range(478):
        if i in head:
            x, y, z = head[i]
        elif i == 133:
            x, y = LEFT_EYE_INNER; z = 0.0
        elif i == 362:
            x, y = RIGHT_EYE_INNER; z = 0.0
        elif i == 159:
            x, y = LEFT_EYE_TOP; z = 0.0
        elif i == 145:
            x, y = LEFT_EYE_BOTTOM; z = 0.0
        elif i == 386:
            x, y = RIGHT_EYE_TOP; z = 0.0
        elif i == 374:
            x, y = RIGHT_EYE_BOTTOM; z = 0.0
        elif i == 468:
            x, y = left_iris_x, iris_y; z = 0.0
        elif i == 473:
            x, y = right_iris_x, iris_y; z = 0.0
        else:
            x, y, z = 0.5, 0.5, 0.0
        landmarks.append(MockLandmark(x, y, z))
    return landmarks


# ============================================================
# Gaze Estimation Tests
# ============================================================


class TestComputeGazeDirection:

    def test_centered_gaze(self):
        """Iris centered in both eyes -> gaze angles near 0."""
        from modules.gaze_estimation import compute_gaze_direction

        landmarks = _build_face_landmarks(gaze_offset=0.0, vert_offset=0.0)
        gaze_x, gaze_y, confidence = compute_gaze_direction(landmarks, (480, 640))

        assert gaze_x is not None, "gaze_x should not be None"
        assert gaze_y is not None, "gaze_y should not be None"
        assert abs(gaze_x) < 5.0, f"Expected gaze_x ~ 0, got {gaze_x:.2f}"
        assert abs(gaze_y) < 5.0, f"Expected gaze_y ~ 0, got {gaze_y:.2f}"
        assert confidence >= 0.0

    def test_looking_left(self):
        """Iris shifted left (negative offset) -> negative gaze_x."""
        from modules.gaze_estimation import compute_gaze_direction

        landmarks = _build_face_landmarks(gaze_offset=-0.4, vert_offset=0.0)
        gaze_x, gaze_y, confidence = compute_gaze_direction(landmarks, (480, 640))

        assert gaze_x is not None
        assert gaze_x < -5.0, f"Expected negative gaze_x, got {gaze_x:.2f}"

    def test_looking_right(self):
        """Iris shifted right (positive offset) -> positive gaze_x."""
        from modules.gaze_estimation import compute_gaze_direction

        landmarks = _build_face_landmarks(gaze_offset=0.4, vert_offset=0.0)
        gaze_x, gaze_y, confidence = compute_gaze_direction(landmarks, (480, 640))

        assert gaze_x is not None
        assert gaze_x > 5.0, f"Expected positive gaze_x, got {gaze_x:.2f}"

    def test_looking_up(self):
        """Iris shifted up -> negative gaze_y."""
        from modules.gaze_estimation import compute_gaze_direction

        landmarks = _build_face_landmarks(gaze_offset=0.0, vert_offset=-0.4)
        gaze_x, gaze_y, confidence = compute_gaze_direction(landmarks, (480, 640))

        assert gaze_y is not None
        assert gaze_y < -5.0, f"Expected negative gaze_y, got {gaze_y:.2f}"

    def test_looking_down(self):
        """Iris shifted down -> positive gaze_y."""
        from modules.gaze_estimation import compute_gaze_direction

        landmarks = _build_face_landmarks(gaze_offset=0.0, vert_offset=0.4)
        gaze_x, gaze_y, confidence = compute_gaze_direction(landmarks, (480, 640))

        assert gaze_y is not None
        assert gaze_y > 5.0, f"Expected positive gaze_y, got {gaze_y:.2f}"

    def test_missing_landmarks_returns_none(self):
        """No iris landmarks -> (None, None, 0.0)."""
        from modules.gaze_estimation import compute_gaze_direction

        class Bad:
            pass

        landmarks = [Bad() for _ in range(10)]
        gaze_x, gaze_y, confidence = compute_gaze_direction(landmarks, (480, 640))

        assert gaze_x is None
        assert gaze_y is None
        assert confidence == 0.0

    def test_disagreeing_eyes_lower_confidence(self):
        """Opposite eye gaze -> lower confidence than agreeing gaze."""
        from modules.gaze_estimation import compute_gaze_direction

        agree = _build_face_landmarks(gaze_offset=0.0, disagree=False)
        disagree = _build_face_landmarks(gaze_offset=0.4, disagree=True)

        _, _, conf_a = compute_gaze_direction(agree, (480, 640))
        _, _, conf_d = compute_gaze_direction(disagree, (480, 640))

        assert conf_d < conf_a, (
            f"Expected disagreeing confidence ({conf_d}) < "
            f"agreeing confidence ({conf_a})"
        )


class TestGazeIsLookingAtCamera:

    def test_within_threshold(self):
        from modules.gaze_estimation import gaze_is_looking_at_camera
        assert gaze_is_looking_at_camera(5.0, 3.0, threshold=15.0) is True

    def test_outside_threshold(self):
        from modules.gaze_estimation import gaze_is_looking_at_camera
        assert gaze_is_looking_at_camera(20.0, 3.0, threshold=15.0) is False

    def test_none_angle(self):
        from modules.gaze_estimation import gaze_is_looking_at_camera
        assert gaze_is_looking_at_camera(None, 3.0, threshold=15.0) is False

    def test_custom_threshold(self):
        from modules.gaze_estimation import gaze_is_looking_at_camera
        assert gaze_is_looking_at_camera(12.0, 5.0, threshold=10.0) is False
        assert gaze_is_looking_at_camera(8.0, 5.0, threshold=10.0) is True


# ============================================================
# Eye Contact Enhanced Tests
# ============================================================


class TestHeadPose:

    def test_straight_face(self):
        """Forward-facing face -> yaw/pitch near 0 (tolerance ±5)."""
        from modules.eye_contact_enhanced import _compute_head_pose

        landmarks = _build_face_landmarks()
        yaw, pitch, roll = _compute_head_pose(landmarks, (480, 640))

        assert yaw is not None
        assert pitch is not None
        assert abs(yaw) < 5.0, f"Expected yaw ≈ 0°, got {yaw:.2f}°"
        assert abs(pitch) < 5.0, f"Expected pitch ≈ 0°, got {pitch:.2f}°"

    def test_head_pose_failure_returns_none(self):
        """Empty landmarks -> (None, None, None)."""
        from modules.eye_contact_enhanced import _compute_head_pose
        result = _compute_head_pose([], (480, 640))
        assert result == (None, None, None)


class TestCombinedScore:

    def test_head_only_when_gaze_unreliable(self):
        from modules.eye_contact_enhanced import _compute_combined_score
        looking, conf = _compute_combined_score(
            yaw=5.0, pitch=3.0,
            gaze_angle_x=50.0, gaze_angle_y=10.0,
            gaze_confidence=0.05,
        )
        assert looking is True
        assert conf > 0.0

    def test_both_agree_looking(self):
        from modules.eye_contact_enhanced import _compute_combined_score
        looking, conf = _compute_combined_score(
            yaw=5.0, pitch=3.0,
            gaze_angle_x=5.0, gaze_angle_y=3.0,
            gaze_confidence=0.8,
        )
        assert looking is True
        assert conf > 0.5

    def test_both_agree_not_looking(self):
        from modules.eye_contact_enhanced import _compute_combined_score
        looking, conf = _compute_combined_score(
            yaw=30.0, pitch=20.0,
            gaze_angle_x=40.0, gaze_angle_y=50.0,
            gaze_confidence=0.8,
        )
        assert looking is False

    def test_gaze_overrides_head(self):
        """Gaze says looking but head says not -> combined=True (gaze weight 0.65)."""
        from modules.eye_contact_enhanced import _compute_combined_score
        looking, conf = _compute_combined_score(
            yaw=20.0, pitch=5.0,
            gaze_angle_x=10.0, gaze_angle_y=5.0,
            gaze_confidence=0.8,
        )
        assert looking is True

    def test_head_none_falls_back_to_gaze(self):
        from modules.eye_contact_enhanced import _compute_combined_score
        looking, conf = _compute_combined_score(
            yaw=None, pitch=None,
            gaze_angle_x=5.0, gaze_angle_y=3.0,
            gaze_confidence=0.8,
        )
        assert looking is True
        assert conf == 0.8


class TestAnalyzeEyeContactEnhanced:

    def test_empty_frames(self):
        from modules.eye_contact_enhanced import analyze_eye_contact_enhanced
        result = analyze_eye_contact_enhanced([], None)
        assert result.contact_percentage == 0.0
        assert result.total_frames == 0
        assert result.contact_frames == 0
        assert result.frame_results == []

    def test_no_face_detected(self):
        """Frame with no face -> has_face=False, not looking."""
        from modules.eye_contact_enhanced import analyze_eye_contact_enhanced

        class MockResult:
            face_landmarks = None

        class MockMesh:
            def detect(self, image):
                return MockResult()

        frames = [np.zeros((480, 640, 3), dtype=np.uint8)]
        result = analyze_eye_contact_enhanced(frames, MockMesh())

        assert isinstance(result, EyeContactResult)
        assert result.total_frames == 1
        assert result.frame_results[0].has_face is False
        assert result.frame_results[0].looking_at_camera is False


class TestAnalyzeVisualEnhanced:

    def test_integration_returns_correct_types(self):
        from modules.eye_contact_enhanced import analyze_visual

        mock_eye_result = EyeContactResult(
            contact_percentage=80.0,
            total_frames=60,
            contact_frames=48,
            frame_results=[
                FrameEyeContact(
                    frame_index=0, has_face=True,
                    looking_at_camera=True, confidence=0.85,
                ),
            ],
        )
        mock_emotion_result = EmotionResult(
            dominant_emotion="neutral",
            emotion_distribution={"neutral": 0.6, "happy": 0.4},
            frames_analyzed=55,
        )

        with (
            patch("utils.helpers.load_mediapipe_face_mesh") as mock_load_mesh,
            patch("utils.helpers.load_deepface_model") as mock_load_df,
            patch("modules.eye_contact_enhanced.extract_keyframes") as mock_extract,
            patch("modules.eye_contact_enhanced.analyze_eye_contact_enhanced") as mock_eye,
            patch("modules.eye_contact_enhanced.analyze_emotions") as mock_emo,
        ):
            mock_extract.return_value = (
                [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(3)],
                [0, 1, 2],
            )
            mock_eye.return_value = mock_eye_result
            mock_emo.return_value = mock_emotion_result

            eye_result, emotion_result = analyze_visual("fake/path.mp4")

        assert isinstance(eye_result, EyeContactResult)
        assert isinstance(emotion_result, EmotionResult)
        assert eye_result.contact_percentage == 80.0
        assert eye_result.total_frames == 60
        assert emotion_result.dominant_emotion == "neutral"
        assert emotion_result.frames_analyzed == 55
        mock_load_mesh.assert_called_once()
        mock_load_df.assert_called_once()
        mock_extract.assert_called_once()
        mock_eye.assert_called_once()
        mock_emo.assert_called_once()

    def test_analyze_visual_empty_video(self):
        """Empty video returns empty results without error."""
        from modules.eye_contact_enhanced import analyze_visual

        with (
            patch("utils.helpers.load_mediapipe_face_mesh"),
            patch("utils.helpers.load_deepface_model"),
            patch("modules.eye_contact_enhanced.extract_keyframes") as mock_extract,
        ):
            mock_extract.return_value = ([], [])

            eye_result, emotion_result = analyze_visual("fake/empty.mp4")

        assert isinstance(eye_result, EyeContactResult)
        assert eye_result.total_frames == 0
        assert eye_result.contact_percentage == 0.0
        assert isinstance(emotion_result, EmotionResult)
        assert emotion_result.frames_analyzed == 0
        assert emotion_result.dominant_emotion == "uncertain"
