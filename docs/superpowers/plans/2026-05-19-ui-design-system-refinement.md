# UI Design System Refinement — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the frontend UI/UX and visual consistency — light mode upload area, theme toggle contrast, surface hierarchy, card spacing, and light mode completeness.

**Architecture:** Keep the single `app.py` entrypoint unchanged functionally. Modify `assets/styles.css` (952 lines) for all visual token and component refinements. Add a `.upload-zone` wrapper `<div>` in `render_upload_page()`. Append explicit `[data-testid]` light-mode overrides in `app.py`'s `load_css()` function. No backend, state, or routing changes.

**Tech Stack:** CSS custom properties, Streamlit CSS selectors, Python string templates

---

### Task 1: Add upload-zone wrapper to app.py

**Files:**
- Modify: `app.py:492-496`
- Test: Manual visual check only (no CSS yet)

- [ ] **Wrap `st.file_uploader()` in upload-zone div**

In `render_upload_page()`, find:

```python
uploaded_file = st.file_uploader(
    "Interview video",
    type=["mp4", "mov", "avi"],
    help="Maximum recommended size: 500 MB",
)
```

Wrap with:

```python
st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Interview video",
    type=["mp4", "mov", "avi"],
    help="Maximum recommended size: 500 MB",
)
st.markdown('</div>', unsafe_allow_html=True)
```

- [ ] **Verify no functionality change** — file uploader still renders, drag/drop still works, help text still shows

---

### Task 2: Add upload-zone CSS class and reset native uploader styles

**Files:**
- Modify: `assets/styles.css`

- [ ] **Add `.upload-zone` class** after the existing file uploader section (after line 396):

```css
/* ── Upload zone wrapper (replaces raw uploader visual) ── */

.upload-zone {
  background: color-mix(in srgb, var(--muted) 85%, transparent);
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius);
  padding: 1.5rem;
  transition: background 180ms ease, border-color 180ms ease;
}

.upload-zone:hover {
  background: color-mix(in srgb, var(--muted) 70%, var(--card));
  border-color: color-mix(in srgb, var(--primary) 34%, var(--border-strong));
}
```

- [ ] **Reset native uploader styles inside the wrapper** (add after the above):

```css
.upload-zone div[data-testid="stFileUploader"] {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  margin: 0 !important;
}

.upload-zone div[data-testid="stFileUploader"]:hover {
  background: transparent !important;
  border-color: transparent !important;
}

.upload-zone div[data-testid="stFileUploadDropzone"] {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  margin: 0 !important;
}

.upload-zone div[data-testid="stFileUploadDropzone"] * {
  color: var(--foreground) !important;
}

.upload-zone div[data-testid="stFileUploadDropzone"] small {
  color: var(--muted-foreground) !important;
}

.upload-zone div[data-testid="stFileUploadDropzone"] svg {
  fill: var(--muted-foreground) !important;
  color: var(--muted-foreground) !important;
}
```

---

### Task 3: Fix theme toggle contrast

**Files:**
- Modify: `assets/styles.css:220-242`

- [ ] **Replace existing segmented control CSS** (lines 220-242) with:

```css
/* ═══════════════════════════════════════════════
   THEME TOGGLE — Segmented Control
   ═══════════════════════════════════════════════ */

.stSegmentedControl [data-baseweb="button-group"] {
  background: var(--muted);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.2rem;
}

.stSegmentedControl button {
  border-radius: 6px !important;
  min-height: 34px;
  font-size: 0.82rem;
  font-weight: 560;
  color: var(--muted-foreground) !important;
  background: transparent !important;
  border: 1px solid transparent !important;
  transition: background 160ms ease, color 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
  cursor: pointer;
  position: relative;
  z-index: 0;
}

.stSegmentedControl button[aria-checked="true"] {
  background: var(--surface-raised) !important;
  color: var(--foreground) !important;
  border-color: var(--border-strong) !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  z-index: 1;
}
```

---

### Task 4: Retune surface token values for visual hierarchy

**Files:**
- Modify: `assets/styles.css:7-46` (dark mode tokens)
- Modify: `app.py:64-96` (light mode tokens)

- [ ] **Update dark mode `--muted`** in `styles.css` line 13:
```css
--muted: #0c0c0c;
```

