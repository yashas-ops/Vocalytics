"""Unit tests for scoring module — confidence scoring and feedback generation.

Tests follow TDD pattern:
- compute_confidence tests cover all component scoring rules
- generate_feedback tests cover template structure and edge cases
- All tests are pure logic (no ML model dependencies)
"""

import pytest
from modules.models import ConfidenceScores


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def perfect_inputs():
    """All metrics at ideal values — expects composite = 100, Excellent."""
    return {
        "eye_contact_pct": 100.0,
        "filler_rate_per_100": 0.0,
        "wpm": 135.0,
        "speed_classification": "good",
        "dominant_emotion": "happy",
    }


@pytest.fixture
def zero_inputs():
    """All metrics at minimum — expects composite ≈ 1.0, Needs Improvement."""
    return {
        "eye_contact_pct": 0.0,
        "filler_rate_per_100": 15.0,
        "wpm": 240.0,
        "speed_classification": "fast",
        "dominant_emotion": "disgust",  # disgust=10 → weight 0.10 → min composite ≠ 0 exactly
    }


# ============================================================
# Scoring Tests: compute_confidence()
# ============================================================

class TestComputeConfidence:
    """Test suite for compute_confidence."""

    # ----- Threshold tests -----

    def test_perfect_scores(self, perfect_inputs):
        """All metrics ideal -> composite = 100, Excellent."""
        from modules.scoring import compute_confidence

        result = compute_confidence(**perfect_inputs)

        assert isinstance(result, ConfidenceScores)
        assert result.composite == 100.0, \
            f"Expected composite = 100.0, got {result.composite}"
        assert result.classification == "Excellent", \
            f"Expected 'Excellent', got '{result.classification}'"

    def test_zero_scores(self, zero_inputs):
        """All metrics poor -> composite near 0, Needs Improvement."""
        from modules.scoring import compute_confidence

        result = compute_confidence(**zero_inputs)

        # Minimum possible composite: disgust=10 * 0.10 = 1.0, everything else 0
        assert result.composite < 5.0, \
            f"Expected composite near 0, got {result.composite}"
        assert result.classification == "Needs Improvement", \
            f"Expected 'Needs Improvement', got '{result.classification}'"

    def test_excellent_threshold(self):
        """composite >= 80 -> Excellent."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=90.0,
            filler_rate_per_100=0.5,
            wpm=130.0,
            speed_classification="good",
            dominant_emotion="happy",
        )

        assert result.composite >= 80.0, \
            f"Expected composite >= 80, got {result.composite}"
        assert result.classification == "Excellent", \
            f"Expected 'Excellent', got '{result.classification}'"

    def test_good_threshold(self):
        """composite 60-79 -> Good."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=60.0,
            filler_rate_per_100=4.0,
            wpm=120.0,
            speed_classification="good",
            dominant_emotion="neutral",
        )

        assert 60.0 <= result.composite < 80.0, \
            f"Expected composite in [60, 80), got {result.composite}"
        assert result.classification == "Good", \
            f"Expected 'Good', got '{result.classification}'"

    def test_needs_improvement_threshold(self):
        """composite < 60 -> Needs Improvement."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=30.0,
            filler_rate_per_100=8.0,
            wpm=180.0,
            speed_classification="fast",
            dominant_emotion="sad",
        )

        assert result.composite < 60.0, \
            f"Expected composite < 60, got {result.composite}"
        assert result.classification == "Needs Improvement", \
            f"Expected 'Needs Improvement', got '{result.classification}'"

    # ----- Component score tests -----

    def test_eye_contact_score_direct(self):
        """eye_contact_pct maps 1:1 to eye_contact_score (clamped 0-100)."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=75.0,
            filler_rate_per_100=5.0,
            wpm=135.0,
            speed_classification="good",
            dominant_emotion="neutral",
        )

        assert result.eye_contact_score == 75.0, \
            f"Expected eye_contact_score = 75.0, got {result.eye_contact_score}"

    def test_eye_contact_score_clamped(self):
        """eye_contact_pct > 100 should be clamped to 100."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=150.0,
            filler_rate_per_100=5.0,
            wpm=135.0,
            speed_classification="good",
            dominant_emotion="neutral",
        )

        assert result.eye_contact_score == 100.0, \
            f"Expected eye_contact_score = 100.0, got {result.eye_contact_score}"

    def test_filler_score_zero_rate(self):
        """filler_rate=0 -> filler_score=100."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=0.0,
            wpm=135.0,
            speed_classification="good",
            dominant_emotion="neutral",
        )

        assert result.filler_score == 100.0, \
            f"Expected filler_score = 100.0, got {result.filler_score}"

    def test_filler_score_high_rate(self):
        """filler_rate >= 10 -> filler_score=0 (clamped)."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=10.0,
            wpm=135.0,
            speed_classification="good",
            dominant_emotion="neutral",
        )

        assert result.filler_score == 0.0, \
            f"Expected filler_score = 0.0, got {result.filler_score}"

    def test_filler_score_above_ten(self):
        """filler_rate > 10 -> filler_score=0 (clamped)."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=12.0,
            wpm=135.0,
            speed_classification="good",
            dominant_emotion="neutral",
        )

        assert result.filler_score == 0.0, \
            f"Expected filler_score = 0.0, got {result.filler_score}"

    def test_filler_score_linear(self):
        """filler_rate=5 -> filler_score=50 (100 - 5*10 = 50)."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=135.0,
            speed_classification="good",
            dominant_emotion="neutral",
        )

        assert result.filler_score == 50.0, \
            f"Expected filler_score = 50.0, got {result.filler_score}"

    def test_pacing_good(self):
        """speed='good' -> pacing_score=100 regardless of WPM."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=135.0,
            speed_classification="good",
            dominant_emotion="neutral",
        )

        assert result.pacing_score == 100.0, \
            f"Expected pacing_score = 100.0, got {result.pacing_score}"

    def test_pacing_slow_edge(self):
        """wpm=110, speed='slow' -> pacing_score=100 (boundary)."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=110.0,
            speed_classification="slow",
            dominant_emotion="neutral",
        )

        assert result.pacing_score == 100.0, \
            f"Expected pacing_score = 100.0, got {result.pacing_score}"

    def test_pacing_slow_midpoint(self):
        """wpm=80, speed='slow' -> pacing_score=(80-50)/(110-50)*100 = 50."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=80.0,
            speed_classification="slow",
            dominant_emotion="neutral",
        )

        assert result.pacing_score == 50.0, \
            f"Expected pacing_score = 50.0, got {result.pacing_score}"

    def test_pacing_slow_minimum(self):
        """wpm=50, speed='slow' -> pacing_score=0."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=50.0,
            speed_classification="slow",
            dominant_emotion="neutral",
        )

        assert result.pacing_score == 0.0, \
            f"Expected pacing_score = 0.0, got {result.pacing_score}"

    def test_pacing_fast_edge(self):
        """wpm=160, speed='fast' -> pacing_score=100 (boundary)."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=160.0,
            speed_classification="fast",
            dominant_emotion="neutral",
        )

        assert result.pacing_score == 100.0, \
            f"Expected pacing_score = 100.0, got {result.pacing_score}"

    def test_pacing_fast_midpoint(self):
        """wpm=200, speed='fast' -> pacing_score=(240-200)/(240-160)*100 = 50."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=200.0,
            speed_classification="fast",
            dominant_emotion="neutral",
        )

        assert result.pacing_score == 50.0, \
            f"Expected pacing_score = 50.0, got {result.pacing_score}"

    def test_pacing_fast_maximum(self):
        """wpm=240, speed='fast' -> pacing_score=0."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=240.0,
            speed_classification="fast",
            dominant_emotion="neutral",
        )

        assert result.pacing_score == 0.0, \
            f"Expected pacing_score = 0.0, got {result.pacing_score}"

    def test_clarity_ideal(self):
        """wpm=135 -> clarity_score=100."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=135.0,
            speed_classification="good",
            dominant_emotion="neutral",
        )

        assert result.clarity_score == 100.0, \
            f"Expected clarity_score = 100.0, got {result.clarity_score}"

    def test_clarity_off(self):
        """wpm=100 -> clarity_score = max(0, 100 - abs(100-135)*1.0) = 65."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=100.0,
            speed_classification="slow",
            dominant_emotion="neutral",
        )

        assert result.clarity_score == 65.0, \
            f"Expected clarity_score = 65.0, got {result.clarity_score}"

    def test_clarity_extreme_low(self):
        """wpm=0 -> clarity_score = max(0, 100 - abs(0-135)*1.0) = 0 (clamped)."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=0.0,
            speed_classification="slow",
            dominant_emotion="neutral",
        )

        assert result.clarity_score == 0.0, \
            f"Expected clarity_score = 0.0, got {result.clarity_score}"

    def test_clarity_above_ideal(self):
        """wpm=170 -> clarity_score = max(0, 100 - abs(170-135)*1.0) = 65."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=170.0,
            speed_classification="fast",
            dominant_emotion="neutral",
        )

        assert result.clarity_score == 65.0, \
            f"Expected clarity_score = 65.0, got {result.clarity_score}"

    # ----- Emotion mapping tests -----

    @pytest.mark.parametrize("emotion,expected_score", [
        ("happy", 100.0),
        ("neutral", 80.0),
        ("surprise", 70.0),
        ("sad", 40.0),
        ("angry", 30.0),
        ("fear", 20.0),
        ("disgust", 10.0),
    ])
    def test_emotion_mapping(self, emotion, expected_score):
        """Each emotion maps to correct score."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=135.0,
            speed_classification="good",
            dominant_emotion=emotion,
        )

        assert result.emotion_score == expected_score, \
            f"Expected emotion_score = {expected_score} for '{emotion}', " \
            f"got {result.emotion_score}"

    def test_emotion_case_insensitive(self):
        """Emotion matching should be case-insensitive."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=135.0,
            speed_classification="good",
            dominant_emotion="HAPPY",
        )

        assert result.emotion_score == 100.0, \
            f"Expected emotion_score = 100.0 for 'HAPPY', got {result.emotion_score}"

    def test_emotion_unknown(self):
        """Unknown emotion -> emotion_score=50 (fallback to 'uncertain')."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=135.0,
            speed_classification="good",
            dominant_emotion="unknown_emotion",
        )

        assert result.emotion_score == 50.0, \
            f"Expected emotion_score = 50.0 for unknown emotion, " \
            f"got {result.emotion_score}"

    # ----- Classification boundary tests -----

    def test_classification_excellent(self):
        """composite=85 -> Excellent."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=90.0,
            filler_rate_per_100=1.0,
            wpm=130.0,
            speed_classification="good",
            dominant_emotion="happy",
        )

        assert result.classification == "Excellent", \
            f"Expected 'Excellent', got '{result.classification}'"

    def test_classification_good(self):
        """composite=70 -> Good."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=60.0,
            filler_rate_per_100=4.0,
            wpm=120.0,
            speed_classification="good",
            dominant_emotion="neutral",
        )

        assert result.classification == "Good", \
            f"Expected 'Good', got '{result.classification}'"

    def test_classification_needs_improvement(self):
        """composite=50 -> Needs Improvement."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=30.0,
            filler_rate_per_100=8.0,
            wpm=180.0,
            speed_classification="fast",
            dominant_emotion="sad",
        )

        assert result.classification == "Needs Improvement", \
            f"Expected 'Needs Improvement', got '{result.classification}'"

    # ----- Composite weight verification tests -----

    def test_weighted_composite(self):
        """Verify composite matches manual calculation with given weights."""
        from modules.scoring import compute_confidence

        # eye_contact=80, filler_rate=2 -> filler=80, wpm=135 -> pacing=100, clarity=100
        # emotion=neutral -> 80
        # composite = 80*0.30 + 80*0.25 + 100*0.20 + 100*0.15 + 80*0.10
        #           = 24.0 + 20.0 + 20.0 + 15.0 + 8.0 = 87.0
        result = compute_confidence(
            eye_contact_pct=80.0,
            filler_rate_per_100=2.0,   # 100 - 20 = 80
            wpm=135.0,
            speed_classification="good",
            dominant_emotion="neutral",
        )

        expected_composite = 87.0
        assert result.composite == expected_composite, \
            f"Expected composite = {expected_composite}, got {result.composite}"

    # ----- Edge cases -----

    def test_wpm_zero_pacing(self):
        """WPM=0 -> pacing_score=0 (falls in 'slow' territory, formula gives 0)."""
        from modules.scoring import compute_confidence

        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=5.0,
            wpm=0.0,
            speed_classification="slow",
            dominant_emotion="neutral",
        )

        assert result.pacing_score == 0.0, \
            f"Expected pacing_score = 0.0, got {result.pacing_score}"

    def test_classification_boundary_excellent(self):
        """composite exactly 80.0 -> Excellent (boundary)."""
        from modules.scoring import compute_confidence

        # Need composite = 80.0 exactly
        # Try: eye_contact=85, filler=100, pacing=100, clarity=100, emotion=80
        # composite = 85*0.30 + 100*0.25 + 100*0.20 + 100*0.15 + 80*0.10
        #           = 25.5 + 25.0 + 20.0 + 15.0 + 8.0 = 93.5 ... too high
        # Try: eye_contact=70, filler=80, pacing=100, clarity=85, emotion=50
        # composite = 70*0.30 + 80*0.25 + 100*0.20 + 85*0.15 + 50*0.10
        #           = 21.0 + 20.0 + 20.0 + 12.75 + 5.0 = 78.75 ... too low
        # Try: eye_contact=75, filler=80, pacing=100, clarity=85, emotion=80
        # composite = 75*0.30 + 80*0.25 + 100*0.20 + 85*0.15 + 80*0.10
        #           = 22.5 + 20.0 + 20.0 + 12.75 + 8.0 = 83.25 ... too high
        # Let's try: eye_contact=60, filler=80, pacing=100, clarity=100, emotion=80
        # composite = 60*0.30 + 80*0.25 + 100*0.20 + 100*0.15 + 80*0.10
        #           = 18.0 + 20.0 + 20.0 + 15.0 + 8.0 = 81.0 ... close but not 80
        # eye_contact=50, filler=80, pacing=100, clarity=100, emotion=100
        # = 15+20+20+15+10 = 80.0
        result = compute_confidence(
            eye_contact_pct=50.0,
            filler_rate_per_100=2.0,   # 100 - 20 = 80
            wpm=135.0,
            speed_classification="good",  # 100
            dominant_emotion="happy",      # 100
        )

        assert result.composite == 80.0, \
            f"Expected composite = 80.0 (boundary), got {result.composite}"
        assert result.classification == "Excellent", \
            f"Expected 'Excellent' at boundary 80, got '{result.classification}'"

    def test_classification_boundary_good_low(self):
        """composite exactly 60.0 -> Good (lower boundary, >=60.0)."""
        from modules.scoring import compute_confidence

        # eye_contact=20, filler_rate=4 -> 60, wpm=135(good->100, clarity=100), emotion=sad->40
        # composite = 20*0.30 + 60*0.25 + 100*0.20 + 100*0.15 + 40*0.10
        #           = 6.0 + 15.0 + 20.0 + 15.0 + 4.0 = 60.0
        result = compute_confidence(
            eye_contact_pct=20.0,
            filler_rate_per_100=4.0,
            wpm=135.0,
            speed_classification="good",
            dominant_emotion="sad",
        )

        assert result.composite == 60.0, \
            f"Expected composite = 60.0, got {result.composite}"
        assert result.classification == "Good", \
            f"Expected 'Good' at boundary 60, got '{result.classification}'"

    # ----- calc_filler_rate helper test -----

    def test_calc_filler_rate(self):
        """calc_filler_rate should compute rate per 100 words."""
        from modules.scoring import calc_filler_rate

        rate = calc_filler_rate(5, 100)
        assert rate == 5.0, f"Expected 5.0, got {rate}"

        rate = calc_filler_rate(10, 200)
        assert rate == 5.0, f"Expected 5.0, got {rate}"

        rate = calc_filler_rate(0, 100)
        assert rate == 0.0, f"Expected 0.0, got {rate}"

    def test_calc_filler_rate_zero_words(self):
        """calc_filler_rate with 0 total_words should return 0.0 (no div by zero)."""
        from modules.scoring import calc_filler_rate

        rate = calc_filler_rate(5, 0)
        assert rate == 0.0, f"Expected 0.0, got {rate}"

        rate = calc_filler_rate(5, -1)
        assert rate == 0.0, f"Expected 0.0, got {rate}"


