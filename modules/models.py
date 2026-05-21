"""Shared Pydantic data models for all pipeline stages.

All analysis stage models are defined here so each phase can import
from a single source of truth — no circular dependencies, no duplication.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class AudioExtractionResult(BaseModel):
    """Result of extracting audio from uploaded video."""
    audio_path: str
    duration_sec: float
    success: bool


class TranscriptionSegment(BaseModel):
    """A single timestamped segment from the transcript."""
    start: float
    end: float
    text: str


class TranscriptionResult(BaseModel):
    """Full transcription output from faster-whisper."""
    segments: List[TranscriptionSegment]
    full_text: str
    model_used: str
    duration_sec: float


class FillerWordCount(BaseModel):
    """Count of a specific filler word."""
    word: str
    count: int


class SpeechAnalysisResult(BaseModel):
    """Filler word frequency and speaking speed analysis."""
    filler_words: List[FillerWordCount]
    total_filler_count: int
    top_filler: Optional[str] = None
    wpm: float
    speed_classification: str
    total_words: int
    duration_minutes: float


class FrameEyeContact(BaseModel):
    """Eye contact result for a single video frame."""
    frame_index: int
    has_face: bool
    looking_at_camera: bool
    confidence: float


class EyeContactResult(BaseModel):
    """Aggregated eye contact analysis across sampled frames."""
    contact_percentage: float
    total_frames: int
    contact_frames: int
    frame_results: List[FrameEyeContact]


class EmotionScores(BaseModel):
    """Emotion probability distribution."""
    angry: float = 0.0
    disgust: float = 0.0
    fear: float = 0.0
    happy: float = 0.0
    sad: float = 0.0
    surprise: float = 0.0
    neutral: float = 0.0


class EmotionResult(BaseModel):
    """Dominant emotion and per-frame analysis results."""
    dominant_emotion: str
    emotion_distribution: Dict[str, float]
    frames_analyzed: int


class ConfidenceScores(BaseModel):
    """Weighted heuristic confidence score with component breakdown.

    Per D-08: All score fields defined from Phase 1 even though
    scoring implementation is Phase 5.
    """
    eye_contact_score: float = 0.0
    filler_score: float = 0.0
    pacing_score: float = 0.0
    emotion_score: float = 0.0
    clarity_score: float = 0.0
    composite: float = 0.0
    classification: str = "Needs Improvement"


class InterviewResult(BaseModel):
    """Top-level container for a complete interview analysis session."""
    interview_id: str
    created_at: datetime
    video_path: str
    duration_sec: float
    transcription: Optional[TranscriptionResult] = None
    speech_analysis: Optional[SpeechAnalysisResult] = None
    eye_contact: Optional[EyeContactResult] = None
    emotion: Optional[EmotionResult] = None
    confidence: Optional[ConfidenceScores] = None
    feedback: Optional[str] = None
