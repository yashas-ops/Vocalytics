# Implementation Plan

[Overview]
Refine the existing Streamlit frontend styling to a more premium, consistent color system that fixes light-mode readability/contrast issues while preserving all layouts, workflows, animations, interactions, and backend logic.

The app is a Streamlit UI styled via `assets/styles.css` with a small light-mode override embedded directly in `app.py` (`load_css()` sets CSS variables for `.stApp`). The CSS defines a restrained design system (surfaces, borders, typography colors, tone borders, buttons, tabs, segmented controls, and various custom “surface-*” container variants). The light-mode readability complaints are likely caused by mismatched variable values (e.g., `--text-muted`, `--text-soft`, `--border` and derived surface/border colors), plus cases where Streamlit’s default components still render with styles that our CSS only partially overrides.

High-level approach:
- Keep the current component structure and HTML class hooks (`surface-hero`, `surface-muted`, `insight-card`, `detail-list`, `score-lockup`, `tone-success/warning/error/info`, `.stButton`, `.stTabs`, etc.) unchanged.
- Improve visual consistency by tightening the semantic palette (graphite/slate + warm neutrals) and ensuring all text used inside card-like surfaces has sufficient contrast in BOTH theme modes.
- Increase surface hierarchy using borders/shadows that are subtle but clearly separating.
- Fix light-mode contrast by adjusting light theme CSS variables and adding targeted CSS overrides for card text and Streamlit’s internal text (where it blends).
- Preserve existing animations/transitions already present in CSS; refine them to be smoother/subtler without removing any transitions or changing their presence.

No backend logic will be modified.

[Types]  
No type system changes are required.

[Files]
Modify existing frontend style files only:
- Existing: `assets/styles.css` (update token palette defaults, improve light-mode and cross-mode contrast rules, add targeted overrides for card text and Streamlit widgets, refine hover/focus states, and ensure tone styles are consistent).
- Existing: `app.py` (only adjust the embedded Light-mode CSS variable overrides inside `load_css()` so that card text/surfaces/borders remain readable; no workflow/logic changes).

No new files are required.

[Functions]
No Python functions will be functionally changed; only the CSS variable values inside `load_css(theme: str)` for the Light theme will be updated.

[Classes]
No classes (in the OOP sense) will be modified/added.

[Dependencies]
No dependencies will be added/changed.

[Testing]
Testing will be performed as a visual + regression smoke check:
- Run the Streamlit app and manually verify Upload, Dashboard (all tabs), and History screens in BOTH Dark and Light modes.
- Validate that all animations and transitions remain present (no removal of transitions/hover/focus behaviors).
- Validate light-mode requirements: all card text remains clearly visible; no sections blend into backgrounds; surface separation remains visible; contrast is consistent.
- Validate dark-mode tone consistency: surfaces/borders and tone outlines remain restrained (no pure-black extremes, no neon/glow).

[Implementation Order]
1. Update code knowledge alignment: inspect current `assets/styles.css` and Light-mode tokens embedded in `app.py` to identify which variables drive card text/surface/border contrast.
2. Create a semantic palette update in `assets/styles.css` for borders, text-muted/text-soft, surfaces, shadows, and tone colors; ensure derived states (hover/focus/tabs/buttons/segments) use those tokens.
3. Fix light-mode specifically by adjusting Light theme CSS variables in `app.py`’s `load_css()` so derived components (including custom cards) meet contrast targets.
4. Add targeted CSS overrides inside `assets/styles.css` for any card text elements that are currently inheriting insufficient colors in Light mode (without changing layout or removing functionality).
5. Refine hover/focus states and separators for premium feel (slightly smoother transitions, consistent border thickness, subtle shadow elevation) while keeping existing interaction feedback.
6. Smoke test: run app, switch themes, and visually inspect major screens and all card-like components for contrast and hierarchy.
7. Run unit tests (if applicable) to ensure no accidental regressions in Python/UI rendering.

