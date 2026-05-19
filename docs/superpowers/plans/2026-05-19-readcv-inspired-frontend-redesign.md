# Read.cv-Inspired Frontend Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the Streamlit presentation layer so the app visually follows the supplied Read.cv/Figma Sites template while preserving all upload, analysis, dashboard, history, chart, and session-state behavior.

**Architecture:** Keep the existing one-file Streamlit app architecture and use semantic HTML hooks plus CSS to transform the UI. Update tests first to encode the new minimalist editorial contract, then adjust markup hooks in `app.py`, replace the visual system in `assets/styles.css`, and verify the app still renders.

**Tech Stack:** Python, Streamlit, Plotly, pytest, Streamlit AppTest, CSS.

---

## File Structure

- Modify `tests/test_app_shell.py`
  - Replace the old premium SaaS visual-token assertions with Read.cv-inspired contract assertions.
  - Keep existing safety tests for complete HTML wrappers, Streamlit exception-free render, and native menu accessibility.

- Modify `app.py`
  - Preserve analysis pipeline, session-state keys, routing, database calls, and Streamlit widgets.
  - Change only HTML class hooks, page copy, sidebar module markup, upload metadata markup, dashboard summary classes, and Plotly chart theme colors.

- Modify `assets/styles.css`
  - Replace the current dark premium SaaS card system with a minimalist editorial system: thin rules, low radius, almost no shadow, muted surfaces, profile-style sidebar, and quiet data modules.
  - Continue styling Streamlit internals for uploader, tabs, metrics, dataframe, status widget, focus, and sidebar controls.

---

### Task 1: Update UI Contract Tests

**Files:**
- Modify: `tests/test_app_shell.py`

- [ ] **Step 1: Replace the light-theme token test**

In `tests/test_app_shell.py`, replace `test_light_theme_sidebar_tokens_are_visibly_separated` with:

```python
def test_light_theme_uses_readcv_editorial_tokens():
    """Light mode should use warm editorial surfaces and subtle dividers."""
    source = APP_SOURCE.read_text(encoding="utf-8")

    assert "--background: #f7f5ef;" in source
    assert "--sidebar-bg: #f7f5ef;" in source
    assert "--card: #fffefa;" in source
    assert "--muted: #ece8df;" in source
    assert "--border: rgba(25, 24, 23, 0.12);" in source
    assert "--muted-foreground: #6f6a60;" in source
```

- [ ] **Step 2: Replace the motion/surface contract test**

In `tests/test_app_shell.py`, replace `test_css_uses_restrained_surface_and_motion_contracts` with:

```python
def test_css_uses_readcv_surface_and_motion_contracts():
    """Core CSS should prefer Read.cv-like rules over glossy dashboard chrome."""
    css = (APP_SOURCE.parent / "assets" / "styles.css").read_text(encoding="utf-8")

    assert "--radius: 6px;" in css
    assert "--shadow: none;" in css
    assert "border-bottom: 1px solid var(--border);" in css
    assert "letter-spacing: 0;" in css
    assert "min-height: 44px;" in css
    assert "transform: scale(1.05)" not in css
    assert "border-radius: 999px" not in css
```

- [ ] **Step 3: Add markup hook regression test**

Add this test below the CSS contract tests:

```python
def test_app_markup_contains_editorial_readcv_hooks():
    """The app should expose semantic hooks for the minimalist editorial redesign."""
    source = APP_SOURCE.read_text(encoding="utf-8")

    assert "brand-profile" in source
    assert "process-meta" in source
    assert "score-editorial" in source
    assert "evidence-grid" in source
    assert "archive-summary" in source
```

- [ ] **Step 4: Run the targeted tests and verify expected failures**

Run:

```bash
pytest tests/test_app_shell.py -v
```

Expected:

- `test_light_theme_uses_readcv_editorial_tokens` fails because the old light tokens are still present.
- `test_css_uses_readcv_surface_and_motion_contracts` fails because the current CSS still uses `--radius: 10px` or `8px`, `box-shadow`, pill radii, and old motion language.
- `test_app_markup_contains_editorial_readcv_hooks` fails because the new hooks are not in `app.py` yet.
- The existing shell safety tests should continue passing.

- [ ] **Step 5: Commit the failing test contract**

Run:

```bash
git add tests/test_app_shell.py
git commit -m "test: define Read.cv frontend contract"
```

---

### Task 2: Add Editorial Markup Hooks In `app.py`

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Update sidebar profile markup**

