# Phase 5: Scoring, Feedback & Dashboard - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-16
**Phase:** 05-scoring-feedback-dashboard
**Areas discussed:** Confidence scoring formula, Feedback template content, Dashboard layout & charts, History page design

---

## Confidence Scoring Formula

| Option | Description | Selected |
|--------|-------------|----------|
| Differentiated weights (Recommended) | Eye contact 30%, filler 25%, pacing 20%, clarity 15%, emotion 10% | ✓ |
| Equal weights | 20% each | |
| You decide | Let the agent design a reasonable weighted formula | |

**User's choice:** Differentiated weights (Recommended)
**Notes:** Also confirmed standard classification thresholds: Excellent >=80, Good 60-79, Needs Improvement <60.

---

## Feedback Template Content

| Option | Description | Selected |
|--------|-------------|----------|
| Three sections (Recommended) | Strengths, Weaknesses, Improvement Tips | ✓ |
| Four sections | Overall Summary, Strengths, Areas to Improve, Actionable Tips | |
| You decide | Let the agent design the structure | |

**User's choice:** Three sections (Recommended)
**Follow-up:** Tip granularity

| Option | Description | Selected |
|--------|-------------|----------|
| Concrete per-metric tips (Recommended) | Each weakness maps to 1-2 concrete tips | ✓ |
| General advice | General advice paragraphs per section | |
| You decide | Let the agent decide based on available metrics | |

**User's choice:** Concrete per-metric tips (Recommended)

---

## Dashboard Layout & Charts

| Option | Description | Selected |
|--------|-------------|----------|
| Top summary row then stacked (Recommended) | Video preview + summary cards in top row, then transcript, then charts below | ✓ |
| Two-column layout | Left: video + report, right: metrics + charts | |
| You decide | Let the agent design | |

**User's choice:** Top summary row then stacked (Recommended)

**Follow-up:** Chart types

| Option | Description | Selected |
|--------|-------------|----------|
| Plotly charts (Recommended) | Gauge for confidence, bar for emotion, annotation for eye contact | ✓ |
| Streamlit native widgets | st.metric for confidence, st.dataframe for emotion | |
| You decide | Let the agent pick | |

**User's choice:** Plotly charts (Recommended)

**Follow-up:** Video preview

| Option | Description | Selected |
|--------|-------------|----------|
| st.video() player (Recommended) | Embedded video player | ✓ |
| Thumbnail + link | Video thumbnail with link | |
| You decide | Let the agent decide | |

**User's choice:** st.video() player (Recommended)

**Follow-up:** Report display

| Option | Description | Selected |
|--------|-------------|----------|
| Expandable section at bottom (Recommended) | st.expander at bottom of dashboard | ✓ |
| Always-visible section | Full-width always visible | |
| You decide | Let the agent decide | |

**User's choice:** Expandable section at bottom (Recommended)

---

## History Page Design

| Option | Description | Selected |
|--------|-------------|----------|
| Summary table + click to view (Recommended) | Table with metrics, click to load full report | ✓ |
| List + inline expand | Simple list with inline expansion | |
| You decide | Let the agent design | |

**User's choice:** Summary table + click to view (Recommended)

**Follow-up:** Table columns

| Option | Description | Selected |
|--------|-------------|----------|
| All key metrics (Recommended) | Date, Confidence Score, WPM, Filler Count, Eye Contact %, Dominant Emotion | ✓ |
| Minimal | Date, Confidence Score, WPM | |
| You decide | Let the agent decide | |

**User's choice:** All key metrics (Recommended)

---

## Agent's Discretion

- **Database persistence timing** — Not discussed (user skipped this area). Single write at end of pipeline, matching existing patterns.
- Exact weight fine-tuning (±5%) within differentiated proportions
- Clarity score derivation from WPM (linear interpolation or step function)
- Plotly chart configuration (colors, sizing, labels within dark theme)
- History page "load" implementation approach

## Deferred Ideas

None.
