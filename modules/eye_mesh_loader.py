"""MediaPipe Face Mesh loader with video temporal processing.

Provides a FaceLandmarker initialized with RunningMode.VIDEO for
temporal tracking across video frames (equivalent to the legacy
static_image_mode=False behavior). Iris landmarks (478-point model)
are available by default with the face_landmarker.task model.

Suppresses detect() warnings about MODEL_COMPLEXITY and reframes
RunningMode.VIDEO as the temporal-tracking equivalent of the legacy
mp.solutions.face_mesh static_image_mode=False configuration.
"""

import time
from typing import Optional

import numpy as np

from mediapipe.tasks.python import vision


class VideoFaceLandmarkerWrapper:
    """Wraps Tasks FaceLandmarker in VIDEO mode for temporal tracking.

    Provides a .detect(mp_image) method (auto-assigning timestamps) that
    returns detection results with .face_landmarks, making it a drop-in
    replacement for IMAGE-mode FaceLandmarker.

    VIDEO mode provides frame-to-frame temporal context, reducing flickering
    in landmark predictions. Equivalent to the legacy static_image_mode=False.
    """

    def __init__(
        self,
        model_path: str,
        num_faces: int = 1,
        min_face_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        from mediapipe.tasks.python import BaseOptions

        base_options = BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_faces=num_faces,
            min_face_detection_confidence=min_face_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self._landmarker = vision.FaceLandmarker.create_from_options(options)
        self._timestamp_ms = 0

    def detect(self, mp_image):
        """Process a MediaPipe Image and return detection results.

        Auto-increments timestamps for VIDEO mode. First call gets
        timestamp=1, subsequent calls increment by 1.

        Args:
            mp_image: mediapipe.Image (SRGB format).

        Returns:
            Detection result with .face_landmarks matching Tasks API format.
        """
        self._timestamp_ms += 1
        try:
            return self._landmarker.detect_for_video(mp_image, self._timestamp_ms)
        except Exception:
            return type('EmptyResult', (), {'face_landmarks': None})()

    def close(self):
        """Release underlying resources."""
        if hasattr(self, '_landmarker') and self._landmarker is not None:
            self._landmarker.close()


def _get_model_path() -> str:
    """Resolve the face_landmarker.task model path, downloading if needed."""
    from pathlib import Path
    import urllib.request

    model_dir = Path(__file__).resolve().parent.parent / "models"
    model_path = model_dir / "face_landmarker.task"

    if not model_path.exists():
        model_dir.mkdir(parents=True, exist_ok=True)
        url = (
            "https://storage.googleapis.com/mediapipe-models/"
            "face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
        )
        urllib.request.urlretrieve(url, str(model_path))

    return str(model_path)


def load_video_face_mesh(
    min_detection_confidence: float = 0.5,
    min_tracking_confidence: float = 0.5,
) -> VideoFaceLandmarkerWrapper:
    """Load a MediaPipe Face Landmarker in VIDEO mode for temporal tracking.

    Uses the Tasks API with RunningMode.VIDEO, which provides frame-to-frame
    temporal context (equivalent to the legacy static_image_mode=False).

    The face_landmarker.task model outputs 478 landmarks including iris
    landmarks (indices 468-477, equivalent to refine_landmarks=True).

    Args:
        min_detection_confidence: Minimum confidence for face detection.
        min_tracking_confidence: Minimum confidence for landmark tracking.

    Returns:
        VideoFaceLandmarkerWrapper instance (drop-in for IMAGE FaceLandmarker).
    """
    model_path = _get_model_path()
    return VideoFaceLandmarkerWrapper(
        model_path=model_path,
        num_faces=1,
        min_face_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )
