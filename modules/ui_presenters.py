"""Presentation helpers for the Streamlit interface.

These functions keep UI-specific copy and state mapping out of the
main application flow so visual refinements can be tested safely.
"""

from __future__ import annotations

from typing import Any


def get_score_summary(score: float, classification: str) -> dict[str, str]:
    """Return a tone and summary copy for the top-level confidence score."""
    normalized = classification.strip().lower()

    if normalized == "excellent":
        return {
            "tone": "success",
            "headline": "Excellent momentum",
            "body": (
                f"Your latest session landed at {score:.0f}/100. "
                "Keep reinforcing the habits that already feel natural."
            ),
        }

    if normalized == "good":
        return {
            "tone": "warning",
            "headline": "Strong base to build on",
            "body": (
                f"You are sitting at {score:.0f}/100. A few targeted tweaks "
                "should noticeably improve your delivery."
            ),
        }

    return {
        "tone": "error",
        "headline": "Clear improvement opportunity",
        "body": (
            f"This session scored {score:.0f}/100. Focus on one or two weak "
            "signals first and the overall score should move quickly."
        ),
    }


def get_speed_summary(speed_classification: str, wpm: float) -> dict[str, str]:
    """Return user-facing pacing guidance."""
    normalized = speed_classification.strip().lower()

    if normalized == "good":
        return {
            "tone": "success",
            "headline": "Pacing is in a healthy range",
            "body": f"At {wpm:.0f} WPM, your delivery should feel steady and easy to follow.",
        }

    if normalized == "fast":
        return {
            "tone": "warning",
            "headline": "You are rushing key points",
            "body": f"At {wpm:.0f} WPM, adding short pauses will improve clarity and confidence.",
        }

    return {
        "tone": "warning",
        "headline": "You can be more conversational",
        "body": f"At {wpm:.0f} WPM, a slightly quicker cadence should help the answer feel sharper.",
    }


def get_eye_contact_summary(contact_percentage: float | None) -> dict[str, str]:
    """Return user-facing eye-contact guidance."""
    if contact_percentage is None:
        return {
            "tone": "info",
            "headline": "Visual analysis unavailable",
            "body": "No camera-based eye contact reading was captured for this session.",
        }

    if contact_percentage >= 70:
        return {
            "tone": "success",
            "headline": "Eye contact looks steady",
            "body": f"You stayed camera-aligned for {contact_percentage:.0f}% of sampled frames.",
        }

    if contact_percentage >= 40:
        return {
            "tone": "warning",
            "headline": "Eye contact is mixed",
            "body": f"You were camera-aligned for {contact_percentage:.0f}% of sampled frames.",
        }

    return {
        "tone": "error",
        "headline": "Eye contact needs attention",
        "body": f"Only {contact_percentage:.0f}% of sampled frames showed camera-facing eye contact.",
    }


def build_history_label(record: dict[str, Any]) -> str:
    """Build a readable label for history selection controls."""
    date = record.get("Date") or "Unknown date"
    score = record.get("Score") or "No score"
    emotion = record.get("Emotion") or "Unknown emotion"
    return f"{date} - {score} - {emotion}"


def get_score_tone(score: float) -> str:
    """Map a numeric score to a restrained semantic tone."""
    if score >= 80:
        return "success"
    if score >= 60:
        return "warning"
    return "error"


def get_component_breakdown(confidence: Any) -> list[dict[str, str]]:
    """Build display data for the confidence component bars."""
    components = [
        ("Eye contact", confidence.eye_contact_score),
        ("Filler control", confidence.filler_score),
        ("Pacing", confidence.pacing_score),
        ("Clarity", confidence.clarity_score),
        ("Expression", confidence.emotion_score),
    ]

    return [
        {
            "label": label,
            "score": f"{score:.0f}",
            "width": f"{max(0.0, min(100.0, score)):.0f}%",
            "tone": get_score_tone(score),
        }
        for label, score in components
    ]


def get_dashboard_highlights(
    confidence: Any | None,
    speech: Any | None,
    eye_contact: Any | None,
    emotion: Any | None,
) -> list[dict[str, str]]:
    """Build a short list of key takeaways for the dashboard overview."""
    highlights: list[dict[str, str]] = []

    if confidence is not None:
        highlights.append(
            {
                "tone": get_score_tone(confidence.composite),
                "label": "Overall",
                "title": confidence.classification,
                "body": f"Composite confidence score: {confidence.composite:.0f}/100.",
            }
        )

    if speech is not None:
        if speech.total_filler_count == 0:
            highlights.append(
                {
                    "tone": "success",
                    "label": "Speech",
                    "title": "Clean delivery",
                    "body": "No filler words were detected in this session.",
                }
            )
        elif speech.total_filler_count >= 8:
            highlights.append(
                {
                    "tone": "warning",
                    "label": "Speech",
                    "title": "Filler words are visible",
                    "body": f"{speech.total_filler_count} filler words were detected across the answer.",
                }
            )

        if speech.speed_classification != "good":
            highlights.append(
                {
                    "tone": "warning",
                    "label": "Pacing",
                    "title": speech.speed_classification.capitalize(),
                    "body": f"Speaking speed landed at {speech.wpm:.0f} WPM.",
                }
            )
        else:
            highlights.append(
                {
                    "tone": "success",
                    "label": "Pacing",
                    "title": "Well paced",
                    "body": f"Speaking speed landed at {speech.wpm:.0f} WPM.",
                }
            )

    if eye_contact is not None:
        tone = "success" if eye_contact.contact_percentage >= 70 else "warning"
        if eye_contact.contact_percentage < 40:
            tone = "error"
        highlights.append(
            {
                "tone": tone,
                "label": "Presence",
                "title": "Eye contact",
                "body": f"Camera-facing eye contact measured {eye_contact.contact_percentage:.0f}%.",
            }
        )

    if emotion is not None and emotion.dominant_emotion:
        highlights.append(
            {
                "tone": "info",
                "label": "Expression",
                "title": emotion.dominant_emotion.capitalize(),
                "body": f"Dominant expression across sampled frames: {emotion.dominant_emotion}.",
            }
        )

    return highlights[:4]
