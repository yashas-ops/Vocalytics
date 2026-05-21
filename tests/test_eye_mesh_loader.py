"""Unit tests for eye_mesh_loader module.

The VideoFaceLandmarkerWrapper creates a real MediaPipe model,
so these tests use mocking to avoid requiring the model file.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest


class TestVideoFaceLandmarkerWrapper:

    def test_detect_returns_result_with_face_landmarks(self):
        """detect() should return an object with .face_landmarks on success."""
        from modules.eye_mesh_loader import VideoFaceLandmarkerWrapper

        mock_result = MagicMock()
        mock_result.face_landmarks = [MagicMock()]

        with patch(
            "modules.eye_mesh_loader.vision.FaceLandmarker.create_from_options"
        ) as mock_create:
            mock_landmarker = MagicMock()
            mock_landmarker.detect_for_video.return_value = mock_result
            mock_create.return_value = mock_landmarker

            wrapper = VideoFaceLandmarkerWrapper("fake_model_path")
            result = wrapper.detect(MagicMock())

            assert result.face_landmarks is not None
            assert len(result.face_landmarks) == 1

    def test_detect_handles_exception_gracefully(self):
        """If detect_for_video raises, should return empty result."""
        from modules.eye_mesh_loader import VideoFaceLandmarkerWrapper

        with patch(
            "modules.eye_mesh_loader.vision.FaceLandmarker.create_from_options"
        ) as mock_create:
            mock_landmarker = MagicMock()
            mock_landmarker.detect_for_video.side_effect = RuntimeError("Model error")
            mock_create.return_value = mock_landmarker

            wrapper = VideoFaceLandmarkerWrapper("fake_model_path")
            result = wrapper.detect(MagicMock())

            assert result.face_landmarks is None

    def test_detect_increments_timestamp(self):
        """Each detection call should increment the internal timestamp."""
        from modules.eye_mesh_loader import VideoFaceLandmarkerWrapper

        mock_result = MagicMock()
        mock_result.face_landmarks = [MagicMock()]

        with patch(
            "modules.eye_mesh_loader.vision.FaceLandmarker.create_from_options"
        ) as mock_create:
            mock_landmarker = MagicMock()
            mock_landmarker.detect_for_video.return_value = mock_result
            mock_create.return_value = mock_landmarker

            wrapper = VideoFaceLandmarkerWrapper("fake_model_path")

            wrapper.detect(MagicMock())
            assert wrapper._timestamp_ms == 1

            wrapper.detect(MagicMock())
            assert wrapper._timestamp_ms == 2

            wrapper.detect(MagicMock())
            assert wrapper._timestamp_ms == 3

    def test_close_releases_resources(self):
        """close() should call the underlying landmarker's close()."""
        from modules.eye_mesh_loader import VideoFaceLandmarkerWrapper

        with patch(
            "modules.eye_mesh_loader.vision.FaceLandmarker.create_from_options"
        ) as mock_create:
            mock_landmarker = MagicMock()
            mock_create.return_value = mock_landmarker

            wrapper = VideoFaceLandmarkerWrapper("fake_model_path")
            wrapper.close()

            mock_landmarker.close.assert_called_once()

    def test_close_handles_none(self):
        """close() should not fail if _landmarker is None."""
        from modules.eye_mesh_loader import VideoFaceLandmarkerWrapper

        wrapper = VideoFaceLandmarkerWrapper.__new__(VideoFaceLandmarkerWrapper)
        wrapper._landmarker = None
        wrapper.close()  # should not raise


class TestLoadVideoFaceMesh:

    def test_load_video_face_mesh_returns_wrapper(self):
        """load_video_face_mesh should return a VideoFaceLandmarkerWrapper."""
        from modules.eye_mesh_loader import load_video_face_mesh

        with patch(
            "modules.eye_mesh_loader._get_model_path"
        ) as mock_path, patch(
            "modules.eye_mesh_loader.vision.FaceLandmarker.create_from_options"
        ):
            mock_path.return_value = "fake_model_path"

            wrapper = load_video_face_mesh()
            assert wrapper is not None
            assert hasattr(wrapper, "detect")
            assert hasattr(wrapper, "close")
