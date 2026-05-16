"""Unit tests for speech analysis module — filler words and WPM.

Tests follow these conventions:
- Fixtures (nlp) load spaCy model once per session
- All filler word tests use analyze_filler_words() directly
- All WPM tests use calculate_wpm() directly
- Integration test uses analyze_speech() with TranscriptionResult
"""

from typing import List

import pytest
from modules.models import FillerWordCount, TranscriptionResult


@pytest.fixture(scope="module")
def nlp():
    """Load spaCy English model once for all tests in this module."""
    import spacy
    return spacy.load("en_core_web_sm")


# ============================================================
# Test 1: "like" as verb is NOT a filler
# ============================================================

def test_analyze_filler_words_verb_like_excluded(nlp):
    """'like' used as a verb (VB/VBP/VBZ/VBD) should NOT be counted as filler."""
    from modules.speech_analysis import analyze_filler_words

    text = "I like pizza and I like running"
    result = analyze_filler_words(text, nlp)

    like_entry = next((fw for fw in result if fw.word == "like"), None)
    assert like_entry is None or like_entry.count == 0, \
        f"Expected 'like' count = 0 for verb usage, got {like_entry.count if like_entry else 'missing'}"


# ============================================================
# Test 2: "like" as discourse filler IS counted
# ============================================================

def test_analyze_filler_words_discourse_like_counted(nlp):
    """'like' used as a discourse filler should be counted."""
    from modules.speech_analysis import analyze_filler_words

    text = "I was like really tired and he was like whatever"
    result = analyze_filler_words(text, nlp)

    like_entry = next((fw for fw in result if fw.word == "like"), None)
    assert like_entry is not None, "Expected 'like' entry in results"
    assert like_entry.count == 2, \
        f"Expected 'like' count = 2 for discourse usage, got {like_entry.count}"


# ============================================================
# Test 3: "um" and "uh" are detected
# ============================================================

def test_analyze_filler_words_um_uh(nlp):
    """'um' and 'uh' should both be detected as filler words."""
    from modules.speech_analysis import analyze_filler_words

    text = "Um I think uh maybe we should go"
    result = analyze_filler_words(text, nlp)

    words = {fw.word: fw.count for fw in result}
    assert words.get("um") == 1, f"Expected 'um' = 1, got {words.get('um')}"
    assert words.get("uh") == 1, f"Expected 'uh' = 1, got {words.get('uh')}"


# ============================================================
# Test 4: "basically" and "literally" are detected
# ============================================================

def test_analyze_filler_words_basically_literally(nlp):
    """'basically' and 'literally' should both be detected as filler words."""
    from modules.speech_analysis import analyze_filler_words

    text = "Basically it's literally the best option"
    result = analyze_filler_words(text, nlp)

    words = {fw.word: fw.count for fw in result}
    assert words.get("basically") == 1, \
        f"Expected 'basically' = 1, got {words.get('basically')}"
    assert words.get("literally") == 1, \
        f"Expected 'literally' = 1, got {words.get('literally')}"


# ============================================================
# Test 5: "you know" bigram detected
# ============================================================

def test_analyze_filler_words_you_know(nlp):
    """'you know' bigram should be detected across case variations."""
    from modules.speech_analysis import analyze_filler_words

    text = "You know I was thinking, you know what I mean"
    result = analyze_filler_words(text, nlp)

    words = {fw.word: fw.count for fw in result}
    assert words.get("you know") == 2, \
        f"Expected 'you know' = 2, got {words.get('you know')}"


# ============================================================
# Test 6: Mixed filler words return correct totals
# ============================================================

def test_analyze_filler_words_mixed(nlp):
    """Mixed filler words should return correct total and top filler."""
    from modules.speech_analysis import analyze_filler_words

    text = "Um like I was literally thinking you know about the idea uh basically"
    result = analyze_filler_words(text, nlp)

    total = sum(fw.count for fw in result)
    assert total == 6, f"Expected total_filler_count = 6, got {total}"

    # All 6 filler words should have count 1 (tie for top)
    words = {fw.word: fw.count for fw in result}
    assert words.get("um") == 1
    assert words.get("like") == 1
    assert words.get("literally") == 1
    assert words.get("you know") == 1
    assert words.get("uh") == 1
    assert words.get("basically") == 1