# ============================================================
# Feedback Tests: generate_feedback()
# ============================================================

class TestGenerateFeedback:
    """Test suite for generate_feedback."""

    def _get_feedback(self, eye_contact_pct, filler_rate_per_100, wpm,
                      speed_classification, dominant_emotion,
                      filler_count=None, eye_contact_score_override=None):
        """Helper: compute confidence then generate feedback."""
        from modules.scoring import compute_confidence, generate_feedback

        confidence = compute_confidence(
            eye_contact_pct=eye_contact_pct,
            filler_rate_per_100=filler_rate_per_100,
            wpm=wpm,
            speed_classification=speed_classification,
            dominant_emotion=dominant_emotion,
        )

        return generate_feedback(
            confidence=confidence,
            eye_contact_pct=eye_contact_pct,
            filler_rate_per_100=filler_rate_per_100,
            filler_count=filler_count if filler_count is not None else 0,
            wpm=wpm,
            speed_classification=speed_classification,
            dominant_emotion=dominant_emotion,
        )

    def test_feedback_perfect(self):
        """All metrics ideal -> full strengths, no weaknesses, few tips."""
        feedback = self._get_feedback(
            eye_contact_pct=100.0,
            filler_rate_per_100=0.0,
            wpm=135.0,
            speed_classification="good",
            dominant_emotion="happy",
            filler_count=0,
        )

        # Should have strengths + overall (composite=100)
        assert "Strong Eye Contact" in feedback
        assert "Low Filler Usage" in feedback
        assert "Well-Paced" in feedback
        assert "Positive Demeanor" in feedback
        assert "Excellent confidence score" in feedback

        # Should NOT have weakness markers
        assert "⚠️" not in feedback, \
            "Perfect scores should have no weaknesses"

    def test_feedback_all_poor(self):
        """All metrics poor -> 1 encouraging strength, all weaknesses, all tips."""
        feedback = self._get_feedback(
            eye_contact_pct=0.0,
            filler_rate_per_100=15.0,
            wpm=240.0,
            speed_classification="fast",
            dominant_emotion="disgust",
            filler_count=30,
        )

        # Should have encouraging message
        assert "Keep practicing" in feedback, \
            "Should have encouraging message when no strengths"

        # Should have all weakness markers
        assert "Eye Contact Needs Work" in feedback
        assert "Frequent Filler Words" in feedback
        assert "Speaking Pace is FAST" in feedback
        assert "Speaking Clarity Affected" in feedback
        assert "Facial Expressions Appear" in feedback

        # Should have various tip markers
        assert "Camera Practice" in feedback
        assert "Pause Instead of Filler" in feedback
        assert "Slow Down" in feedback
        assert "Clarity Drill" in feedback
        assert "Facial Engagement" in feedback

        # Should have 3 sections
        assert feedback.count("---") == 2, \
            f"Expected 2 separators for 3 sections, got {feedback.count('---')}"

    def test_feedback_mixed(self):
        """Mixed scores -> partial strengths + partial weaknesses."""
        feedback = self._get_feedback(
            eye_contact_pct=75.0,
            filler_rate_per_100=8.0,     # filler_score = 20 (< 60)
            wpm=100.0,
            speed_classification="slow",
            dominant_emotion="sad",       # emotion_score = 40 (< 60)
            filler_count=16,
        )

        # Should have some strengths (eye_contact=75 >= 70)
        assert "Strong Eye Contact" in feedback

        # Should have some weaknesses (filler=20 < 60, emotion=40 < 60)
        assert "Frequent Filler Words" in feedback
        assert "Facial Expressions Appear SAD" in feedback

        # Should NOT have all weakness types
        assert "Eye Contact Needs Work" not in feedback, \
            "Eye contact 75% should not be a weakness"

    def test_feedback_structure(self):
        """Verify output contains proper section structure."""
        feedback = self._get_feedback(
            eye_contact_pct=80.0,
            filler_rate_per_100=5.0,     # filler_score = 50 (< 60)
            wpm=130.0,
            speed_classification="good",
            dominant_emotion="happy",
            filler_count=10,
        )

        # Should have all three section headers
        assert "## Strengths" in feedback, \
            "Should have Strengths section"
        assert "## Areas to Improve" in feedback, \
            "Should have Areas to Improve section"
        assert "## Improvement Tips" in feedback, \
            "Should have Improvement Tips section"

        # Sections separated by ---
        assert "---" in feedback, \
            "Should have section separators"

        # Feedback should be non-empty string
        assert len(feedback) > 50, \
            "Feedback should be substantive"

    def test_feedback_empty_strengths(self):
        """All scores < 70 -> encouraging message, no individual strengths."""
        feedback = self._get_feedback(
            eye_contact_pct=40.0,
            filler_rate_per_100=8.0,     # filler_score = 20
            wpm=30.0,                    # pacing=0, clarity=0
            speed_classification="slow",
            dominant_emotion="disgust",   # emotion_score = 10
            filler_count=20,
        )

        # Should have "keep practicing" message
        assert "Keep practicing" in feedback, \
            "Should show encouraging message when no strengths"

        # Should NOT have individual strength markers
        assert "Strong Eye Contact" not in feedback
        assert "Low Filler Usage" not in feedback
        assert "Well-Paced" not in feedback
        assert "Positive Demeanor" not in feedback

        # Should still have weaknesses (all < 60)
        assert "Eye Contact Needs Work" in feedback
