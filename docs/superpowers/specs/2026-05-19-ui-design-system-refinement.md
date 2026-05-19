# UI Design System Refinement — Design Spec

## Purpose

Fix the frontend UI/UX implementation and visual consistency of the AI Interview Analyzer — light mode upload area, theme toggle contrast, surface hierarchy, card spacing, and light mode completeness.

**Files changed**: `assets/styles.css`, `app.py` (CSS block + upload wrapper only)

---

## 1. Upload Zone Wrapper

**`app.py` — `render_upload_page()`**: Wrap `st.file_uploader()` in `<div class="upload-zone">`. Single parent div, no logic change.

**`styles.css` — new `.upload-zone` class**:
```css
.upload-zone {
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius);
  padding: 1.5rem;
  transition: background 180ms ease, border-color 180ms ease;
}
```

**`styles.css` — uploader internal reset**:
```css
.upload-zone div[data-testid="stFileUploader"] {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
}
.upload-zone div[data-testid="stFileUploadDropzone"] {
  background: transparent !important;
}
```

**Contract**: Native uploader functionality fully preserved (file selection, drag/drop, Streamlit state, upload events, backend integration).

---

## 2. Theme Toggle Fix

**`styles.css` — refine `.stSegmentedControl` tokens**:

Dark mode button-group: keep `background: var(--muted)` (`#0c0c0c`)
Light mode button-group: inherits `--muted` (`#f2f0e8`)

Active button:
```css
.stSegmentedControl button[aria-checked="true"] {
  background: var(--surface-raised) !important;
  color: var(--foreground) !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12),
              0 0 0 1px var(--border-strong);
  z-index: 1;
}
```

---

## 3. Surface Hierarchy & Spacing

**Token retuning**:

| Token | Dark (old → new) | Light (old → new) |
|-------|-----------------|-------------------|
| `--background` | `#050505` → keep | `#faf9f7` → keep |
| `--card` | `#0d0d0d` → keep | `#ffffff` → keep |
| `--muted` | `#0a0a0a` → `#0c0c0c` | `#f0eee6` → `#f2f0e8` |
| `--surface-raised` | `#141414` → keep | `#fdfcf9` → `#f8f7f2` |
| `--surface-inset` | `#030303` → `#000000` | `#e9e5da` → `#ece9e0` |

**Spacing audit** (4px scale enforcement):

| Component | Current | New |
|-----------|---------|-----|
| `.surface` padding | 1.25rem (20px) | **1.5rem (24px)** |
| `.insight-card` padding | 1rem (16px) | **1.25rem (20px)** |
| `.file-summary > div` padding | 1rem (16px) | **1.25rem (20px)** |
| `.checklist > div` padding | 1rem (16px) | **1.25rem (20px)** |
| `.score-lockup` padding | 1.25rem (20px) | **1.5rem (24px)** |
| `.signal-strip > div` padding | 0.75rem 1rem | **1rem 1.25rem** |
| `.detail-list > div` padding | 1rem (16px) | **1.25rem (20px)** |
| `.section-header` margin-bottom | 0.75rem (12px) | **1rem (16px)** |
| `.page-header` margin-bottom | 1.55rem (~25px) | **2rem (32px)** |

---

## 4. Light Mode Completeness

Add explicit overrides for Streamlit internal components in the light-mode `<style>` block:

- Status widget (`stStatusWidget`) — background, text, border
- Alerts — background
- Sidebar radio labels — text color
- Metrics — background
- Tabs — list background, tab colors, selected tab colors
- DataFrames — header background and text
- Expander headers — text color
- Disabled textareas — text and background
- Sidebar collapse buttons — background, border, text

---

## Validation

- Upload flow still works (file selection, drag/drop, save)
- Dashboard still renders with video, transcript, scores, graphs
- History still lists sessions and opens reports
- Theme toggle switches Dark↔Light without Streamlit theme popup
- All Plotly charts render with correct template
- Animations (hover, press, progress fills) still function
- Sidebar collapse/expand controls visible in both themes
- No backend/API regressions
- No state management regressions
