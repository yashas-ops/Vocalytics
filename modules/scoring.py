"""Scoring engine: confidence scoring and template-based feedback generation.

Provides two public functions:
    - compute_confidence: Weighted heuristic confidence score (0-100) with
      per-component breakdown and classification.
    - generate_feedback: Deterministic template-based feedback report with
      strengths, weaknesses, and improvement tips.

All scoring is purely mathematical — no ML models, no LLM calls.
"""

from modules.models import ConfidenceScores

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXCELLENT_THRESHOLD = 80.0
GOOD_THRESHOLD = 60.0

WEIGHTS = {
    "eye_contact": 0.30,
    "filler": 0.25,
    "pacing": 0.20,
    "clarity": 0.15,
    "emotion": 0.10,
}

EMOTION_SCORES = {
    "happy": 100,
    "neutral": 80,
    "surprise": 70,
    "sad": 40,
    "angry": 30,
    "fear": 20,
    "disgust": 10,
    "uncertain": 50,
}

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def calc_filler_rate(total_filler_count: int, total_words: int) -> float:
    """Calculate filler word rate per 100 words.

    Args:
        total_filler_count: Total number of filler words detected.
        total_words: Total number of words spoken.

    Returns:
        Filler rate per 100 words. Returns 0.0 if total_words <= 0
        to avoid division by zero.
    """
    if total_words <= 0:
        return 0.0
    return (total_filler_count / total_words) * 100.0


# ---------------------------------------------------------------------------
# Component scoring helpers
# ---------------------------------------------------------------------------


def _score_eye_contact(eye_contact_pct: float) -> float:
    """Score eye contact — maps directly from percentage (0-100)."""
    return max(0.0, min(100.0, eye_contact_pct))


def _score_filler(filler_rate_per_100: float) -> float:
    """Score filler word usage — inverse linear from rate.

    filler_rate=0 → 100, filler_rate=10 → 0, clamped to 0-100.
    """
    score = 100.0 - filler_rate_per_100 * 10.0
    return max(0.0, min(100.0, score))


def _score_pacing(wpm: float, speed_classification: str) -> float:
    """Score speaking pace based on speed classification and WPM.

    - 'good': 100 always
    - 'slow': linear from 100 at 110 WPM to 0 at 50 WPM
    - 'fast': linear from 100 at 160 WPM to 0 at 240 WPM
    """
    if speed_classification == "good":
        return 100.0

    if speed_classification == "slow":
        # Linear: 110 WPM → 100, 50 WPM → 0
        score = ((wpm - 50.0) / (110.0 - 50.0)) * 100.0
        return max(0.0, min(100.0, score))

    if speed_classification == "fast":
        # Linear: 160 WPM → 100, 240 WPM → 0
        score = ((240.0 - wpm) / (240.0 - 160.0)) * 100.0
        return max(0.0, min(100.0, score))

    # Fallback for unknown classification
    return 0.0


def _score_clarity(wpm: float) -> float:
    """Score speaking clarity based on distance from ideal pace (135 WPM).

    At 135 WPM → 100, at 100 WPM → 65, at 60 WPM → 25.
    """
    score = 100.0 - abs(wpm - 135.0) * 1.0
    return max(0.0, min(100.0, score))


def _score_emotion(dominant_emotion: str) -> float:
    """Map dominant emotion to a score.

    Case-insensitive. Unknown emotions fall back to 'uncertain' → 50.
    """
    emotion_lower = dominant_emotion.lower().strip()
    return float(EMOTION_SCORES.get(emotion_lower, EMOTION_SCORES["uncertain"]))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compute_confidence(
    eye_contact_pct: float,
    filler_rate_per_100: float,
    wpm: float,
    speed_classification: str,
    dominant_emotion: str,
) -> ConfidenceScores:
    """Compute a weighted confidence score (0-100) with component breakdown.

    Combines five components into a single confidence score using weighted
    heuristic per D-03. Classifies the composite score per D-02 thresholds.

    Args:
        eye_contact_pct: Percentage of frames with eye contact (0-100).
        filler_rate_per_100: Filler word rate per 100 words.
        wpm: Words per minute speaking speed.
        speed_classification: One of "slow", "good", or "fast".
        dominant_emotion: Detected dominant emotion label.

    Returns:
        ConfidenceScores with all component scores, composite (0-100,
        rounded to 1 decimal), and classification string.
    """
    eye_contact_score = _score_eye_contact(eye_contact_pct)
    filler_score = _score_filler(filler_rate_per_100)
    pacing_score = _score_pacing(wpm, speed_classification)
    clarity_score = _score_clarity(wpm)
    emotion_score = _score_emotion(dominant_emotion)

    composite = (
        eye_contact_score * WEIGHTS["eye_contact"]
        + filler_score * WEIGHTS["filler"]
        + pacing_score * WEIGHTS["pacing"]
        + clarity_score * WEIGHTS["clarity"]
        + emotion_score * WEIGHTS["emotion"]
    )
    composite = round(composite, 1)

    # Classification thresholds per D-02
    if composite >= EXCELLENT_THRESHOLD:
        classification = "Excellent"
    elif composite >= GOOD_THRESHOLD:
        classification = "Good"
    else:
        classification = "Needs Improvement"

    return ConfidenceScores(
        eye_contact_score=eye_contact_score,
        filler_score=filler_score,
        pacing_score=pacing_score,
        clarity_score=clarity_score,
        emotion_score=emotion_score,
        composite=composite,
        classification=classification,
    )
