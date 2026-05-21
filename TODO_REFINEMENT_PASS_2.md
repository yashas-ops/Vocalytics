# TODO Refinement Pass 2 (CSS-only, premium SaaS polish)

## Goals
- Preserve baseline tests and all selector contracts.
- Only adjust additive/refinement CSS in:
  - `assets/styles.css`
  - `assets/light.css`
- No changes to routing/session-state/logic in `app.py`.

## Checklist (track progress)
- [x] Premium glassmorphism treatment (deeper layering) on existing surfaces:
  - `.surface-hero`, `.executive-summary`
- [ ] `.surface-muted` glass layering pass

- [ ] Card padding/internal spacing consistency across editorial/metrics/list blocks.
- [ ] DataFrame/table integration into card system (containment + spacing + hover cohesion).
- [x] Uploader prominence + drag/drop hover feedback polish.
- [ ] Dashboard composition depth + visual grouping (CSS-only reinforcement).

- [ ] Background depth layering: radial accents + section separation.
- [ ] Motion polish: standardize hover transition timing for key elements.
- [ ] Mirror all changes in `assets/light.css`.
- [ ] Run `pytest -q` (131 must still pass).
- [ ] Update `TODO.md` checkboxes accordingly.

