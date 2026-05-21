"""faster-whisper transcription: INT8 CPU, timestamped segments. Uses cached model from utils/helpers."""

from modules.models import TranscriptionResult, TranscriptionSegment
from utils.helpers import load_whisper_model


def transcribe_audio(audio_path: str, model_size: str = "base") -> TranscriptionResult:
    """Transcribe audio using faster-whisper with INT8 CPU optimization.

    Args:
        audio_path: Path to audio file (16kHz mono WAV).
        model_size: Whisper model size ("tiny", "base", or "small").

    Returns:
        TranscriptionResult with segments, full text, and model info.
    """
    model = load_whisper_model(model_size)
    segments_generator, info = model.transcribe(audio_path, beam_size=1)

    segments_list = []
    text_parts = []

    for seg in segments_generator:
        segments_list.append(
            TranscriptionSegment(start=seg.start, end=seg.end, text=seg.text.strip())
        )
        text_parts.append(seg.text.strip())

    if not segments_list:
        return TranscriptionResult(
            segments=[], full_text="", model_used=model_size, duration_sec=0.0
        )

    duration_sec = segments_list[-1].end
    full_text = " ".join(text_parts)

    return TranscriptionResult(
        segments=segments_list,
        full_text=full_text,
        model_used=model_size,
        duration_sec=duration_sec,
    )
