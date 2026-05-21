# Read.cv Figma Shell Adaptation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Status note (2026-05-20):** Implementation and automated verification were continued from the approved Read.cv spec. The checked-in Figma-derived design spec was used as the authoritative reference in this session because live Figma MCP/resources were not exposed here, so the explicit side-by-side visual compare remains open until that manual pass is completed.

**Goal:** Rework the Streamlit presentation shell so `Upload`, `Dashboard`, and `History` follow the approved Read.cv-inspired editorial system while preserving all analyzer functionality.

**Architecture:** Keep the existing one-file Streamlit app structure and current widgets, then tighten the UI contract with tests, update semantic hooks in `app.py`, replace the premium/glass CSS with a quiet editorial shell in `assets/styles.css` and `assets/light.css`, and close the loop by marking the Figma traceability checklist in `TODO.md`. The implementation stays additive and presentation-only: no changes to scoring, upload, history, or session-state behavior.

**Tech Stack:** Python, Streamlit, Plotly, CSS, pytest, Streamlit AppTest.

---

## File Structure

- Modify: `tests/test_app_shell.py`
  - Lock the approved shell contract in tests before editing implementation.
- Modify: `app.py`
  - Keep logic stable while adjusting semantic hooks, page copy, and shell wrappers.
- Modify: `assets/styles.css`
  - Replace the premium/glass dark shell with the restrained editorial dark system.
- Modify: `assets/light.css`
  - Align light mode with the same editorial system.
- Modify: `TODO.md`
  - Mark the Figma traceability checklist as implementation lands and verification completes.

### Task 1: Tighten The Editorial Shell Contract

**Files:**
- Modify: `tests/test_app_shell.py`

- [x] **Step 1: Add a failing CSS contract test for the editorial shell**

Insert this test below `test_light_theme_uses_readcv_editorial_tokens`:

```python
def test_css_uses_editorial_shell_contract():
    """The Read.cv shell should avoid premium glass effects and use quiet surfaces."""
    css = (APP_SOURCE.parent / "assets" / "styles.css").read_text(encoding="utf-8")

    assert "--shadow-soft: none;" in css
    assert "backdrop-filter: blur" not in css
    assert "box-shadow:\n    0 22px" not in css
    assert "border-radius: 12px;" not in css
    assert ".top-nav{" in css
    assert ".score-editorial" in css
    assert ".file-evidence" in css
```

- [x] **Step 2: Tighten the markup hook regression test**

Replace `test_app_markup_contains_editorial_readcv_hooks` with:

```python
def test_app_markup_contains_editorial_readcv_hooks():
    """The app should expose stable hooks for the approved Figma mapping."""
    source = APP_SOURCE.read_text(encoding="utf-8")

    assert "top-nav-wrap" in source
    assert "file-evidence" in source
    assert "section-list" in source
    assert "score-editorial" in source
    assert "archive-summary" in source
```

- [x] **Step 3: Run the targeted shell tests and verify failure**

Run:

```bash
pytest tests/test_app_shell.py -v
```

Expected:

- `test_css_uses_editorial_shell_contract` fails because `assets/styles.css` still contains premium shadows, blur, and large-radius shell styling.
- `test_app_initial_render_has_no_streamlit_exceptions` still passes.

- [x] **Step 4: Commit the failing contract tests**

Run:

```bash
git add tests/test_app_shell.py
git commit -m "test: tighten Read.cv shell contract"
```

### Task 2: Re-Author `app.py` Around The Approved Shell Mapping

**Files:**
- Modify: `app.py`
- Modify: `TODO.md`
- Test: `tests/test_app_shell.py`

- [x] **Step 1: Update page headers so each route uses the approved editorial framing**

In `render_upload_page`, replace the current `render_page_header(...)` call with:

```python
render_page_header(
    "New session",
    "Upload interview recording",
    "Run the local analysis pipeline and move directly into a structured editorial review.",
)
```

In `render_dashboard_page`, replace the page header call with:

```python
render_page_header(
    "Interview dossier",
    "Session review",
    "Read the score, coaching interpretation, transcript, and supporting evidence as one structured report.",
)
```

In `render_history_page`, replace the page header call with:

```python
render_page_header(
    "Archive index",
    "Session history",
    "Reopen saved sessions and compare progress without leaving the current workflow.",
)
```

- [x] **Step 2: Make the top navigation read like an editorial shell instead of a premium pill bar**

Keep the existing button logic, but replace the opening navigation markup in `render_top_nav()` with:

