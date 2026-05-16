---
phase: 03-speech-text-analysis
plan: 01
subsystem: speech-analysis
tags: [spacy, nlp, filler-words, wpm, speech-analysis]

# Dependency graph
requires:
  - phase: 01-core-infrastructure-data-models
    provides: "Pydantic models (SpeechAnalysisResult, FillerWordCount), utils/helpers (load_spacy_model)"
  - phase: 02-video-upload-audio-pipeline-transcription
    provides: "TranscriptionResult model with full_text and duration_sec"
provides:
  - "Filler word detection with POS-disambiguated 'like' (excludes VERB/AUX usage)"
  - "Speaking speed WPM calculation with slow/good/fast classification"
  - "analyze_speech integration function accepting TranscriptionResult"
affects:
  - "Phase 3 Plan 2: Integrate into Upload pipeline + Dashboard display"
  - "Phase 5: Confidence scoring uses filler word and WPM metrics"

# Tech tracking
tech-stack:
  added: [spacy 3.8.14, pytest 9.0.3, streamlit 1.57.0]
  patterns:
    - "TDD: tests written before implementation, 12 test cases all passing"
    - "spaCy POS-based disambiguation for filler word detection"
    - "Optional nlp parameter pattern for testability"
    - "Integration function pattern (analyze_speech) that wires sub-functions together"

key-files:
  created:
    - modules/speech_analysis.py
    - tests/__init__.py
    - tests/test_speech_analysis.py
  modified: []

key-decisions:
  - "POS check excludes both VERB and AUX tags for 'like' (spaCy tags catenative 'like' as AUX, not VERB)"
  - "calculate_wpm accepts optional nlp param for testability (falls back to spacy.load if None)"
  - "analyze_filler_words returns sorted list (descending count, alphabetically for ties)"

patterns-established:
  - "Module functions accept explicit nlp parameter for testability (not hidden imports)"
  - "Pure functions for filler_words and WPM, integration function wires them together"
  - "Edge cases (empty text, zero duration) return safe defaults (0.0, 'slow', [])

requirements-completed: [SPE-01, SPE-02, SPE-03, SPE-04]

# Metrics
duration: 6min
completed: 2026-05-16
---

# Phase 03: Speech & Text Analysis — Plan 1 Summary

**spaCy-based filler word detection with POS disambiguation (excludes verb "like") and WPM calculation with slow/good/fast classification, delivered via TDD with 12 passing tests**

## Performance

- **Duration:** 6 min
- **Started:** 2026-05-16T12:20:22Z
- **Completed:** 2026-05-16T12:25:59Z
- **Tasks:** 1
- **Files modified:** 3

## Accomplishments
- Filler word detection for "um", "uh", "like", "basically", "literally", and "you know" bigram
- POS-disambiguated "like": excluded when tagged as VERB or AUX, counted when discourse marker
- WPM calculation with slow (<110), good (110-160), and fast (>160) classification
- Edge case handling: empty text returns zero counts, zero duration returns safe defaults
- `analyze_speech` integration function produces fully populated `SpeechAnalysisResult`
- 12 automated unit tests verify all behaviors

## Task Commits

Each task phase was committed atomically:

1. **Task 1 (RED): Test file with 12 failing tests** - `ef67135` (test: add failing tests for filler word detection and WPM calculation)
2. **Task 1 (GREEN): Speech analysis module implementation** - `bea6074` (feat: implement speech analysis engine with filler word detection and WPM)

## Files Created/Modified
- `modules/speech_analysis.py` - 3 exported functions: `analyze_filler_words`, `calculate_wpm`, `analyze_speech`
- `tests/__init__.py` - Test suite init marker
- `tests/test_speech_analysis.py` - 12 unit tests covering all behaviors

## Decisions Made
- **POS exclusion includes AUX**: spaCy tags "like" in "I like running" as AUX (catenative verb), not VERB. Excluding both `pos_` values is essential for correctness.
- **Optional nlp parameter on calculate_wpm**: Accepts an `nlp` parameter for test efficiency; falls back to `spacy.load("en_core_web_sm")` if None. This matches the pattern established in `analyze_filler_words`.
- **Filler results sorted descending**: Results sorted by count (highest first) with alphabetical tie-breaking, enabling `filler_words[0]` as top filler.
- **"you know" bigram**: Implemented with while-loop index tracking to skip the "know" token after detection, preventing double-count.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] VERB-only POS check missed AUX-tagged "like"**
- **Found during:** Task 1 (GREEN phase verification)
- **Issue:** The initial check `token.pos_ != "VERB"` failed to exclude "like" in "I like running" because spaCy tags it as `AUX` (catenative verb usage), not `VERB`. Test 1 ("like as verb") was failing with count=1 instead of count=0.
- **Fix:** Changed `pos_ != "VERB"` to `pos_ not in ("VERB", "AUX")` in the `analyze_filler_words` function.
- **Files modified:** `modules/speech_analysis.py`
- **Verification:** `test_analyze_filler_words_verb_like_excluded` now passes. Tested with both "I like pizza" (VERB) and "I like running" (AUX).
- **Committed in:** `bea6074` (GREEN commit)

**2. [Rule 3 - Blocking] Missing dependencies: pytest, spacy, streamlit**
- **Found during:** Task 1 (RED phase test execution)
- **Issue:** Project environment had none of the dependencies installed (pytest for running tests, spaCy for NLP, streamlit for `load_spacy_model()` decorator).
- **Fix:** Installed `pytest`, `spacy==3.8.14`, `en_core_web_sm` model, and `streamlit==1.57.0`.
- **Files modified:** N/A (global pip installation)
- **Verification:** All 12 tests pass, module imports cleanly.
- **Committed in:** `bea6074` (GREEN commit)

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking)
**Impact on plan:** Both auto-fixes were necessary for correctness and test execution. No scope creep.

## Issues Encountered
- **spaCy POS tagging nuance**: "like" in "I like running" is tagged as `AUX` (auxiliary verb) rather than `VERB`. This is a known spaCy behavior for catenative verb constructions. Fixed by excluding both `VERB` and `AUX` in the POS check.
- **Streamlit dependency in utils/helpers.py**: The `load_spacy_model()` function uses `@_get_st().cache_resource` decorator, which evaluates at import time and requires streamlit to be installed. This is a pre-existing pattern that requires streamlit for the integration test. Documented for awareness.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Speech analysis engine complete with 3 exported functions
- Ready for **Plan 2**: Integrate into Upload pipeline + Dashboard display
- Wires into `TranscriptionResult` (from Phase 2) via `analyze_speech()` integration function
- Output `SpeechAnalysisResult` model ready for dashboard display and confidence scoring (Phase 5)

## Self-Check: PASSED

- ✅ `modules/speech_analysis.py` — exists
- ✅ `tests/__init__.py` — exists
- ✅ `tests/test_speech_analysis.py` — exists
- ✅ Commit `ef67135` — found in git history
- ✅ Commit `bea6074` — found in git history

---

*Phase: 03-speech-text-analysis*
*Completed: 2026-05-16*
