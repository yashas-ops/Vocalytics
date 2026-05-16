# Phase 1: Core Infrastructure & Data Models - Context

**Gathered:** 2026-05-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Project skeleton, shared data contracts, SQLite database schema, file management utilities, Streamlit entrypoint app with page navigation and dark theme, and ML model caching infrastructure. This is the foundation that all subsequent pipeline phases build on. No analysis logic is implemented here — just the scaffolding and shared types.

</domain>

<decisions>
## Implementation Decisions

### Project Structure
- **D-01:** Entry point file named `app.py` (conventional, matches PRD specification)
- **D-02:** Single `app.py` with Streamlit page routing managed internally (not `pages/` dir, not `st.navigation`) — keeps it simple for MVP
- **D-03:** Python 3.11 pinned in `runtime.txt` and `requirements.txt` — faster-whisper requires <3.12
- **D-04:** Folder structure follows PRD spec: `modules/`, `utils/`, `assets/`, `database/`, `uploads/`, `temp/`, `reports/`
- **D-05:** All shared Pydantic models in a single `modules/models.py` file (not split per stage)

### Database Schema
- **D-06:** Single `interviews` table in SQLite (not normalized across multiple tables) — sufficient for single-user local app
- **D-07:** WAL mode enabled for concurrent reads during analysis writes
- **D-08:** Confidence score heuristic formula structure defined in schema from Phase 1 (not deferred to Phase 5) — fields for eye_contact_score, filler_score, pacing_score, composite confidence

### Dark Theme
- **D-09:** Streamlit built-in dark mode via `.streamlit/config.toml` as the base
- **D-10:** Custom CSS in `assets/styles.css` for polish (cards, progress bars, layout refinements)
- **D-11:** Color scheme: dark blue/navy palette (professional, recruiter-impressive — Vercel/Linear-style)

### ML Model Caching
- **D-12:** Models loaded via `@st.cache_resource` decorator — each model loads exactly once per session
- **D-13:** Model loading functions in `utils/helpers.py` (clean separation from app logic)

### Agent's Discretion
- Exact Streamlit page structure within `app.py` (how pages are organized, the Upload/Dashboard/History tab layout)
- SQLite column types and exact field names (follow standard conventions)
- CSS class names and specific color values (within dark navy palette)
- File management utility function signatures

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

No external specs or ADRs — requirements fully captured in decisions above and the following project docs:

- `CLAUDE.md` — Project context, tech stack constraints, CPU optimization patterns
- `.planning/ROADMAP.md` §Phase 1 — Phase goal and success criteria
- `.planning/REQUIREMENTS.md` §UI/UX — UI-01 requirement definition
- `.planning/research/STACK.md` — Technology stack with versions, CPU optimization code, compatibility matrix
- `.planning/research/ARCHITECTURE.md` — Pipeline architecture, component boundaries, build order

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — greenfield project, no existing code

### Established Patterns
- Streamlit-only architecture (no separate frontend framework)
- Python 3.11 standard library patterns

### Integration Points
- `modules/` directory will receive pipeline modules from Phases 2-5
- `database/app.db` will be read by all downstream phases
- `uploads/` and `temp/` managed here, consumed by Phase 2+

</code_context>

<specifics>
## Specific Ideas

- Recruiter-impressive SaaS-style dashboard aesthetic
- Dark navy palette inspired by Vercel/Linear dark mode
- Clean cards, progress bars, analytics charts as the visual foundation

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-core-infrastructure-data-models*
*Context gathered: 2026-05-16*
