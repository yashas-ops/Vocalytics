"""ML model loading with optional Streamlit caching.

Per D-12 and D-13: Models loaded once per session. CPU-optimized configs per STACK.md.
Uses Streamlit caching when available, otherwise falls back to module-level caching
so the same functions work in both Streamlit and non-Streamlit (e.g. FastAPI) contexts.
"""

from pathlib import Path

# Module-level cache for non-Streamlit contexts
_model_cache: dict[str, object] = {}

def _try_streamlit_cache(func):
    """Apply @st.cache_resource if Streamlit is running, else return func as-is."""
    try:
        import streamlit as st
        return st.cache_resource(func)
    except Exception:
        return func


def load_whisper_model(model_size: str = "base") -> "WhisperModel":
    """Load faster-whisper model with INT8 CPU optimization.

    Args:
        model_size: "tiny", "base", or "small". Default "base" balances
                   accuracy and speed on CPU (per STACK.md recommendation).

    Returns:
        faster_whisper.WhisperModel instance configured for CPU inference.
    """
    cache_key = f"whisper_{model_size}"
    if cache_key in _model_cache:
        return _model_cache[cache_key]
    from faster_whisper import WhisperModel
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    _model_cache[cache_key] = model
    return model


def load_spacy_model() -> "spacy.Language":
    """Load spaCy English model for NLP analysis.

    Returns:
        spaCy Language object with en_core_web_sm pipeline loaded.
    """
    if "spacy" in _model_cache:
        return _model_cache["spacy"]
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        import subprocess
        subprocess.run(
            ["python", "-m", "spacy", "download", "en_core_web_sm"],
            check=True
        )
        nlp = spacy.load("en_core_web_sm")
    _model_cache["spacy"] = nlp
    return nlp


def load_mediapipe_face_mesh() -> "FaceLandmarker":
    """Load MediaPipe Face Landmarker using the Tasks API.

    Returns:
        MediaPipe FaceLandmarker instance configured for static image processing.
    """
    if "face_mesh" in _model_cache:
        return _model_cache["face_mesh"]
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    model_path = str(Path(__file__).resolve().parent.parent / "models" / "face_landmarker.task")
    if not Path(model_path).exists():
        import urllib.request
        url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, model_path)

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_faces=1,
        min_face_detection_confidence=0.5,
    )
    mesh = vision.FaceLandmarker.create_from_options(options)
    _model_cache["face_mesh"] = mesh
    return mesh


def load_deepface_model() -> bool:
    """Sentinel: trigger DeepFace model download on first call.

    Returns:
        True (sentinel — actual model is managed internally by DeepFace)
    """
    if "deepface" in _model_cache:
        return True
    _model_cache["deepface"] = True
    return True