```python
st.markdown(
    """
    <div class="top-nav-wrap">
      <div class="top-nav" role="navigation" aria-label="Primary navigation">
        <div class="top-nav-left">
          <div class="top-nav-brand">Interview Intelligence</div>
          <div class="top-nav-sub">Editorial practice review</div>
        </div>
        <div class="top-nav-center" aria-label="Navigation">
    """,
    unsafe_allow_html=True,
)
```

Replace the closing right-side block with:

```python
st.markdown(
    """
        </div>
        <div class="top-nav-right" aria-label="Session context">
          <button class="top-nav-theme" data-active="false" type="button" aria-label="Toggle theme">
            {THEME}
          </button>
          <div class="top-nav-latest" aria-label="Latest session">
            <div class="k">Latest session</div>
            <div class="v">{LATEST}</div>
          </div>
        </div>
      </div>
    </div>
    """.replace("{THEME}", theme_label).replace(
        "{LATEST}", f"{latest_id or '-'} - {latest_score}"
    ),
    unsafe_allow_html=True,
)
```

- [x] **Step 3: Keep the Dashboard score block aligned with the dossier framing**

In the dashboard summary markup, ensure the summary wrapper uses:

```python
<div class="score-editorial tone-{escape(score_summary["tone"])}">
```

and the supporting metrics strip stays:

```python
html = ['<div class="evidence-grid" aria-label="Supporting interview metrics">']
```

If the score wrapper still uses any older class name, replace it in full with:

```python
st.markdown(
    textwrap.dedent(f"""
    <div class="score-editorial tone-{escape(score_summary["tone"])}">
        <div>
            <p class="score-label">Confidence score</p>
            <h2>{confidence.composite:.0f}</h2>
        </div>
        <div>
            <p class="score-classification">{escape(score_summary["headline"])}</p>
            <p>{escape(score_summary["body"])}</p>
        </div>
    </div>
    """),
    unsafe_allow_html=True,
)
```

- [x] **Step 4: Keep the history summary anchor explicit for styling and traceability**

Ensure `render_history_page()` contains this exact anchor before the summary metrics:

```python
st.markdown('<span class="archive-summary"></span>', unsafe_allow_html=True)
summary_cols = st.columns(4)
```

- [x] **Step 5: Mark the hook-oriented traceability rows as completed**

In `TODO.md`, update these rows from `[ ]` to `[x]` after the `app.py` changes land:

```md
- [x] Shell navigation / editorial rail -> persistent chrome, latest-session context, restrained navigation -> top nav + shell wrappers -> `.top-nav*`, branding hooks, nav button selectors
- [x] Page header pattern -> calm title stack with divider transition -> all page headers -> `.page-header`, `.page-eyebrow`, `.page-description`
- [x] Dashboard score anchor -> dossier-style lead score and summary -> executive summary shell -> `.score-editorial`, `.executive-summary`
- [x] Dashboard evidence row -> supporting metrics in divided band -> signal strip -> `.evidence-grid`
- [x] History archive summary -> restrained summary metrics band -> history top stats -> `archive-summary` hook + metric row selectors
```

- [x] **Step 6: Run the shell tests and verify only CSS-specific failures remain**

Run:

```bash
pytest tests/test_app_shell.py -v
```

Expected:

- Markup hook tests pass.
- CSS contract test still fails until the stylesheet rewrite is done.

- [x] **Step 7: Commit the shell hook refactor**

Run:

```bash
git add app.py TODO.md
git commit -m "refactor: align shell hooks with Read.cv mapping"
```

### Task 3: Replace The Dark Shell In `assets/styles.css`

**Files:**
- Modify: `assets/styles.css`
- Modify: `TODO.md`
- Test: `tests/test_app_shell.py`

- [x] **Step 1: Replace the root dark token block with the editorial dark system**

At the top of `.stApp`, replace the current token group with:

```css
.stApp {
  --background: #0d0d0d;
  --foreground: #f3f1ea;
  --card: #111111;
  --border: rgba(243, 241, 234, 0.12);
  --border-strong: rgba(243, 241, 234, 0.20);
  --muted: #171717;
  --muted-foreground: #9a968d;
  --primary: #d8d1c3;
  --primary-foreground: #111111;
  --accent: #b9b1a4;
  --accent-foreground: #111111;
  --bg-subtle: #151515;
  --sidebar-bg: #0d0d0d;
  --surface-raised: #151515;
  --surface-inset: #080808;
  --text-soft: #7f7a70;
  --accent-hover: #f3f1ea;
  --accent-soft: rgba(216, 209, 195, 0.12);
  --success: #a9b7a2;
  --warning: #c4ad83;
  --danger: #c08f83;
  --shadow: none;
  --shadow-soft: none;
  --radius: 6px;
  --bg: var(--background);
  --surface: var(--card);
  --surface-muted: var(--muted);
  --text: var(--foreground);
  --text-muted: var(--muted-foreground);
  --text-card: var(--foreground);
  --text-card-muted: var(--muted-foreground);
  --accent-text: var(--primary-foreground);
  background: var(--background);
  color: var(--foreground);
}
```