In `render_sidebar`, replace the current `brand-block` HTML string with:

```python
st.markdown(
    textwrap.dedent("""
    <div class="brand-profile">
        <div class="brand-kicker">Local analysis workspace</div>
        <h2>Interview Intelligence</h2>
        <p class="brand-subtitle">Speech, presence, and confidence review for practice interviews.</p>
        <div class="brand-meta">
            <span>Private by default</span>
            <span>v0.1.0</span>
        </div>
    </div>
    """),
    unsafe_allow_html=True,
)
```

- [ ] **Step 2: Update sidebar support sections**

Replace `sidebar-card` class usage with `sidebar-note` in the latest-session block:

```python
<div class="sidebar-note">
    <p class="sidebar-label">Latest session</p>
    <h4>{escape(str(latest_id))}</h4>
    <p>Most recent confidence score: {escape(score_label)}</p>
</div>
```

Replace the current-flow block with:

```python
<div class="sidebar-note sidebar-note-muted">
    <p class="sidebar-label">Current flow</p>
    <ul>
        <li>Upload a local recording.</li>
        <li>Review the interview dossier.</li>
        <li>Reopen prior sessions from the archive.</li>
    </ul>
</div>
```

Keep `st.caption("v0.1.0 - Local-first analysis")` or update the caption text to ASCII if needed.

- [ ] **Step 3: Update upload process markup**

In `render_upload_page`, replace:

```html
<div class="process-strip">
    <span>Upload</span>
    <span>Transcribe</span>
    <span>Interpret</span>
    <span>Report</span>
</div>
```

with:

```html
<div class="process-meta" aria-label="Analysis stages">
    <span><strong>01</strong> Upload</span>
    <span><strong>02</strong> Transcribe</span>
    <span><strong>03</strong> Interpret</span>
    <span><strong>04</strong> Report</span>
</div>
```

- [ ] **Step 4: Update upload and checklist helper class names**

Change:

```html
<div class="file-summary">
```

to:

```html
<div class="file-evidence">
```

Change:

```html
<div class="checklist">
```

to:

```html
<div class="section-list">
```

Keep all dynamic values and backend validation logic unchanged.

- [ ] **Step 5: Update dashboard score and evidence hooks**

In `render_dashboard_page`, change:

```html
<div class="score-lockup tone-{escape(score_summary["tone"])}">
```

to:

```html
<div class="score-editorial tone-{escape(score_summary["tone"])}">
```

In `render_signal_strip`, change the first line from:

```python
html = ['<div class="signal-strip" aria-label="Supporting interview metrics">']
```

to:

```python
html = ['<div class="evidence-grid" aria-label="Supporting interview metrics">']
```

- [ ] **Step 6: Update history summary wrapper**

In `render_history_page`, wrap the four summary metrics with a CSS anchor so they can be styled as a Read.cv archive row:

```python
st.markdown('<span class="archive-summary"></span>', unsafe_allow_html=True)
summary_cols = st.columns(4)
```

The anchor is complete HTML and does not wrap Streamlit elements, so it preserves the existing partial-wrapper safety contract.

- [ ] **Step 7: Tune Plotly chart colors**

In the emotion chart block, replace the current `color_scale`, `font_c`, and `tick_c` values with:

```python
color_scale = (
    ["#e6e1d8", "#b9b1a4", "#716b61"] if is_light
    else ["#252525", "#5d5a52", "#d8d1c3"]
)
font_c = "#191817" if is_light else "#f3f1ea"
tick_c = "#6f6a60" if is_light else "#9a968d"
```

Keep `paper_bgcolor` and `plot_bgcolor` transparent.

- [ ] **Step 8: Run app-shell tests and verify only CSS contract remains failing**

Run:

```bash
pytest tests/test_app_shell.py -v
```

Expected:

- Markup hook test now passes.
- Complete HTML wrapper test passes.
- Initial render test passes.
- Token and CSS visual contract tests may still fail until Task 3.

- [ ] **Step 9: Commit markup hooks**

Run:

```bash
git add app.py
git commit -m "refactor: add Read.cv editorial UI hooks"
```

---

### Task 3: Replace CSS With Read.cv-Inspired Visual System

**Files:**
- Modify: `assets/styles.css`

- [ ] **Step 1: Replace the dark default token block**

At the top of `.stApp`, use these default tokens:

