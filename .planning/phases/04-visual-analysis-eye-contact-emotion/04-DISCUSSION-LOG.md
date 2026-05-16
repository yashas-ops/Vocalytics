# Phase 4: Visual Analysis — Eye Contact & Emotion - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-16
**Phase:** 04-visual-analysis-eye-contact-emotion
**Areas discussed:** Pipeline integration

---

## Pipeline Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Sequential step (Recommended) | Add as Step 5 after speech analysis. Simplest, matches existing pattern with progress bar. Users wait ~60-120s more but see all results when the Dashboard loads. | ✓ |
| Split pipeline — run after | Complete transcription steps first, show transcript + speech results immediately. Run visual analysis as a separate step. | |
| Separate button | Dedicated 'Analyze Eye Contact & Emotion' button on Upload or Dashboard page. Gives users control. | |

**User's choice:** Sequential step (Recommended)
**Notes:** Matches existing pipeline pattern, simplest integration, consistent UX.

---

## the agent's Discretion

- Keyframe sampling strategy — time-based sampling at intervals capped at 20 frames
- Eye contact visualization — percentage metric card + text annotation
- Emotion visualization — dominant emotion badge + distribution display
- No-face error handling — partial results with informative messaging
- Module file structure — single file or split
- Chart type and layout

## Deferred Ideas

None — discussion stayed within phase scope.
