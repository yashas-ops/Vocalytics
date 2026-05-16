"""Speech analysis engine: filler word detection and WPM calculation.

Provides three functions:
    - analyze_filler_words: POS-disambiguated filler word detection
    - calculate_wpm: Words-per-minute calculation with speed classification
    - analyze_speech: Integration function that produces SpeechAnalysisResult
"""

from typing import List, Optional, Tuple

from modules.models import FillerWordCount, SpeechAnalysisResult


FILLER_WORDS: List[str] = [
    "um",
    "uh",
    "like",
    "basically",
    "literally",
    "you know",
]


def analyze_filler_words(text: str, nlp) -> List[FillerWordCount]:
    """Detect and count filler words in text with POS disambiguation.

    Uses spaCy for tokenization and POS tagging. The word "like" is only
    counted as filler when it is NOT used as a verb (pos_ != "VERB").

    Args:
        text: Input text to analyze.
        nlp: Loaded spaCy Language object for tokenization.

    Returns:
        List of FillerWordCount for detected filler words, sorted by count
        descending (alphabetically for ties). Empty list if no fillers found.
    """
    if not text or not text.strip():
        return []

    doc = nlp(text)

    # Tokenize: only alphabetic tokens, lowercase
    tokens = [token for token in doc if token.is_alpha]

    # Initialize counters for all filler words
    counts: dict = {
        "um": 0,
        "uh": 0,
        "like": 0,
        "basically": 0,
        "literally": 0,
        "you know": 0,
    }

    i = 0
    while i < len(tokens):
        token_lower = tokens[i].lower_

        if token_lower == "um":
            counts["um"] += 1
        elif token_lower == "uh":
            counts["uh"] += 1
        elif token_lower == "like":
            # Only count if NOT used as a verb (VERB or AUX pos)
            if tokens[i].pos_ not in ("VERB", "AUX"):
                counts["like"] += 1
        elif token_lower == "basically":
            counts["basically"] += 1
        elif token_lower == "literally":
            counts["literally"] += 1
        elif token_lower == "you":
            # Check for "you know" bigram
            if i + 1 < len(tokens) and tokens[i + 1].lower_ == "know":
                counts["you know"] += 1
                i += 1  # Skip "know" token

        i += 1

    # Filter out words with zero count and build result list
    result = [
        FillerWordCount(word=word, count=count)
        for word, count in counts.items()
        if count > 0
    ]

    # Sort descending by count, alphabetically for ties
    result.sort(key=lambda fw: (-fw.count, fw.word))

    return result


def calculate_wpm(
    text: str, duration_sec: float, nlp=None
) -> Tuple[float, str]:
    """Calculate speaking speed in words per minute and classify.

    Args:
        text: Transcribed text to analyze.
        duration_sec: Duration of speech in seconds.
        nlp: Optional loaded spaCy Language object. If None, loads
             en_core_web_sm.

    Returns:
        Tuple of (wpm, classification) where classification is one of
        "slow" (<110), "good" (110-160), or "fast" (>160).
    """
    duration_min = duration_sec / 60.0

    if not text or not text.strip() or duration_min <= 0:
        return (0.0, "slow")

    if nlp is None:
        import spacy
        nlp = spacy.load("en_core_web_sm")

    doc = nlp(text)

    # Count only alphabetic tokens
    total_words = sum(1 for token in doc if token.is_alpha)

    if total_words == 0:
        return (0.0, "slow")

    wpm = total_words / duration_min

    if wpm < 110:
        classification = "slow"
    elif wpm <= 160:
        classification = "good"
    else:
        classification = "fast"

    return (round(wpm, 1), classification)


def analyze_speech(transcript) -> SpeechAnalysisResult:
    """Full speech analysis: filler words + WPM from a TranscriptionResult.

    Args:
        transcript: TranscriptionResult with full_text and duration_sec.

    Returns:
        SpeechAnalysisResult with all fields populated.
    """
    from utils.helpers import load_spacy_model

    nlp = load_spacy_model()
    text = transcript.full_text
    duration_sec = transcript.duration_sec

    # Analyze filler words
    filler_words = analyze_filler_words(text, nlp)
    total_filler_count = sum(fw.count for fw in filler_words)

    # Determine top filler (max count, tie-break alphabetically)
    top_filler: Optional[str] = None
    if filler_words:
        top_filler = filler_words[0].word

    # Calculate WPM
    wpm, speed_classification = calculate_wpm(text, duration_sec, nlp)

    # Count total words
    doc = nlp(text)
    total_words = sum(1 for token in doc if token.is_alpha)

    duration_minutes = duration_sec / 60.0

    return SpeechAnalysisResult(
        filler_words=filler_words,
        total_filler_count=total_filler_count,
        top_filler=top_filler,
        wpm=wpm,
        speed_classification=speed_classification,
        total_words=total_words,
        duration_minutes=duration_minutes,
    )
