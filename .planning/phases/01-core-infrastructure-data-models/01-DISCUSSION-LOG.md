# Phase 1: Core Infrastructure & Data Models - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-16
**Phase:** 1-Core Infrastructure & Data Models
**Areas discussed:** Project Structure, Data Models & DB Schema, Dark Theme

---

## Project Structure

| Option | Description | Selected |
|--------|-------------|----------|
| app.py (Recommended) | Clean, conventional, matches PRD spec | ✓ |
| streamlit_app.py | Explicit naming, Streamlit auto-detects on run | |
| No preference | Either is fine | |

**User's choice:** app.py
**Notes:** User prefers conventional naming matching their PRD spec.

| Option | Description | Selected |
|--------|-------------|----------|
| st.navigation (Recommended) | Modern routing with st.navigation + st.Page (v1.36+) | |
| pages/ directory | Streamlit's built-in auto-routing | |
| Single app.py | All routing in one file | ✓ |

**User's choice:** Single app.py
**Notes:** User wants simplicity — keep all page routing in one file. No separate page directory.

| Option | Description | Selected |
|--------|-------------|----------|
| Python 3.11 (Recommended) | Required for faster-whisper compatibility | ✓ |
| Python 3.12 | No faster-whisper wheel currently available | |
| Skip pinning | Risk of version mismatch | |

**User's choice:** Python 3.11
**Notes:** Pin to 3.11 based on research — faster-whisper caps at 3.11.

---

## Data Models & DB Schema

| Option | Description | Selected |
|--------|-------------|----------|
| Single models.py (Recommended) | All Pydantic models in one file | ✓ |
| Separate files per stage | One file per pipeline stage | |

**User's choice:** Single models.py
**Notes:** Keep it simple for Phase 1 — all models in one file.

| Option | Description | Selected |
|--------|-------------|----------|
| Single interviews table | One table with all fields | ✓ |
| Multiple normalized tables | Separate tables for each concern | |

**User's choice:** Single interviews table
**Notes:** Sufficient for single-user local app. Simple is better.

| Option | Description | Selected |
|--------|-------------|----------|
| Yes (Recommended) | Define confidence fields in schema from Phase 1 | ✓ |
| Later in Phase 5 | Add confidence fields when implementing scoring | |

**User's choice:** Yes
**Notes:** Include confidence score component fields in the schema from the start.

---

## Dark Theme

| Option | Description | Selected |
|--------|-------------|----------|
| Built-in + custom CSS (Recommended) | Streamlit config.toml + assets/styles.css | ✓ |
| Built-in only | Just Streamlit dark mode via config.toml | |
| Custom CSS only | Full custom override | |

**User's choice:** Built-in + custom CSS
**Notes:** Streamlit's built-in dark mode as base, custom CSS for polish.

| Option | Description | Selected |
|--------|-------------|----------|
| Dark blue/navy (Recommended) | Professional, Vercel/Linear-style | ✓ |
| True dark (pure black) | AMOLED-style high contrast | |
| Your call | Agent discretion | |

**User's choice:** Dark blue/navy
**Notes:** Professional recruiter-impressive aesthetic.

---

## Agent's Discretion

- Exact Streamlit page structure within `app.py` (how pages are organized)
- SQLite column types and exact field names
- CSS class names and specific color values (within dark navy palette)
- File management utility function signatures

## Deferred Ideas

None.