```css
.stApp {
  --background: #0d0d0d;
  --foreground: #f3f1ea;
  --card: #111111;
  --border: rgba(243, 241, 234, 0.12);
  --muted: #171717;
  --muted-foreground: #9a968d;
  --primary: #d8d1c3;
  --primary-foreground: #111111;
  --accent: #b9b1a4;
  --accent-foreground: #111111;

  --bg: var(--background);
  --bg-subtle: #151515;
  --sidebar-bg: #0d0d0d;
  --surface: var(--card);
  --surface-raised: #151515;
  --surface-muted: var(--muted);
  --surface-inset: #080808;
  --text: var(--foreground);
  --text-muted: var(--muted-foreground);
  --text-soft: #7f7a70;
  --text-card: var(--foreground);
  --text-card-muted: var(--muted-foreground);
  --accent-hover: #f3f1ea;
  --accent-text: var(--primary-foreground);
  --accent-soft: rgba(216, 209, 195, 0.12);
  --success: #a9b7a2;
  --warning: #c4ad83;
  --danger: #c08f83;
  --shadow: none;
  --shadow-soft: none;
  --border-strong: rgba(243, 241, 234, 0.20);
  --radius: 6px;

  background: var(--background);
  color: var(--foreground);
}
```

- [ ] **Step 2: Replace the light-mode token override in `app.py`**

Inside `load_css`, replace the light-mode `<style>` token values with:

```css
.stApp {
    --background: #f7f5ef;
    --foreground: #191817;
    --card: #fffefa;
    --border: rgba(25, 24, 23, 0.12);
    --muted: #ece8df;
    --muted-foreground: #6f6a60;
    --primary: #191817;
    --primary-foreground: #fffefa;
    --accent: #716b61;
    --accent-foreground: #fffefa;

    --bg: var(--background);
    --bg-subtle: #efebe2;
    --sidebar-bg: #f7f5ef;
    --surface: var(--card);
    --surface-raised: #fffefa;
    --surface-muted: var(--muted);
    --surface-inset: #e6e1d8;
    --text: var(--foreground);
    --text-muted: var(--muted-foreground);
    --text-soft: #8b857a;
    --text-card: var(--foreground);
    --text-card-muted: var(--muted-foreground);
    --accent-hover: #3a3733;
    --accent-text: var(--primary-foreground);
    --accent-soft: rgba(25, 24, 23, 0.08);
    --success: #66755f;
    --warning: #8a6f3e;
    --danger: #8a5149;
    --shadow: none;
    --shadow-soft: none;
    --border-strong: rgba(25, 24, 23, 0.20);
    --radius: 6px;
}
```

- [ ] **Step 3: Update base layout**

In `assets/styles.css`, set:

```css
.main .block-container {
  max-width: 1240px;
  padding-top: 3rem;
  padding-bottom: 4rem;
}

.stApp,
.stApp p,
.stApp li,
.stApp label,
.stApp span:not(.nav-icon) {
  color: var(--foreground);
  letter-spacing: 0;
}
```

- [ ] **Step 4: Replace sidebar class styles**

Replace the old `.brand-block`, `.sidebar-card`, and related rules with:

```css
.brand-profile,
.sidebar-note {
  border-bottom: 1px solid var(--border);
  padding: 0 0 1.25rem;
  margin: 0 0 1.15rem;
}

.brand-kicker,
.sidebar-label {
  color: var(--text-soft);
  font-size: 0.76rem;
  font-weight: 520;
  letter-spacing: 0;
  margin: 0 0 0.45rem;
}

.brand-profile h2 {
  color: var(--foreground);
  font-size: 1.18rem;
  font-weight: 620;
  letter-spacing: 0;
  line-height: 1.18;
  margin: 0 0 0.65rem;
}

.brand-subtitle,
.sidebar-note p,
.sidebar-note li {
  color: var(--muted-foreground);
  font-size: 0.9rem;
  line-height: 1.55;
  margin: 0;
}

.brand-meta {
  border-top: 1px solid var(--border);
  display: flex;
  gap: 0.75rem;
  justify-content: space-between;
  margin-top: 1rem;
  padding-top: 0.75rem;
}

.brand-meta span {
  color: var(--text-soft);
  font-size: 0.78rem;
}

.sidebar-note h4 {
  color: var(--foreground);
  font-size: 0.96rem;
  font-weight: 580;
  margin: 0 0 0.35rem;
}

.sidebar-note ul {
  list-style: none;
  margin: 0.65rem 0 0;
  padding: 0;
}

.sidebar-note li + li {
  margin-top: 0.45rem;
}
```

