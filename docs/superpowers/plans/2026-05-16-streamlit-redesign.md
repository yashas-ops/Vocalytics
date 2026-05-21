# Streamlit Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the Streamlit app to feel launch-ready without changing the existing analysis pipeline, storage model, or business logic.

**Architecture:** Keep the application as a single Streamlit entrypoint, but extract a small presentation-helper layer so UX decisions become testable. Recompose the Upload, Dashboard, and History pages around clearer information hierarchy, then back the redesign with a stronger CSS surface system.

**Tech Stack:** Python, Streamlit, Plotly, pandas, pytest

---

### Task 1: Create testable presentation helpers

**Files:**
- Create: `modules/ui_presenters.py`
- Create: `tests/test_ui_presenters.py`

- [ ] Add helper functions for score summaries, pacing summaries, eye-contact summaries, history labels, and dashboard highlights.
- [ ] Add unit tests that verify the helpers produce the expected copy and prioritization.

### Task 2: Recompose page layouts safely

**Files:**
- Modify: `app.py`

- [ ] Clean corrupted interface strings and navigation labels.
- [ ] Convert the sidebar navigation to a cleaner selection model that still writes through `st.session_state.page`.
- [ ] Turn the upload screen into a guided workflow and redirect successful runs to the Dashboard.
- [ ] Reorganize the Dashboard into summary, insights, and detail sections without touching the underlying analysis calls.
- [ ] Streamline History browsing and report loading while preserving SQLite-backed session restoration.

### Task 3: Strengthen the visual system

**Files:**
- Modify: `assets/styles.css`

- [ ] Introduce a more coherent spacing, surface, and typography system.
- [ ] Add stronger states for navigation, buttons, upload areas, tabs, data sections, and insight cards.
- [ ] Improve responsive behavior and polish empty/loading states using Streamlit-compatible CSS only.