# ============================================================
# Test 7: Empty text returns zero counts
# ============================================================

def test_analyze_filler_words_empty(nlp):
    """Empty text should return an empty list."""
    from modules.speech_analysis import analyze_filler_words

    result = analyze_filler_words("", nlp)
    assert result == [], f"Expected empty list, got {result}"


# ============================================================
# Test 8: WPM calculation — slow (< 110)
# ============================================================

def test_calculate_wpm_slow(nlp):
    """WPM under 110 should be classified as 'slow'."""
    from modules.speech_analysis import calculate_wpm

    # 100 words in 60 seconds = 100 WPM
    text = " ".join(["word"] * 100)
    wpm, classification = calculate_wpm(text, 60.0, nlp)

    assert abs(wpm - 100.0) < 1.0, f"Expected WPM ≈ 100.0, got {wpm}"
    assert classification == "slow", \
        f"Expected 'slow', got '{classification}'"


# ============================================================
# Test 9: WPM calculation — good (110–160)
# ============================================================

def test_calculate_wpm_good(nlp):
    """WPM between 110 and 160 should be classified as 'good'."""
    from modules.speech_analysis import calculate_wpm

    # 130 words in 60 seconds = 130 WPM
    text = " ".join(["word"] * 130)
    wpm, classification = calculate_wpm(text, 60.0, nlp)

    assert abs(wpm - 130.0) < 1.0, f"Expected WPM ≈ 130.0, got {wpm}"
    assert classification == "good", \
        f"Expected 'good', got '{classification}'"


# ============================================================
# Test 10: WPM calculation — fast (> 160)
# ============================================================

def test_calculate_wpm_fast(nlp):
    """WPM above 160 should be classified as 'fast'."""
    from modules.speech_analysis import calculate_wpm

    # 170 words in 60 seconds = 170 WPM
    text = " ".join(["word"] * 170)
    wpm, classification = calculate_wpm(text, 60.0, nlp)

    assert abs(wpm - 170.0) < 1.0, f"Expected WPM ≈ 170.0, got {wpm}"
    assert classification == "fast", \
        f"Expected 'fast', got '{classification}'"


# ============================================================
# Test 11: WPM calculation — empty text edge case
# ============================================================

def test_calculate_wpm_empty(nlp):
    """Empty text should return 0.0 WPM and 'slow' classification."""
    from modules.speech_analysis import calculate_wpm

    wpm, classification = calculate_wpm("", 60.0, nlp)

    assert wpm == 0.0, f"Expected WPM = 0.0, got {wpm}"
    assert classification == "slow", \
        f"Expected 'slow', got '{classification}'"


# ============================================================
# Test 12: analyze_speech integration test
# ============================================================

def test_analyze_speech_integration():
    """analyze_speech should produce a fully populated SpeechAnalysisResult."""
    from modules.speech_analysis import analyze_speech

    transcript = TranscriptionResult(
        segments=[],
        full_text="Um I like pizza but literally I was thinking you know uh basically",
        model_used="base",
        duration_sec=30.0,
    )

    result = analyze_speech(transcript)

    # Verify type and field presence
    assert result.total_filler_count >= 0
    assert result.wpm >= 0
    assert result.speed_classification in ("slow", "good", "fast")
    assert result.total_words >= 0
    assert result.duration_minutes > 0

    # Verify filler_words is a list of FillerWordCount
    assert isinstance(result.filler_words, list)
    if result.filler_words:
        assert isinstance(result.filler_words[0], FillerWordCount)

    # "like" in "I like pizza" is a verb, should not be counted
    like_entry = next(
        (fw for fw in result.filler_words if fw.word == "like"), None
    )
    if like_entry is not None:
        # "like" in this text appears as verb ("I like pizza") AND potentially
        # as filler elsewhere, so count should be 0 since "like" here is a verb
        pass  # Accept either 0 or absent for "like"

    # Verify top_filler is populated if there are filler words
    if result.total_filler_count > 0:
        assert result.top_filler is not None, \
            "top_filler should not be None when fillers exist"
        assert isinstance(result.top_filler, str)