- [ ] **Step 5: Restyle navigation**

Replace the current sidebar radio label block with:

```css
section[data-testid="stSidebar"] .stRadio > div {
  display: flex;
  flex-direction: column;
  gap: 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.15rem;
  padding-bottom: 1.15rem;
}

section[data-testid="stSidebar"] .stRadio label {
  border: 0;
  border-left: 1px solid transparent;
  border-radius: 0;
  cursor: pointer;
  display: flex;
  min-height: 44px;
  padding: 0.56rem 0 0.56rem 0.8rem;
  transition: background 160ms ease, border-color 160ms ease, color 160ms ease;
}

section[data-testid="stSidebar"] .stRadio label:hover {
  background: color-mix(in srgb, var(--muted) 62%, transparent);
}

section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
  background: transparent;
  border-left-color: var(--foreground);
}

section[data-testid="stSidebar"] .stRadio label p {
  color: var(--muted-foreground);
  font-size: 0.93rem;
  font-weight: 480;
}

section[data-testid="stSidebar"] .stRadio label:has(input:checked) p {
  color: var(--foreground);
  font-weight: 580;
}
```

- [ ] **Step 6: Restyle surfaces, page headers, and section headers**

Use these rules for the core editorial layout:

```css
.page-header {
  border-bottom: 1px solid var(--border);
  margin: 0 0 2rem;
  padding-bottom: 1.65rem;
}

.page-eyebrow {
  color: var(--text-soft);
  font-size: 0.82rem;
  font-weight: 480;
  letter-spacing: 0;
  margin: 0 0 0.45rem;
}

.page-header h1 {
  color: var(--foreground);
  font-size: 2.25rem;
  font-weight: 620;
  letter-spacing: 0;
  line-height: 1.1;
  margin: 0;
}

.page-description {
  color: var(--muted-foreground);
  font-size: 1rem;
  line-height: 1.62;
  max-width: 720px;
  margin-top: 0.75rem;
}

.surface,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.surface-anchor) {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: none;
  margin-bottom: 1rem;
  padding: 1.5rem;
}

.surface-hero,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.surface-hero) {
  background: var(--surface-raised);
  border-color: var(--border);
  box-shadow: none;
}

.surface-muted,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.surface-muted) {
  background: var(--muted);
}

.section-header {
  border-bottom: 1px solid var(--border);
  margin-bottom: 1rem;
  padding-bottom: 0.9rem;
}

.section-header h3 {
  color: var(--foreground);
  font-size: 1rem;
  font-weight: 590;
  letter-spacing: 0;
  margin: 0 0 0.35rem;
}

.section-header p {
  color: var(--muted-foreground);
  font-size: 0.92rem;
  line-height: 1.55;
  margin: 0;
}
```

- [ ] **Step 7: Replace upload and list styles**

Rename and restyle the upload-related selectors:

```css
.process-meta,
.file-evidence {
  border-bottom: 1px solid var(--border);
  border-top: 1px solid var(--border);
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-bottom: 1.5rem;
}

.process-meta span,
.file-evidence > div {
  color: var(--muted-foreground);
  font-size: 0.86rem;
  min-height: 48px;
  padding: 0.85rem 1rem;
}

.process-meta span + span,
.file-evidence > div + div {
  border-left: 1px solid var(--border);
}

.process-meta strong,
.file-label {
  color: var(--text-soft);
  font-size: 0.76rem;
  font-weight: 480;
  letter-spacing: 0;
  margin-right: 0.35rem;
}

.file-evidence {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin: 1.25rem 0 0.9rem;
}

.file-evidence h4 {
  color: var(--foreground);
  font-size: 0.95rem;
  font-weight: 560;
  margin: 0.2rem 0 0;
}

.section-list {
  display: grid;
}

.section-list > div {
  border-bottom: 1px solid var(--border);
  padding: 1rem 0;
}

.section-list > div:first-child {
  padding-top: 0;
}

.section-list strong {
  color: var(--foreground);
  font-size: 0.94rem;
  font-weight: 580;
}

.section-list span {
  color: var(--muted-foreground);
  display: block;
  font-size: 0.9rem;
  line-height: 1.55;
  margin-top: 0.22rem;
}
```

Keep the uploader itself native but minimal:

```css
div[data-testid="stFileUploader"] {
  background: transparent;
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius);
  padding: 1.2rem;
  transition: background 160ms ease, border-color 160ms ease;
}

div[data-testid="stFileUploader"]:hover {
  background: color-mix(in srgb, var(--muted) 45%, transparent);
  border-color: var(--foreground);
}
```

- [ ] **Step 8: Replace dashboard module styles**

Rename and restyle the dashboard selectors:

```css
.score-editorial {
  align-items: end;
  border-bottom: 1px solid var(--border);
  display: grid;
  gap: 1.5rem;
  grid-template-columns: minmax(140px, 0.38fr) 1fr;
  margin-bottom: 1.25rem;
  padding-bottom: 1.25rem;
}

.score-editorial h2 {
  color: var(--foreground);
  font-size: 4rem;
  font-weight: 620;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
}

.score-label,
.score-classification,
.insight-label,
.detail-list span,
.component-row-header span,
.evidence-grid span {
  color: var(--text-soft);
  font-size: 0.78rem;
  font-weight: 480;
  letter-spacing: 0;
}

.score-editorial p:last-child {
  color: var(--muted-foreground);
  font-size: 0.98rem;
  line-height: 1.6;
  margin: 0;
}

.insight-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0;
  margin-top: 1rem;
  border-top: 1px solid var(--border);
}

.insight-card {
  background: transparent;
  border: 0;
  border-bottom: 1px solid var(--border);
  border-radius: 0;
  box-shadow: none;
  padding: 1rem 0;
  transition: background 160ms ease;
}

.insight-card:nth-child(odd) {
  padding-right: 1rem;
}

.insight-card:nth-child(even) {
  border-left: 1px solid var(--border);
  padding-left: 1rem;
}

.insight-card:hover {
  background: transparent;
  transform: none;
}

.insight-card h4 {
  color: var(--foreground);
  font-size: 0.98rem;
  font-weight: 580;
  margin: 0 0 0.35rem;
}

.insight-card p {
  color: var(--muted-foreground);
  font-size: 0.9rem;
  line-height: 1.55;
  margin: 0;
}

.evidence-grid {
  border-bottom: 1px solid var(--border);
  border-top: 1px solid var(--border);
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin: 0.6rem 0 1.25rem;
}

.evidence-grid > div {
  padding: 0.95rem 1rem;
}

.evidence-grid > div + div {
  border-left: 1px solid var(--border);
}

.evidence-grid strong {
  color: var(--foreground);
  display: block;
  font-size: 1.1rem;
  font-weight: 580;
  margin-top: 0.25rem;
}
```

- [ ] **Step 9: Restyle metrics, detail rows, buttons, tabs, charts, and status**

Keep minimum interaction sizes and remove glossy chrome:

```css
.detail-list > div,
div[data-testid="stMetric"] {
  background: transparent;
  border: 0;
  border-bottom: 1px solid var(--border);
  border-radius: 0;
  box-shadow: none;
  min-height: 64px;
  padding: 0.9rem 0;
}

div[data-testid="stMetric"] label {
  color: var(--text-soft);
  font-size: 0.78rem;
  letter-spacing: 0;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
  color: var(--foreground);
  font-size: 1.45rem;
  font-weight: 580;
}

.stButton button {
  background-color: transparent !important;
  color: var(--foreground) !important;
  border: 1px solid var(--border-strong) !important;
  border-radius: var(--radius);
  min-height: 44px;
  font-size: 0.92rem;
  font-weight: 520;
  transition: background 160ms ease, border-color 160ms ease, color 160ms ease;
  cursor: pointer;
}

.stButton button[kind="primary"] {
  background-color: var(--primary) !important;
  color: var(--primary-foreground) !important;
  border-color: var(--primary) !important;
}

.stButton button:hover {
  background-color: var(--muted) !important;
  border-color: var(--foreground) !important;
}

.stButton button[kind="primary"]:hover {
  background-color: var(--accent-hover) !important;
}

.stTabs [data-baseweb="tab-list"] {
  background: transparent;
  border-bottom: 1px solid var(--border);
  border-radius: 0;
  gap: 1.25rem;
  padding: 0;
}

.stTabs [data-baseweb="tab"] {
  border-bottom: 1px solid transparent;
  border-radius: 0;
  color: var(--muted-foreground);
  font-size: 0.92rem;
  font-weight: 500;
  padding: 0.65rem 0;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
  background: transparent;
  border-bottom-color: var(--foreground);
  color: var(--foreground);
}

.stPlotlyChart,
.stDataFrame,
div[data-testid="stStatusWidget"] {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: none;
  overflow: hidden;
}
```