- [x] **Step 2: Replace the layout and surface rules with quiet editorial structure**

Replace the current background/surface-heavy rules with:

```css
.main .block-container {
  max-width: 1240px;
  padding-top: 2.4rem;
  padding-bottom: 3.2rem;
}

.stApp {
  background: var(--background);
}

.page-header {
  border-bottom: 1px solid var(--border);
  margin: 0 0 1.5rem;
  padding-bottom: 1.1rem;
}

.page-eyebrow {
  color: var(--text-soft);
  font-size: 0.74rem;
  font-weight: 600;
  letter-spacing: 0;
  margin: 0 0 0.2rem;
  text-transform: uppercase;
}

.page-header h1 {
  color: var(--foreground);
  font-size: 1.95rem;
  font-weight: 640;
  letter-spacing: 0;
  line-height: 1.1;
  margin: 0;
}

.page-description {
  color: var(--muted-foreground);
  font-size: 0.96rem;
  line-height: 1.58;
  margin: 0.6rem 0 0;
  max-width: 720px;
}

.surface,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.surface-anchor) {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: none;
  margin-bottom: 0.9rem;
  padding: 1.35rem;
}

.surface-hero,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.surface-hero) {
  background: var(--surface-raised);
  border-color: var(--border);
  box-shadow: none;
}

.surface-muted,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.surface-muted),
.executive-summary,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.executive-summary) {
  background: var(--muted);
  border-color: var(--border);
  box-shadow: none;
}

.section-header {
  border-bottom: 1px solid var(--border);
  margin-bottom: 0.8rem;
  padding-bottom: 0.7rem;
}
```

- [x] **Step 3: Rewrite the top navigation, evidence rows, and dossier blocks**

Replace the current top-nav and dashboard-heavy styling with:

```css
.top-nav-wrap {
  position: sticky;
  top: 0;
  z-index: 50;
  background: transparent;
  padding: 14px 0 10px;
}

.top-nav {
  max-width: 1240px;
  margin: 0 auto;
  padding: 12px 14px;
  border-bottom: 1px solid var(--border);
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.top-nav-brand {
  color: var(--foreground);
  font-weight: 660;
  font-size: 0.98rem;
  letter-spacing: 0;
}

.top-nav-sub,
.top-nav-latest .k,
.score-label,
.score-classification,
.file-label,
.detail-list span,
.evidence-grid span {
  color: var(--text-soft);
  font-size: 0.74rem;
  font-weight: 600;
  letter-spacing: 0;
  text-transform: uppercase;
}

.top-nav-latest {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
  border-left: 1px solid var(--border);
  padding-left: 0.9rem;
}

.file-evidence,
.evidence-grid,
.process-meta {
  border-bottom: 1px solid var(--border);
  border-top: 1px solid var(--border);
  display: grid;
  gap: 0;
}

.file-evidence {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.process-meta,
.evidence-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.file-evidence > div,
.process-meta span,
.evidence-grid > div {
  min-height: 68px;
  padding: 0.95rem 1rem;
}

.file-evidence > div + div,
.process-meta span + span,
.evidence-grid > div + div {
  border-left: 1px solid var(--border);
}

.score-editorial {
  align-items: stretch;
  border-bottom: 1px solid var(--border);
  border-top: 1px solid var(--border);
  display: grid;
  gap: 0;
  grid-template-columns: minmax(130px, 0.42fr) 1fr;
  margin: 0.4rem 0 1.2rem;
}

.score-editorial > div {
  padding: 1.05rem 1.1rem;
}

.score-editorial > div + div {
  border-left: 1px solid var(--border);
}

.score-editorial h2 {
  color: var(--foreground);
  font-size: 3.8rem;
  font-weight: 650;
  letter-spacing: 0;
  line-height: 0.95;
  margin: 0;
}
```

- [x] **Step 4: Replace interaction chrome with restrained controls**

In `assets/styles.css`, replace premium hover/glass treatments for buttons, tabs, uploader, metrics, and tables with:

