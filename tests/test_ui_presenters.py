"""Unit tests for UI presentation helpers."""

from modules.models import ConfidenceScores, EmotionResult, EyeContactResult, SpeechAnalysisResult
from modules.ui_presenters import (
    build_history_label,
    get_component_breakdown,
    get_dashboard_highlights,
    get_eye_contact_summary,
    get_score_summary,
    get_score_tone,
    get_speed_summary,
)


def test_get_score_summary_uses_positive_copy_for_excellent_scores():
    summary = get_score_summary(88.0, "Excellent")

    assert summary["tone"] == "success"
    assert "88/100" in summary["body"]


def test_get_speed_summary_flags_fast_pacing():
    summary = get_speed_summary("fast", 188.0)

    assert summary["tone"] == "warning"
    assert "188 WPM" in summary["body"]


def test_get_eye_contact_summary_handles_missing_visual_analysis():
    summary = get_eye_contact_summary(None)

    assert summary["tone"] == "info"
    assert "unavailable" in summary["headline"].lower()


def test_build_history_label_uses_date_score_and_emotion():
    label = build_history_label(
        {"Date": "2026-05-16", "Score": "84/100", "Emotion": "Neutral"}
    )

    assert label == "2026-05-16 - 84/100 - Neutral"


def test_get_score_tone_maps_scores_to_restrained_states():
    assert get_score_tone(82.0) == "success"
    assert get_score_tone(67.0) == "warning"
    assert get_score_tone(45.0) == "error"


def test_get_component_breakdown_formats_component_bar_data():
    confidence = ConfidenceScores(
        eye_contact_score=88.2,
        filler_score=71.0,
        pacing_score=42.4,
        clarity_score=100.0,
        emotion_score=-10.0,
    )

    breakdown = get_component_breakdown(confidence)

    assert breakdown[0] == {
        "label": "Eye contact",
        "score": "88",
        "width": "88%",
        "tone": "success",
    }
    assert breakdown[2]["tone"] == "error"
    assert breakdown[3]["width"] == "100%"
    assert breakdown[4]["width"] == "0%"


def test_get_dashboard_highlights_prioritizes_actionable_signals():
    confidence = ConfidenceScores(composite=58.0, classification="Needs Improvement")
    speech = SpeechAnalysisResult(
        filler_words=[],
        total_filler_count=10,
        top_filler="um",
        wpm=184.0,
        speed_classification="fast",
        total_words=150,
        duration_minutes=1.2,
    )
    eye_contact = EyeContactResult(
        contact_percentage=35.0,
        total_frames=20,
        contact_frames=7,
        frame_results=[],
    )
    emotion = EmotionResult(
        dominant_emotion="neutral",
        emotion_distribution={"neutral": 0.8, "happy": 0.2},
        frames_analyzed=5,
    )

    highlights = get_dashboard_highlights(confidence, speech, eye_contact, emotion)

    assert len(highlights) == 4
    assert any(item["title"] == "Needs Improvement" for item in highlights)
    assert any("10 filler words" in item["body"] for item in highlights)
    assert any("184 WPM" in item["body"] for item in highlights)
    assert any("35%" in item["body"] for item in highlights)