- [ ] **Step 10: Add archive summary styling**

Add:

```css
div[data-testid="stVerticalBlock"]:has(.archive-summary) + div[data-testid="stHorizontalBlock"],
div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMetric"]) {
  border-bottom: 1px solid var(--border);
  border-top: 1px solid var(--border);
  margin-bottom: 1.25rem;
}
```

If this selector is too broad during visual testing, replace it with a more specific nearby anchor strategy in `app.py`, but keep the `archive-summary` marker in source for the test.

- [ ] **Step 11: Update responsive rules**

Replace the old `@media (max-width: 980px)` block with:

```css
@media (max-width: 980px) {
  .file-evidence,
  .insight-grid,
  .process-meta,
  .score-editorial,
  .evidence-grid {
    grid-template-columns: 1fr;
  }

  .process-meta span + span,
  .file-evidence > div + div,
  .evidence-grid > div + div,
  .insight-card:nth-child(even) {
    border-left: 0;
    border-top: 1px solid var(--border);
  }

  .insight-card:nth-child(odd),
  .insight-card:nth-child(even) {
    padding-left: 0;
    padding-right: 0;
  }

  .page-header h1 {
    font-size: 1.85rem;
  }

  .score-editorial h2 {
    font-size: 3rem;
  }
}
```

- [ ] **Step 12: Run targeted tests**

Run:

```bash
pytest tests/test_app_shell.py -v
```

Expected: all tests in `tests/test_app_shell.py` pass.

- [ ] **Step 13: Commit CSS redesign**

Run:

```bash
git add app.py assets/styles.css tests/test_app_shell.py
git commit -m "style: apply Read.cv inspired Streamlit shell"
```

---

### Task 4: Full Regression And Runtime Verification

**Files:**
- No planned edits unless verification finds a presentation regression.

- [ ] **Step 1: Run full test suite**

Run:

```bash
pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Start Streamlit**

Run:

```bash
streamlit run app.py
```

Expected: Streamlit serves the app locally and the Upload page renders without exceptions.

- [ ] **Step 3: Verify Upload page visually**

Manual checks:

- Sidebar looks like a quiet profile/index rail.
- Upload page uses warm/charcoal editorial modules, thin dividers, low radius, and no glossy cards.
- Native file uploader is visible and supports click/drag-drop.
- `Analyze interview` button remains visible after choosing an allowed file.

- [ ] **Step 4: Verify Dashboard empty state**

Manual checks:

- With no analysis in session, Dashboard shows the empty state.
- `Go to upload` navigates back to Upload.
- No partial HTML is visible.

- [ ] **Step 5: Verify History page**

Manual checks:

- Empty archive or existing archive renders without exceptions.
- Summary stats, table, selector, and `Open selected report` retain original behavior when records exist.

- [ ] **Step 6: Verify theme toggle**

Manual checks:

- Dark mode uses charcoal surfaces and soft off-white text.
- Light mode uses warm off-white surfaces and near-black text.
- Sidebar, uploader, tabs, metrics, table, status widget, and collapse controls remain readable in both modes.

- [ ] **Step 7: Commit any verification fix**

If no fixes are needed, do not create a commit.

If a presentation fix is needed, run:

```bash
git add app.py assets/styles.css tests/test_app_shell.py
git commit -m "fix: polish Read.cv redesign verification issues"
```

---

## Self-Review

Spec coverage:

- Sidebar: Task 2 steps 1-2 and Task 3 steps 4-5.
- Upload page: Task 2 steps 3-4 and Task 3 step 7.
- Dashboard composition: Task 2 step 5 and Task 3 step 8.
- Chart containers and Plotly colors: Task 2 step 7 and Task 3 step 9.
- History page: Task 2 step 6 and Task 3 step 10.
- Light/dark mode: Task 3 steps 1-2 and Task 4 step 6.
- Functionality preservation: Task 2 avoids backend/state changes, Task 4 verifies runtime behavior.

Placeholder scan:

- The plan contains no unresolved placeholders and no unspecified implementation steps.

Type and name consistency:

- New class hooks are consistent across tests, markup, and CSS: `brand-profile`, `process-meta`, `score-editorial`, `evidence-grid`, and `archive-summary`.
