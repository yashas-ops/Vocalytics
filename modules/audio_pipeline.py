"""ffmpeg audio extraction: 16kHz mono WAV via subprocess. No moviepy. Per architecture."""

import subprocess
from pathlib import Path

import imageio_ffmpeg

from modules.models import AudioExtractionResult

_FFMPEG_PATH: str | None = None


def _get_ffmpeg() -> str:
    global _FFMPEG_PATH
    if _FFMPEG_PATH is None:
        _FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
    return _FFMPEG_PATH


def _get_ffprobe() -> str:
    return _get_ffmpeg().replace("ffmpeg", "ffprobe")


def extract_audio(video_path: str, temp_dir: str | None = None) -> AudioExtractionResult:
    """Extract 16kHz mono WAV audio from video using ffmpeg subprocess.

    Args:
        video_path: Path to the input video file.
        temp_dir: Directory for extracted audio. Defaults to project temp/.

    Returns:
        AudioExtractionResult with path, duration, and success status.
    """
    if temp_dir is None:
        temp_dir = str(Path(__file__).resolve().parent.parent / "temp")

    video_stem = Path(video_path).stem
    audio_path = str(Path(temp_dir) / f"{video_stem}_audio.wav")

    try:
        result = subprocess.run(
            [
                _get_ffmpeg(), "-i", video_path,
                "-vn", "-acodec", "pcm_s16le",
                "-ar", "16000", "-ac", "1",
                "-y", audio_path,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        if result.returncode != 0:
            return AudioExtractionResult(
                audio_path="", duration_sec=0.0, success=False
            )

        duration = _get_duration(video_path)
        return AudioExtractionResult(
            audio_path=audio_path, duration_sec=duration, success=True
        )

    except FileNotFoundError:
        raise FileNotFoundError(
            f"ffmpeg not found at {_get_ffmpeg()}. The bundled binary may be missing."
        )


def _get_duration(video_path: str) -> float:
    """Get video duration in seconds via ffprobe.

    Args:
        video_path: Path to the video file.

    Returns:
        Duration in seconds, or 0.0 on failure.
    """
    try:
        result = subprocess.run(
            [
                _get_ffprobe(), "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return float(result.stdout.strip())
    except (ValueError, FileNotFoundError):
        return 0.0
