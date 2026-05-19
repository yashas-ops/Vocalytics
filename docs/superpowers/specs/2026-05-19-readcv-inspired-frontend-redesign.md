# Read.cv-Inspired Frontend Redesign - Design Spec

## Purpose

Redesign the AI Interview Analyzer frontend so the application closely follows the visual identity of the supplied Figma Community template: `1501274937411138885/read-cv-template`.

The template direction is intentionally minimalist rather than a conventional SaaS dashboard. The app should adopt its restrained, typographic, whitespace-led, modular presentation while preserving every existing Streamlit workflow and backend behavior.

## Design Reference

Primary reference: Read.cv / Figma Sites resume template.

Observed traits to translate into the app:

- Editorial, "show, don't tell" composition.
- Strong typography hierarchy with quiet supporting text.
- Generous whitespace and clear section rhythm.
- Thin grey dividers instead of heavy surface chrome.
- Modular content blocks that feel like profile/resume sections.
- Minimal interaction states and low-decoration UI.
- Warm light mode and restrained near-black dark mode.

This redesign must not drift into a generic SaaS/admin template. Analytics widgets should feel like evidence sections in a minimalist professional profile, not glossy dashboard cards.

## Non-Goals

- No backend, analysis, database, upload, transcription, report, or history logic changes.
- No replacement of Streamlit as the frontend runtime.
- No new paid services, cloud dependencies, or external APIs.
- No generic admin dashboard visual language.
- No decorative gradients, oversized marketing hero, or flashy SaaS chrome.

## Application Structure

The app remains a Streamlit application with three routes:

- Upload
- Dashboard
- History

The redesign changes the presentation layer in `app.py` and `assets/styles.css` only, unless a test update is required to reflect deliberate markup class changes.

Existing helpers such as `surface_start`, `surface_end`, `render_page_header`, `render_section_header`, `render_sidebar`, and chart construction can be adapted, but the analysis pipeline and session state keys must remain stable.

## Visual System

### Layout Language

Use a minimalist editorial grid:

- Main content max width expands slightly from the current dashboard feel but remains readable.
- Pages begin with a simple text header and horizontal rule rhythm.
- Major sections are stacked as content bands or thin-bordered modules.
- Avoid the feeling of isolated dashboard tiles floating on a dark canvas.
- Prefer label/value rows, section lists, and quiet grids over bulky card stacks.

### Surface Styling

Replace heavy card treatment with Read.cv-like modules:

- Radius: mostly 0-6px, avoiding rounded SaaS cards.
- Borders: 1px thin neutral lines.
- Shadows: none or nearly imperceptible.
- Background layering: subtle surface shifts only.
- Internal dividers: frequent and intentional, especially for metric rows.

Hero surfaces become editorial lead sections rather than glossy panels.

### Typography

Use Inter/system sans-serif with a profile-like hierarchy:

- Page titles: calm, text-first, no marketing scale.
- Section titles: compact and high-contrast.
- Labels: small, neutral, regular or medium weight.
- Values: larger only where data hierarchy demands it.
- Body copy: restrained line height and readable contrast.

Avoid negative letter spacing and excessive uppercase. Uppercase may remain only for compact metadata labels.

### Color

Light mode:

- Warm off-white page background.
- White or near-white modules.
- Neutral grey dividers.
- Near-black primary text.
- Muted grey secondary text.
- Very limited accent color.

Dark mode:

- Near-black / charcoal page background.
- Slightly raised dark modules.
- Thin charcoal/grey dividers.
- Soft off-white primary text.
- Muted grey secondary text.
- Accent used sparingly for selected state, progress, and chart emphasis.

Both themes must maintain readable contrast without harsh black blocks or washed-out cards.

## Sidebar

Redesign the sidebar as a quiet profile/index rail:

- Brand area resembles a profile header: app name, concise descriptor, local-first/version metadata.
- Navigation is a minimal vertical index with thin active indicator and restrained hover state.
- Avoid bulky button rows or pill-heavy styling.
- Theme toggle is visually quiet and aligned with the sidebar rhythm.
- Latest session and current flow become compact metadata sections separated by thin dividers.

Functionality preserved:

- `st.segmented_control` continues to switch Dark/Light.
- `st.radio` continues to control `st.session_state.page`.
- Latest session context continues to read from session state.

## Upload Page

Transform upload into a minimalist "new entry" screen:

