"""Unit tests for visual analysis module — keyframe extraction, eye contact, emotion.

Tests follow TDD pattern:
- extract_keyframes tests use synthetic video files
- _compute_head_pose tests use mock MediaPipe landmarks
- check_eye_contact tests are pure logic
- _aggregate_emotions tests use mock DeepFace results
- analyze_visual integration test mocks sub-functions
"""

import os
import tempfile
from typing import Dict, List, Tuple
from unittest.mock import patch

import cv2
import numpy as np
import pytest
from modules.models import EmotionResult, EyeContactResult, FrameEyeContact


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="module")
def _synthetic_video_path():
    """Create a synthetic video file for keyframe extraction tests.

    5 fps, 10 seconds, 1920x1080 = 50 frames total.
    max_frames=20 → interval = max(1, 50//20) = 2 → 20 frames at indices 0,2,4,...,38.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    tmp.close()
    fps = 5
    duration_sec = 10
    width, height = 1920, 1080
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(tmp.name, fourcc, fps, (width, height))
    for _ in range(duration_sec * fps):
        frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        out.write(frame)
    out.release()
    yield tmp.name
    os.unlink(tmp.name)


# ============================================================
# Test 1: extract_keyframes returns correct frame count
# ============================================================

def test_extract_keyframes_count(_synthetic_video_path):
    """Extract with max_frames=20 from a 50-frame video → ~20 frames."""
    from modules.visual_analysis import extract_keyframes

    frames, indices = extract_keyframes(_synthetic_video_path, max_frames=20)

    assert len(frames) <= 20, f"Expected ≤20 frames, got {len(frames)}"
    assert len(frames) > 0, "Expected at least 1 frame"
    assert len(frames) == len(indices), \
        f"Frames ({len(frames)}) and indices ({len(indices)}) count mismatch"


# ============================================================
# Test 2: extract_keyframes downsamples to 640x480
# ============================================================

def test_extract_keyframes_dimensions(_synthetic_video_path):
    """Frames from a 1920x1080 video should be downscaled to 640x480."""
    from modules.visual_analysis import extract_keyframes

    frames, _ = extract_keyframes(_synthetic_video_path, max_frames=20)

    for i, frame in enumerate(frames):
        assert frame.shape == (480, 640, 3), \
            f"Frame {i}: expected shape (480, 640, 3), got {frame.shape}"


# ============================================================
# Test 3: extract_keyframes handles missing video gracefully
# ============================================================

def test_extract_keyframes_missing_video():
    """Non-existent path should return empty lists without crashing."""
    from modules.visual_analysis import extract_keyframes

    frames, indices = extract_keyframes("/nonexistent/video.mp4", max_frames=20)

    assert frames == [], f"Expected empty list, got {len(frames)} frames"
    assert indices == [], f"Expected empty list, got {len(indices)} indices"


# ============================================================
# Helper: build mock MediaPipe landmarks for head pose tests
# ============================================================

class MockLandmark:
    """Simulates a MediaPipe NormalizedLandmark with x, y, z attributes."""
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


def _build_straight_face_landmarks() -> list:
    """Build 478 mock landmarks simulating a forward-facing face.

    Key points (indices 1, 199, 33, 263, 61, 291) are positioned
    as they would be for a straight-on face in normalized coords.
    """
    # Key landmark positions for a forward-facing face (normalized 0-1)
    key_positions = {
        1:   (0.5, 0.4, 0.0),    # Nose tip
        199: (0.5, 0.7, 0.0),    # Chin
        33:  (0.35, 0.35, 0.0),  # Left eye left corner
        263: (0.65, 0.35, 0.0),  # Right eye right corner
        61:  (0.38, 0.55, 0.0),  # Left mouth corner
        291: (0.62, 0.55, 0.0),  # Right mouth corner
    }

    landmarks = []
    for i in range(478):
        if i in key_positions:
            x, y, z = key_positions[i]
        else:
            x, y, z = 0.5, 0.5, 0.0
        landmarks.append(MockLandmark(x, y, z))
    return landmarks


# ============================================================
# Test 4: _compute_head_pose with straight-on face
# ============================================================

def test_compute_head_pose_straight():
    """Straight-on face should produce yaw ≈ 0°, pitch ≈ 0° (tolerance ±5°)."""
    from modules.visual_analysis import _compute_head_pose

    landmarks = _build_straight_face_landmarks()
    yaw, pitch, roll = _compute_head_pose(landmarks, (480, 640))

    assert yaw is not None, "yaw should not be None"
    assert pitch is not None, "pitch should not be None"
    assert abs(yaw) < 5.0, f"Expected yaw ≈ 0°, got {yaw:.2f}°"
    assert abs(pitch) < 5.0, f"Expected pitch ≈ 0°, got {pitch:.2f}°"


# ============================================================
# Test 5: check_eye_contact within bounds
# ============================================================

def test_check_eye_contact_within_bounds():
    """yaw=5, pitch=3 → True (within ±15° yaw, ±10° pitch)."""
    from modules.visual_analysis import check_eye_contact

    result = check_eye_contact(5.0, 3.0, 0.0)
    assert result is True, f"Expected True, got {result}"


# ============================================================
# Test 6: check_eye_contact outside yaw threshold
# ============================================================

def test_check_eye_contact_outside_yaw():
    """yaw=20, pitch=3 → False (yaw exceeds ±15°)."""
    from modules.visual_analysis import check_eye_contact

    result = check_eye_contact(20.0, 3.0, 0.0)
    assert result is False, f"Expected False, got {result}"


# ============================================================
# Test 7: check_eye_contact outside pitch threshold
# ============================================================

def test_check_eye_contact_outside_pitch():
    """yaw=5, pitch=15 → False (pitch exceeds ±10°)."""
    from modules.visual_analysis import check_eye_contact

    result = check_eye_contact(5.0, 15.0, 0.0)
    assert result is False, f"Expected False, got {result}"


# ============================================================
# Test 8: Emotion soft voting produces correct distribution
# ============================================================

def test_emotion_soft_voting():
    """Soft voting across 3 frames should produce correct frequency distribution."""
    from modules.visual_analysis import _aggregate_emotions

    mock_results: List[Dict] = [
        {"emotion": {"angry": 0.1, "happy": 0.8, "neutral": 0.1},
         "dominant_emotion": "happy"},
        {"emotion": {"angry": 0.1, "happy": 0.7, "neutral": 0.2},
         "dominant_emotion": "happy"},
        {"emotion": {"angry": 0.3, "happy": 0.1, "neutral": 0.6},
         "dominant_emotion": "neutral"},
    ]

    dominant, distribution = _aggregate_emotions(mock_results)

    assert dominant == "happy", f"Expected 'happy', got '{dominant}'"
    assert abs(distribution.get("happy", 0) - 2.0 / 3.0) < 0.01, \
        f"Expected happy ≈ 0.667, got {distribution.get('happy', 0)}"
    assert abs(distribution.get("neutral", 0) - 1.0 / 3.0) < 0.01, \
        f"Expected neutral ≈ 0.333, got {distribution.get('neutral', 0)}"


# ============================================================
# Test 9: Emotion confidence threshold excludes low-confidence frames
# ============================================================

def test_emotion_confidence_threshold():
    """Frames where dominant emotion confidence ≤ 50% should be excluded."""
    from modules.visual_analysis import _aggregate_emotions

    mock_results: List[Dict] = [
        {"emotion": {"angry": 0.1, "happy": 0.8, "neutral": 0.1},
         "dominant_emotion": "happy"},
        # "neutral" at 40% confidence — below 50% threshold, should be excluded
        {"emotion": {"angry": 0.3, "fear": 0.3, "neutral": 0.4},
         "dominant_emotion": "neutral"},
    ]

    dominant, distribution = _aggregate_emotions(mock_results)

    # Only "happy" frame should remain (neutral excluded by threshold)
    assert dominant == "happy", f"Expected 'happy', got '{dominant}'"
    assert abs(distribution.get("happy", 0) - 1.0) < 0.01, \
        f"Expected happy = 1.0, got {distribution.get('happy', 0)}"
    # Neutral should be absent or 0 from distribution
    assert distribution.get("neutral", 0) == 0.0, \
        "Neutral should not appear (below 50% confidence)"


# ============================================================
# Test 10: analyze_visual integration returns correct types
# ============================================================

def test_analyze_visual_integration():
    """verify analyze_visual returns (EyeContactResult, EmotionResult) with mock sub-functions."""
    from modules.visual_analysis import analyze_visual

    mock_eye_result = EyeContactResult(
        contact_percentage=75.0,
        total_frames=20,
        contact_frames=15,
        frame_results=[
            FrameEyeContact(frame_index=0, has_face=True, looking_at_camera=True, confidence=0.85),
            FrameEyeContact(frame_index=15, has_face=True, looking_at_camera=False, confidence=0.3),
        ],
    )
    mock_emotion_result = EmotionResult(
        dominant_emotion="neutral",
        emotion_distribution={"neutral": 0.6, "happy": 0.3, "surprise": 0.1},
        frames_analyzed=18,
    )

    with (
        patch("modules.visual_analysis.load_mediapipe_face_mesh") as mock_load_mesh,
        patch("modules.visual_analysis.load_deepface_model") as mock_load_df,
        patch("modules.visual_analysis.extract_keyframes") as mock_extract,
        patch("modules.visual_analysis.analyze_eye_contact") as mock_eye,
        patch("modules.visual_analysis.analyze_emotions") as mock_emo,
    ):
        mock_extract.return_value = (
            [np.zeros((480, 640, 3), dtype=np.uint8)],
            [0],
        )
        mock_eye.return_value = mock_eye_result
        mock_emo.return_value = mock_emotion_result

        eye_result, emotion_result = analyze_visual("fake/path.mp4")

    assert isinstance(eye_result, EyeContactResult), \
        f"Expected EyeContactResult, got {type(eye_result)}"
    assert isinstance(emotion_result, EmotionResult), \
        f"Expected EmotionResult, got {type(emotion_result)}"

    assert eye_result.contact_percentage == 75.0
    assert eye_result.total_frames == 20
    assert eye_result.contact_frames == 15
    assert len(eye_result.frame_results) == 2

    assert emotion_result.dominant_emotion == "neutral"
    assert emotion_result.frames_analyzed == 18
    assert abs(emotion_result.emotion_distribution["neutral"] - 0.6) < 0.01

    mock_load_mesh.assert_called_once()
    mock_load_df.assert_called_once()
    mock_extract.assert_called_once_with("fake/path.mp4", max_frames=20)
    mock_eye.assert_called_once()
    mock_emo.assert_called_once()
