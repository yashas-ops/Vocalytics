# TODO

- [x] Inspect existing `assets/styles.css` for regression-critical selectors and current design tokens.
- [x] Add/adjust a coherent premium SaaS token palette in `assets/styles.css` (dark mode) while preserving legacy token names.
- [x] Improve surface hierarchy: borders, subtle shadows, gradients, radii; keep Streamlit layout intact.
- [x] Refine component-level styles (stButton, stTabs, segmented control, inputs, uploader, expander header) to be Figma-parity without changing behavior.
- [x] Add targeted light-mode overrides (keeping existing light mode behavior) so card text/surface separation matches dark mode.
- [x] Ensure focus-visible outlines and accessibility contrast remain intact in both modes.
- [x] Create a Figma-parity checklist that maps each Figma UI region to a CSS selector + Streamlit structure.
- [ ] Implement remaining Figma parity items (progressive CSS-only).

## Worklist (Figma replication)
- Navbar & Header Composition
  - [x] Premium navbar container exists (`.top-nav*`)
  - [ ] Match exact Figma navbar spacing/typography (width, paddings, font weights)
  - [ ] Verify light-mode navbar tokens

- Layout & Spacing System
  - [ ] Verify page width and vertical rhythm against Figma
  - [ ] Reduce/adjust whitespace per section blocks

- Typography Hierarchy
  - [ ] Compare headings/subtitles/table labels vs Figma

- Card & Surface Design
  - [x] `surface-hero`, `executive-summary`, `surface-muted` exist
  - [ ] Tune card padding & internal spacing per block type
  - [ ] Ensure tone borders + hover states match Figma

- Dashboard composition depth + grouping
  - [ ] Add CSS-only reinforcement where Figma shows extra containment/separation

- Upload/History screens
  - [ ] Upload: uploader dominance + dropzone visuals
  - [ ] History: table/card container spacing + controls

- Background & Visual Depth
  - [ ] Radial/glow accents parity

- Motion & Interaction Polish
  - [ ] Standardize hover/focus transition timings

- Final QA
  - [ ] Run `pytest -q`
  - [ ] Visual compare every page side-by-side with Figma template

## Figma Traceability Checklist
- [ ] Shell navigation / editorial rail -> persistent chrome, latest-session context, restrained navigation -> top nav + shell wrappers -> `.top-nav*`, branding hooks, nav button selectors
- [ ] Page header pattern -> calm title stack with divider transition -> all page headers -> `.page-header`, `.page-eyebrow`, `.page-description`
- [ ] Upload lead module -> "new session" primary intake surface -> Upload hero block -> `.surface-hero`, uploader selectors
- [ ] Upload evidence row -> file metadata as archival evidence -> upload file summary -> `.file-evidence`
- [ ] Upload secondary guidance -> structured quiet supporting content -> report coverage list -> `.section-list`
- [ ] Dashboard score anchor -> dossier-style lead score and summary -> executive summary shell -> `.score-editorial`, `.executive-summary`
- [ ] Dashboard evidence row -> supporting metrics in divided band -> signal strip -> `.evidence-grid`
- [ ] Dashboard interpretation modules -> restrained report sections instead of dashboard cards -> insight and detail regions -> `.insight-grid`, `.insight-card`, `.detail-list`
- [ ] Dashboard detail navigation -> quiet sectional switching -> tabs area -> `.stTabs` selectors
- [ ] History archive summary -> restrained summary metrics band -> history top stats -> `archive-summary` hook + metric row selectors
- [ ] History archive body -> scan-friendly records plus reopen panel -> table and resume panel surfaces -> `.surface`, dataframe selectors, selectbox/button selectors
- [ ] Light theme tokens -> warm paper-like editorial mode -> global light shell -> `assets/light.css`, light token injection in `app.py`
- [ ] Dark theme tokens -> restrained charcoal editorial mode -> global dark shell -> `.stApp` tokens in `assets/styles.css`