- Header presents the action plainly, in the Read.cv editorial voice.
- Upload area becomes a large quiet module with thin dashed border and clear text hierarchy.
- Process strip becomes inline metadata, not rounded SaaS pills.
- File summary becomes a compact three-column evidence row with dividers.
- Report coverage becomes a minimal section list rather than checklist cards.

Functionality preserved:

- Native `st.file_uploader` remains the internal upload mechanism.
- Drag/drop, file type restrictions, upload state, validation, and `Analyze interview` button remain intact.
- `run_analysis_pipeline` remains unchanged unless class wrappers are needed around UI only.

## Dashboard Page

Transform dashboard into a minimalist interview review dossier:

- Overall confidence score becomes the typographic anchor of the page.
- Executive summary uses a large score/value plus concise interpretation text.
- Coaching takeaways become editorial modules with thin borders and restrained tone indicators.
- Signal strip becomes a quiet metadata grid with dividers.
- Tabs remain for information architecture, but styling should feel like a minimal segmented index.
- Transcript, feedback, filler breakdown, metadata, video, and visual evidence remain available.

Composition:

- Lead section: score, classification, concise guidance.
- Supporting section: source video or session record.
- Evidence strip: compact key metrics.
- Detail sections: interpretation, transcript/feedback, evidence.

Functionality preserved:

- Empty dashboard state still routes to Upload.
- `st.video`, `st.metric`, `st.tabs`, `st.text_area`, `st.expander`, `st.dataframe`, and chart rendering continue to work.
- Session-state driven dashboard data remains unchanged.

## Charts And Data Visualization

Charts should integrate as minimalist evidence panels:

- Transparent plot background.
- Muted axes and gridlines.
- Thin borders around chart containers.
- Sparse color scale.
- No glossy, neon, or high-saturation chart language.
- Font colors must follow active theme tokens.

Plotly configuration remains in Python, but chart colors should align with the new light/dark token system.

## History Page

Transform history into a clean archive:

- Summary metrics become a thin four-column stats row.
- Session table sits in a quiet archive module.
- Resume selected report panel becomes a compact metadata block.
- Empty state follows the same editorial section pattern as Upload/Dashboard.

Functionality preserved:

- `fetch_all_interviews`, `fetch_interview`, history labels, selector, and dashboard reload behavior remain unchanged.

## Interaction And Motion

Keep interactions polished but minimal:

- Hover states use subtle background and border shifts.
- Buttons may translate by at most 1px or simply change tone.
- Focus states remain visible and accessible.
- Avoid decorative motion.
- Respect the existing Streamlit rerun/navigation behavior.

## Accessibility

The redesign must preserve or improve:

- Text contrast in both themes.
- Visible focus outlines.
- 44px minimum button/touch height where Streamlit widgets allow it.
- Clear labels for upload, select, tab, and navigation controls.
- No information conveyed by color alone.

## Implementation Boundaries

Likely files:

- `app.py`
  - Add or rename CSS hooks for editorial modules.
  - Adjust helper-rendered HTML markup for sidebar, upload, summary, metrics, and history.
  - Preserve all function signatures and data flow.

- `assets/styles.css`
  - Replace current premium SaaS card system with Read.cv-inspired tokens and modules.
  - Restyle Streamlit internals for sidebar, uploader, tabs, buttons, metrics, dataframe, status, and collapse controls.
  - Add responsive rules for mobile/narrow widths.

- Tests
  - Update only if existing tests assert old CSS class names or markup shape.

## Validation Plan

Run automated checks:

- `pytest`

Run visual/runtime checks when feasible:

- Start Streamlit locally.
- Verify Upload page loads and uploader remains usable.
- Verify Dashboard empty state.
- If existing session data is present, verify dashboard, charts, transcript, and history reload.
- Verify Dark and Light theme toggle.
- Check responsive layout at narrow and desktop widths.

## Acceptance Criteria

- The app no longer resembles default Streamlit or the prior premium SaaS card layout.
- The visual identity clearly tracks the Read.cv template: minimalist, typographic, modular, whitespace-led, and restrained.
- Sidebar feels like a quiet Read.cv-style index/profile rail.
- Upload, dashboard, cards/modules, chart containers, history, and both themes are visibly redesigned.
- All existing analysis, upload, reporting, history, graph, session state, and navigation functionality remains intact.