```css
div[data-testid="stFileUploader"] {
  background: transparent;
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius);
  padding: 1.2rem;
  transition: background-color 160ms ease, border-color 160ms ease;
}

div[data-testid="stFileUploader"]:hover {
  background: var(--muted);
  border-color: var(--foreground);
}

.stButton button {
  background-color: transparent !important;
  border: 1px solid var(--border-strong) !important;
  border-radius: var(--radius);
  box-shadow: none !important;
  color: var(--foreground) !important;
  min-height: 44px;
  font-size: 0.9rem;
  font-weight: 560;
  transition: background-color 160ms ease, border-color 160ms ease, color 160ms ease;
}

.stButton button[kind="primary"] {
  background-color: var(--primary) !important;
  border-color: var(--primary) !important;
  color: var(--primary-foreground) !important;
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
  font-size: 0.9rem;
  font-weight: 540;
  padding: 0.65rem 0;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
  background: transparent;
  border-bottom-color: var(--foreground);
  color: var(--foreground);
}

div[data-testid="stMetric"],
.detail-list > div {
  background: transparent;
  border: 0;
  border-bottom: 1px solid var(--border);
  border-radius: 0;
  box-shadow: none;
  min-height: 64px;
  padding: 0.85rem 0;
}

.stPlotlyChart,
.stDataFrame,
div[data-testid="stStatusWidget"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  box-shadow: none !important;
  overflow: hidden;
}
```

- [x] **Step 5: Mark the dark-shell traceability rows as completed**

In `TODO.md`, update these rows to `[x]`:

```md
- [x] Upload lead module -> "new session" primary intake surface -> Upload hero block -> `.surface-hero`, uploader selectors
- [x] Upload evidence row -> file metadata as archival evidence -> upload file summary -> `.file-evidence`
- [x] Upload secondary guidance -> structured quiet supporting content -> report coverage list -> `.section-list`
- [x] Dashboard interpretation modules -> restrained report sections instead of dashboard cards -> insight and detail regions -> `.insight-grid`, `.insight-card`, `.detail-list`
- [x] Dashboard detail navigation -> quiet sectional switching -> tabs area -> `.stTabs` selectors
- [x] Dark theme tokens -> restrained charcoal editorial mode -> global dark shell -> `.stApp` tokens in `assets/styles.css`
```

- [x] **Step 6: Run the targeted shell tests and make sure they pass**

Run:

```bash
pytest tests/test_app_shell.py -v
```

Expected:

- all tests in `tests/test_app_shell.py` pass

- [x] **Step 7: Commit the dark shell rewrite**

Run:

```bash
git add assets/styles.css TODO.md tests/test_app_shell.py
git commit -m "style: replace premium shell with editorial dark theme"
```

### Task 4: Align Light Mode In `assets/light.css`

**Files:**
- Modify: `assets/light.css`
- Modify: `app.py`
- Modify: `TODO.md`
- Test: `tests/test_app_shell.py`

- [x] **Step 1: Replace the light-mode token injection in `load_css()`**

Inside `load_css(theme: str)`, replace the current light-mode inline token block with:

```python
if theme == "Light":
    st.markdown(
        """
        <style>
        :root{
          --background: #f7f5ef;
          --foreground: #191817;
          --sidebar-bg: #f7f5ef;
          --card: #fffefa;
          --muted: #ece8df;
          --border: rgba(25, 24, 23, 0.12);
          --border-strong: rgba(25, 24, 23, 0.20);
          --muted-foreground: #6f6a60;
          --primary: #191817;
          --primary-foreground: #fffefa;
          --accent: #716b61;
          --accent-foreground: #fffefa;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
```

- [x] **Step 2: Rewrite the light stylesheet to mirror the editorial dark rules**

At the top of `assets/light.css`, align the base and surfaces with:

```css
.stApp {
  background: #f7f5ef !important;
  color: #191817 !important;
}

.main .block-container {
  max-width: 1240px;
  padding-top: 2.4rem;
  padding-bottom: 3.2rem;
}

.page-header {
  border-bottom: 1px solid rgba(25, 24, 23, 0.12);
  margin: 0 0 1.5rem;
  padding-bottom: 1.1rem;
}

.surface,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.surface-anchor),
.surface-hero,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.surface-hero) {
  background: #fffefa !important;
  border: 1px solid rgba(25, 24, 23, 0.16) !important;
  border-radius: 6px !important;
  box-shadow: none !important;
}

.surface-muted,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.surface-muted),
.executive-summary,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.executive-summary) {
  background: #ece8df !important;
  border-color: rgba(25, 24, 23, 0.16) !important;
  box-shadow: none !important;
}
```

- [x] **Step 3: Replace light-mode control styling so it matches the same shell**

In `assets/light.css`, ensure uploader, buttons, tabs, and evidence rows use:

