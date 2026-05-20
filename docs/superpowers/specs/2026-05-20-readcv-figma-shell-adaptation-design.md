# Read.cv Figma Shell Adaptation - Design Spec

## Purpose

Adapt the existing Streamlit app shell to closely follow the visual language of the Figma Community file `1501274937411138885/read-cv-template`, using it as a visual system reference rather than a literal page clone.

The result should preserve all existing analyzer behavior while giving the full app a consistent editorial structure across:

- Upload
- Dashboard
- History

## Source Reference

Primary design reference:

- Figma Community file `1501274937411138885`
- Identified title: `read-cv-template`

Observed design traits to preserve:

- Editorial composition instead of dashboard-card density
- Quiet typography-led hierarchy
- Thin dividers as the primary structural device
- Minimal radii and restrained surfaces
- Warm light palette and soft near-black dark palette
- Metadata rows and modular sections that feel archival/profile-like
- Low-decoration interaction styling

## Agreed Approach

Use a semantic shell adaptation approach.

This means:

- Keep the current Streamlit runtime, routes, widgets, and backend logic
- Re-author surrounding markup hooks and CSS structure so the interface reads like a Read.cv-style editorial product shell
- Allow app-specific adaptation where uploader, charts, tabs, or history tables need more product-style ergonomics
- Avoid forcing a literal page-for-page copy of the Figma template

## Non-Goals

- No changes to analysis, upload, database, transcription, scoring, or session-state logic
- No replacement of Streamlit
- No new external services or APIs
- No generic glossy SaaS dashboard treatment
- No pixel-perfect clone claims where Streamlit structure makes that unrealistic

## Architecture

Treat the Figma as a visual system and composition reference, not a static page blueprint.

The app remains a three-page Streamlit product:

- `Upload`
- `Dashboard`
- `History`

Each page should be rewritten into the same shared shell grammar:

- quiet page headers
- thin divider-led sectioning
- restrained surfaces
- evidence-first metadata rows
- warm light theme
- restrained dark theme

The app should feel like one cohesive editorial tool rather than three independently styled screens.

## Page Mapping

### Upload -> New Session

The Upload page becomes a calm intake surface:

- clear editorial header
- strong uploader module
- compact process/status metadata row
- file summary shown as evidence blocks
- secondary guidance shown as a quiet structured list

The uploader remains the dominant interactive element, but the surrounding structure should feel intentional and spacious rather than widget-first.

### Dashboard -> Interview Dossier

The Dashboard becomes a dossier-style review page:

- score as the typographic anchor
- concise interpretation and coaching summary
- supporting metrics in thin divided evidence rows
- interpretation modules presented like profile/report sections
- transcript, feedback, and evidence panels aligned with the same shell language

Charts and tabs remain, but their containers should be visually subordinate to the editorial structure.

### History -> Archive Index

The History page becomes a clean archive:

- summary stats as a restrained archive band
- saved sessions in a scan-friendly table module
- reopen flow in a compact metadata panel
- empty state written in the same editorial voice as the other pages

## Visual System

### Layout

- Keep the current wide layout, but use disciplined vertical rhythm
- Prefer full-width section bands and thin dividers over stacked floating cards
- Use spacing to establish hierarchy before relying on borders or fills

### Surfaces

- Radius should stay low, generally `0-6px`
- Borders should do most of the structural work
- Shadows should be absent or barely perceptible
- Surfaces should feel quiet and paper-like, not glossy

### Typography

- Use calm title sizing rather than marketing hero scale
- Use compact section headings
- Use small metadata labels sparingly and consistently
- Keep body text readable and restrained
- Avoid decorative tracking and excessive uppercase

### Color

Light mode:

- warm off-white page background
- near-white module surfaces
- thin gray-brown dividers
- near-black body text
- softened secondary text

Dark mode:

- near-black or charcoal page background
- slightly raised dark surfaces
- soft off-white primary text
- muted neutral secondary text
- limited accent use

## Shared Shell Components

### Navigation / Rail

The persistent shell should read like a quiet editorial index:

- restrained branding
- minimal navigation emphasis
- compact latest-session context
- dividers separating informational blocks

Whether the shell is rendered through the hidden native sidebar, the custom top navigation, or both, the visible result should feel consistent with the same Read.cv-style structure.

### Headers

All pages should open with:

- a short eyebrow or contextual label
- a clear title
- one restrained description line
- a divider establishing the transition into content

### Evidence Rows

Evidence rows are a core translation pattern from the Figma language into the analyzer:

- Upload file summary
- Dashboard supporting metrics
- History summary metrics

These should use a consistent pattern of divided columns, subdued labels, and strong values.

## Traceability And Anti-Hallucination Checklist

Implementation must be grounded in an explicit mapping from design pattern to real app hook.

Each checklist entry should follow this structure:

`Figma pattern -> intended meaning in app -> app region -> concrete selector/class/hook`

Required mapping groups:

1. Shell and navigation
2. Page header pattern
3. Upload lead module
4. Upload evidence row
5. Dashboard score anchor
6. Dashboard evidence row
7. Dashboard interpretation modules
8. Tabs and detail surfaces
9. History archive summary row
10. History table and reopen panel
11. Light theme tokens
12. Dark theme tokens

This checklist should be kept in-repo during implementation so every major styling choice can be traced back to a named reference pattern instead of intuition alone.

## Likely Implementation Files

- `app.py`
  - adjust semantic HTML hooks and helper markup
  - preserve all workflows and state logic

- `assets/styles.css`
  - define the main dark-shell visual system
  - style Streamlit widgets into the editorial shell

- `assets/light.css`
  - align the light theme with the same system

- `TODO.md`
  - maintain the Figma traceability checklist and verification items

- tests only if existing UI-shell assertions need updates to reflect deliberate hook changes

## Verification Plan

Verification should happen in two passes.

### 1. Structural Verification

Confirm that:

- each planned shell hook exists in `app.py`
- each mapped selector exists in CSS
- the traceability checklist is updated as work completes

### 2. Behavioral Verification

Confirm that:

- Upload page still accepts valid files
- analyzer flow still runs
- Dashboard still renders score, transcript, feedback, charts, and tabs
- History still lists sessions and reopens a selected report
- theme switching still works
- no partial HTML wrappers leak into the UI

## Acceptance Criteria

- The app clearly reads as a Read.cv-style editorial interface rather than a generic Streamlit dashboard
- Upload, Dashboard, and History share one coherent shell language
- Existing functionality remains intact
- The implementation is backed by an explicit Figma-to-app traceability checklist
- The final result is faithful in tone, hierarchy, spacing, and color system without making false claims of literal page cloning