- [ ] **Add dark mode `--surface-inset`** update at line 27:
```css
--surface-inset: #000000;
```

- [ ] **Update light mode tokens** in `app.py:64-96`:

Change line 68 (`--muted`):
```css
--muted: #f2f0e8;
```

Change line 79 (`--surface-raised`):
```css
--surface-raised: #f8f7f2;
```

Change line 81 (`--surface-inset`):
```css
--surface-inset: #ece9e0;
```

Also tighten shadows for light mode (lines 93-94) to be slightly more visible:
```css
--shadow: 0 16px 36px rgba(31, 34, 31, 0.08);
--shadow-soft: 0 8px 18px rgba(31, 34, 31, 0.06);
```

---

### Task 5: Update all component paddings to strict 4px spacing scale

**Files:**
- Modify: `assets/styles.css`

- [ ] **Surface container padding** (line 290): `1.25rem` → `1.5rem`
- [ ] **Insight card padding** (line 529): `1rem` → `1.25rem`
- [ ] **File summary boxes** (line 412): `padding: 1rem` → `padding: 1.25rem`
- [ ] **Checklist items** (line 447): `padding: 1rem` → `padding: 1.25rem`
- [ ] **Score lockup padding** (line 477): `1.25rem` → `1.5rem`
- [ ] **Signal strip items** (line 594-596): `0.75rem 1rem` → `1rem 1.25rem`
- [ ] **Detail list items** (line 683-684): `padding: 1rem` → `padding: 1.25rem`
- [ ] **Section header margin-bottom** (line 316): `0.75rem` → `1rem`
- [ ] **Page header margin-bottom** (line 249): `1.55rem` → `2rem`
- [ ] **Insight grid gap** (line 521): `0.75rem` → `1rem`
- [ ] **Process strip gap** (line 341): `0.75rem` → `1rem`
- [ ] **File summary gap** (line 403): `0.75rem` → `1rem`
- [ ] **Checklist gap** (line 439): `0.75rem` → `1rem`

---

### Task 6: Add complete light mode overrides for Streamlit internals

**Files:**
- Modify: `app.py:62-99` (extend the light mode `<style>` block)

- [ ] **Append after the existing light mode `</style>` close** — add overrides inside the same block before `</style>`:

```css
/* Streamlit internal component overrides */
div[data-testid="stStatusWidget"] {
    background: #ffffff !important;
    border-color: rgba(0, 0, 0, 0.08) !important;
}
div[data-testid="stStatusWidget"] * {
    color: #171a19 !important;
}
.stAlert {
    background: #ffffff !important;
    border-color: rgba(0, 0, 0, 0.08) !important;
}
section[data-testid="stSidebar"] .stRadio label p {
    color: #171a19 !important;
}
section[data-testid="stSidebar"] .stRadio label:has(input:checked) p {
    color: #171a19 !important;
}
div[data-testid="stMetric"] {
    background: #ffffff !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #f2f0e8 !important;
}
.stTabs [data-baseweb="tab"] {
    color: #5b635e !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: #f8f7f2 !important;
    color: #171a19 !important;
}
.stDataFrame thead tr th {
    background: #f2f0e8 !important;
    color: #5b635e !important;
}
.streamlit-expanderHeader {
    color: #171a19 !important;
}
textarea:disabled {
    color: #3f4742 !important;
    background: #f2f0e8 !important;
}
/* Sidebar collapse buttons in light mode */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] {
    background-color: #f2f0e8 !important;
    border-color: rgba(0, 0, 0, 0.12) !important;
    color: #171a19 !important;
}
```

---

### Task 7: Verify all functionality

**Files:** None — run manual verification

- [ ] `streamlit run app.py` — app loads without exceptions
- [ ] Upload page — file selection works, drag/drop works, help text shows
- [ ] Upload area shows correctly in Dark mode (premium deep surface)
- [ ] Switch to Light mode — upload area shows soft neutral surface, no dark blocks
- [ ] Theme toggle — active button clearly seated within group in both modes
- [ ] Cards — content has breathing room, no text touches borders
- [ ] Dashboard renders with video, transcript, charts, scores
- [ ] History lists sessions and opens reports
- [ ] All Plotly charts render with correct template in both modes
- [ ] Sidebar collapse/expand visible in both modes
- [ ] `pytest tests/test_app_shell.py` passes
