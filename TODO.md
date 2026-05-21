# TODO

- [x] Inspect existing `assets/styles.css` for regression-critical selectors and current design tokens.
- [x] Add/adjust a restrained editorial token palette in `assets/styles.css` (dark mode) while preserving legacy token names.
- [x] Improve surface hierarchy with dividers, quiet fills, and low radii while keeping the Streamlit layout intact.
- [x] Refine component-level styles (stButton, stTabs, segmented control, inputs, uploader, expander header) to match the Read.cv shell without changing behavior.
- [x] Add targeted light-mode overrides (keeping existing light mode behavior) so card text/surface separation matches dark mode.
- [x] Ensure focus-visible outlines and accessibility contrast remain intact in both modes.
- [x] Create a Figma-parity checklist that maps each Figma UI region to a CSS selector + Streamlit structure.
- [x] Implement remaining Figma parity items (progressive CSS-only).

## Worklist (Figma replication)
- Navbar & Header Composition
  - [x] Premium navbar container exists (`.top-nav*`)
  - [x] Match exact Figma navbar spacing/typography (width, paddings, font weights)
  - [x] Verify light-mode navbar tokens

- Layout & Spacing System
  - [x] Verify page width and vertical rhythm against Figma
  - [x] Reduce/adjust whitespace per section blocks

- Typography Hierarchy
  - [x] Compare headings/subtitles/table labels vs Figma

- Card & Surface Design
  - [x] `surface-hero`, `executive-summary`, `surface-muted` exist
  - [x] Tune card padding & internal spacing per block type
  - [x] Ensure tone borders + hover states match Figma

- Dashboard composition depth + grouping
  - [x] Add CSS-only reinforcement where Figma shows extra containment/separation

- Upload/History screens
  - [x] Upload: uploader dominance + dropzone visuals
  - [x] History: table/card container spacing + controls

- Background & Visual Depth
  - [x] Keep the page background restrained and avoid glossy accent treatments

- Motion & Interaction Polish
  - [x] Standardize hover/focus transition timings

- Final QA
  - [x] Run `pytest -q`
  - [ ] Visual compare every page side-by-side with Figma template

## Figma Traceability Checklist
- [x] Shell navigation / editorial rail -> persistent chrome, latest-session context, restrained navigation -> top nav + shell wrappers -> `.top-nav*`, branding hooks, nav button selectors
- [x] Page header pattern -> calm title stack with divider transition -> all page headers -> `.page-header`, `.page-eyebrow`, `.page-description`
- [x] Upload lead module -> "new session" primary intake surface -> Upload hero block -> `.surface-hero`, uploader selectors
- [x] Upload evidence row -> file metadata as archival evidence -> upload file summary -> `.file-evidence`
- [x] Upload secondary guidance -> structured quiet supporting content -> report coverage list -> `.section-list`
- [x] Dashboard score anchor -> dossier-style lead score and summary -> executive summary shell -> `.score-editorial`, `.executive-summary`
- [x] Dashboard evidence row -> supporting metrics in divided band -> signal strip -> `.evidence-grid`
- [x] Dashboard interpretation modules -> restrained report sections instead of dashboard cards -> insight and detail regions -> `.insight-grid`, `.insight-card`, `.detail-list`
- [x] Dashboard detail navigation -> quiet sectional switching -> tabs area -> `.stTabs` selectors
- [x] History archive summary -> restrained summary metrics band -> history top stats -> `archive-summary` hook + metric row selectors
- [x] History archive body -> scan-friendly records plus reopen panel -> table and resume panel surfaces -> `.surface`, dataframe selectors, selectbox/button selectors
- [x] Light theme tokens -> warm paper-like editorial mode -> global light shell -> `assets/light.css`, light token injection in `app.py`
- [x] Dark theme tokens -> restrained charcoal editorial mode -> global dark shell -> `.stApp` tokens in `assets/styles.css`

