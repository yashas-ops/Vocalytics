# Phase 5: Scoring, Feedback & Dashboard - Context

**Gathered:** 2026-05-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Complete the analysis pipeline: confidence score computation (weighted heuristic), template-based feedback report generation, full dashboard with visualizations and video preview, SQLite persistence of all results, and interview history browser. Integrates as the final pipeline step and finalizes all dashboard display sections.

**Depends on:** Phase 3 (speech analysis metrics), Phase 4 (visual analysis metrics)
**Does NOT include:** PDF export (v2), multi-session comparison (v2), webcam recording (v2), chatbot/LLM features.

</domain>

<decisions>
## Implementation Decisions

### Confidence Scoring Formula
- **D-01:** Differentiated weights: Eye contact 30%, Filler words 25%, Speaking pace 20%, Clarity 15%, Emotion 10%. Weights emphasize strongest confidence signals and de-emphasize noisier emotion keyframe data.
- **D-02:** Classification thresholds: Excellent >=80, Good 60-79, Needs Improvement <60 (matches SCORE-02).
- **D-03:** Composite score = sum(component_score * weight) for all 5 components. Each component score normalized 0-100 before weighting.
- **D-04:** Clarity score derived from WPM classification (not from a separate ML model) — at target WPM = high clarity, too slow/fast = lower clarity.

### Template-Based Feedback
- **D-05:** Three-section report structure: Strengths, Weaknesses, Improvement Tips.
- **D-06:** Concrete per-metric improvement tips — each low-performing metric generates 1-2 specific actionable tips (no generic advice paragraphs).
- **D-07:** Template generation uses Python string formatting + conditional logic (no spaCy NLP needed beyond existing filler word detection). Threshold-driven messages keyed to metric values.
- **D-08:** Feedback report displayed in an expandable section at the bottom of the Dashboard page (`st.expander`).

### Dashboard Layout & Visualizations
- **D-09:** Top summary row: video preview (`st.video()`) on left, 4 metric cards (Confidence Score, Eye Contact, Speaking Speed, Filler Words) on right using `st.columns`.
- **D-10:** Below summary row, stacked sections: Transcript (text area), Filler Word Analysis (breakdown + rate), Eye Contact & Emotion Analysis (charts + annotations), Feedback Report (expandable).
- **D-11:** Plotly charts for visualizations (not Streamlit native):
  - Confidence score: Plotly gauge chart (0-100 needle)
  - Emotion distribution: Plotly horizontal bar chart
  - Eye contact: `st.metric` with annotation badge (reuses existing Phase 4 threshold text)
- **D-12:** Charts use dark theme colors to match the existing navy palette.

### SQLite Persistence
- **D-13:** Single write at end of pipeline (not incremental). All analysis results written to the existing `interviews` table in one transaction after pipeline completes.
- **D-14:** JSON fields for complex data (transcript segments, filler words, emotion distribution) matching existing schema patterns.

### History Page
- **D-15:** Summary table with columns: Date, Confidence Score, WPM, Filler Count, Eye Contact %, Dominant Emotion.
- **D-16:** Click to view full report — loads the selected interview's data into session state and navigates to Dashboard for full detail view.
- **D-17:** Sorted by date descending (most recent first).

### Agent's Discretion
- Exact weight values within the differentiated proportions (fine-tuning ±5% per component is acceptable).
- Clarity score formula derivation from WPM (linear interpolation or step function).
- Plotly chart exact configuration (colors, sizing, labels within dark theme constraints).
- Column width ratios in the summary row layout.
- History page "load" implementation (whether to use st.session_state overwrite or a separate detail view).

### Folded Todos
None — no pending todos matched Phase 5.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specs
- `.planning/ROADMAP.md` §Phase 5 — Phase goal, success criteria, requirements mapping
- `.planning/REQUIREMENTS.md` §Confidence Scoring — SCORE-01, SCORE-02, SCORE-03 definitions
- `.planning/REQUIREMENTS.md` §Feedback Report — FDBK-01, FDBK-02, FDBK-03 definitions
- `.planning/REQUIREMENTS.md` §Dashboard — DASH-01 through DASH-08 definitions
- `.planning/REQUIREMENTS.md` §Database & History — DB-01, DB-02, DB-03 definitions
- `.planning/REQUIREMENTS.md` §UI/UX — UI-02, UI-03 definitions

### Existing Code Patterns
- `modules/models.py` — `ConfidenceScores` (line 88), `InterviewResult` (line 103) — existing models
- `database/init.py` — `interviews` table with confidence/feedback columns already in schema (lines 63-73)
- `app.py` — Dashboard placeholders at lines 319 and 441-442; History placeholder at lines 452-457; pipeline structure with session state storage pattern
- `modules/speech_analysis.py` — Reference for module structure and error handling patterns
- `modules/visual_analysis.py` — Reference for non-critical pipeline step handling

### Prior Context
- `.planning/phases/01-core-infrastructure-data-models/01-CONTEXT.md` — D-08: Confidence score fields defined from Phase 1
- `.planning/phases/04-visual-analysis-eye-contact-emotion/04-CONTEXT.md` — D-19 through D-22: Dashboard conditional rendering, chart defaults, error handling

### Research
- `.planning/research/STACK.md` §Stack Patterns by Variant — "Budget/lightweight" pattern skips DeepFace, uses MediaPipe alone

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `modules/models.py::ConfidenceScores` — 5 component scores + composite + classification (all fields defined and importable)
- `modules/models.py::InterviewResult` — Top-level container with confidence and feedback fields
- `database/init.py` — Schema with all confidence columns (lines 63-70) and feedback_text column (line 73)
- `database/init.py::insert_interview()` — Inserts pending record, ready for UPDATE at pipeline end
- `app.py::render_dashboard_page()` — Dashboard skeleton with metric columns, speech section, visual analysis section, and Phase 5 placeholder
- Plotly already in requirements.txt (no install needed)
- `st.video()` — Native Streamlit component for video playback

### Established Patterns
- Sequential pipeline with `st.progress()` and `st.status()` (Phases 2-3-4)
- Session state storage: `st.session_state.last_*` pattern
- Dashboard conditional rendering: placeholder when no data, live data when exists
- `try/except` per pipeline step with graceful degradation
- Single `modules/` file per domain area

### Integration Points
- `app.py` Upload pipeline: add confidence scoring + feedback generation as Step 6 (after visual analysis, around line 250)
- `app.py` Upload pipeline: add SQLite UPDATE call at end of pipeline (insert_interview already called at Step 1)
- `app.py` Dashboard: replace "Confidence Score" placeholder `—` (line 319) with live data
- `app.py` Dashboard: replace "Coming in Phase 5" help text with actual help content
- `app.py` Dashboard: replace feedback placeholder (lines 441-442) with expandable report section
- `app.py` History: full render_history_page implementation
- `app.py` sidebar: wire history item click to dashboard navigation

</code_context>

<specifics>
## Specific Ideas

- Gauge chart for confidence score (0-100 scale, color zones: red <60, yellow 60-79, green >=80) — standard dashboard pattern
- Per-metric tips example: if filler rate > 5 per 100 words → "Try using a pause to collect your thoughts instead of saying 'um'. Practice speaking in shorter sentences."
- History "click to view" can store the selected interview_id and call st.rerun() to route to Dashboard with that interview's data loaded
- Can use sqlite3.Row factory (already configured) for fetching history rows as dicts

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

### Reviewed Todos (not folded)
None — no pending todos matched Phase 5.

</deferred>

---

*Phase: 05-scoring-feedback-dashboard*
*Context gathered: 2026-05-16*