```css
div[data-testid="stFileUploader"] {
  background: transparent !important;
  border: 1px dashed rgba(25, 24, 23, 0.20) !important;
  border-radius: 6px !important;
  padding: 1.2rem !important;
}

div[data-testid="stFileUploader"]:hover {
  background: rgba(25, 24, 23, 0.05) !important;
  border-color: #191817 !important;
}

.stButton button {
  background-color: transparent !important;
  border: 1px solid rgba(25, 24, 23, 0.20) !important;
  border-radius: 6px !important;
  box-shadow: none !important;
  color: #191817 !important;
  min-height: 44px;
}

.stButton button[kind="primary"] {
  background-color: #191817 !important;
  border-color: #191817 !important;
  color: #fffefa !important;
}

.stTabs [data-baseweb="tab-list"] {
  background: transparent;
  border-bottom: 1px solid rgba(25, 24, 23, 0.12);
  border-radius: 0;
}

.file-evidence,
.evidence-grid,
.process-meta {
  border-bottom: 1px solid rgba(25, 24, 23, 0.12);
  border-top: 1px solid rgba(25, 24, 23, 0.12);
}
```

- [x] **Step 4: Mark the light-theme traceability row as completed**

In `TODO.md`, update:

```md
- [x] Light theme tokens -> warm paper-like editorial mode -> global light shell -> `assets/light.css`, light token injection in `app.py`
```

- [x] **Step 5: Run the focused shell tests**

Run:

```bash
pytest tests/test_app_shell.py -v
```

Expected:

- all shell tests pass in both dark and light contract coverage

- [ ] **Step 6: Commit the light shell alignment**

Run:

```bash
git add app.py assets/light.css TODO.md
git commit -m "style: align light theme with editorial shell"
```

### Task 5: Verification And Checklist Closure

**Files:**
- Modify: `TODO.md`
- Test: `tests/test_app_shell.py`
- Test: `tests/test_visual_analysis.py`
- Test: full suite via `pytest -q`

- [x] **Step 1: Run the app-shell and full regression tests**

Run:

```bash
pytest tests/test_app_shell.py -v
pytest -q
```

Expected:

- shell tests pass
- full suite passes

- [ ] **Step 2: Start Streamlit and verify runtime behavior**

Run:

```bash
streamlit run app.py
```

Expected:

- Streamlit starts without exceptions
- a local URL is printed, usually `http://localhost:8501`

2026-05-20 status:

- Streamlit startup was re-verified successfully from the current working tree.
- The page-by-page manual walkthrough and explicit side-by-side Figma comparison are still pending.

Verify manually:

- `Upload` shows the new-session framing and uploader remains usable
- `Dashboard` empty state still routes to Upload
- completed analyses still render score, transcript, evidence, charts, and tabs
- `History` still lists records and reopens a selected report
- theme toggle still switches dark/light without unreadable text

- [ ] **Step 3: Mark the remaining checklist and QA rows as complete**

In `TODO.md`, update these rows to `[x]` after visual verification:

```md
- [x] History archive body -> scan-friendly records plus reopen panel -> table and resume panel surfaces -> `.surface`, dataframe selectors, selectbox/button selectors

- [x] Final QA
  - [x] Run `pytest -q`
  - [x] Visual compare every page side-by-side with Figma template
```

Also update the headline work item:

```md
- [x] Implement remaining Figma parity items (progressive CSS-only).
```

- [ ] **Step 4: Commit verification and checklist closure**

Run:

```bash
git add TODO.md
git commit -m "docs: complete Figma traceability checklist"
```

---

## Self-Review

**Spec coverage**

- Purpose / agreed approach: Tasks 2-4 keep logic stable and adapt only shell/markup/CSS.
- Page mapping: Task 2 updates route framing; Tasks 3-4 align Upload, Dashboard, and History surfaces.
- Visual system: Tasks 3-4 replace shadows, blur, premium chrome, and tokens with the editorial system.
- Traceability / anti-hallucination: Tasks 2-5 explicitly complete checklist rows in `TODO.md`.
- Verification: Task 5 covers structural and behavioral validation.

**Placeholder scan**

- No `TBD`, `TODO`, or "implement later" text appears in the tasks.
- Every code-changing step includes exact snippets or direct replacement targets.
- Every validation step includes an exact command and expected result.

**Type and name consistency**

- The plan consistently uses existing hook names already present in the codebase: `.top-nav*`, `.file-evidence`, `.section-list`, `.score-editorial`, `.evidence-grid`, and `archive-summary`.
- Token names remain aligned with the existing CSS contract: `--background`, `--card`, `--muted`, `--border`, `--primary`, and related legacy aliases.


