"""Regression tests for the Streamlit application shell."""

from __future__ import annotations

import ast
from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_SOURCE = Path(__file__).resolve().parents[1] / "app.py"


def test_app_does_not_render_partial_html_wrappers():
    """Custom HTML sent to Streamlit must be complete in one markdown call.

    Streamlit renders each element as its own block. Opening a raw HTML wrapper
    in one block and closing it in another can leak visible markup into the UI.
    """
    source = APP_SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source)

    partial_markdown_calls: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function_name = getattr(node.func, "attr", None)
        if function_name != "markdown" or not node.args:
            continue

        arg = node.args[0]
        value = arg.value if isinstance(arg, ast.Constant) and isinstance(arg.value, str) else None
        if value is None:
            continue

        stripped = value.strip()
        if stripped == "</div>" or (
            stripped.startswith("<div") and "</div>" not in stripped
        ):
            partial_markdown_calls.append(stripped)

    assert partial_markdown_calls == []


def test_app_initial_render_has_no_streamlit_exceptions():
    """The default Upload workspace should render without crashing."""
    app = AppTest.from_file(str(APP_SOURCE))

    app.run(timeout=10)

    assert app.exception == []


def test_menu_css_only_hides_streamlit_theme_selector():
    """The app menu must remain available while native theme choices are hidden."""
    css = (APP_SOURCE.parent / "assets" / "styles.css").read_text(encoding="utf-8")

    assert '[data-testid="stThemeSelector"]' in css
    assert '[data-testid="stAppOptions"]' not in css


def test_light_theme_uses_readcv_editorial_tokens():
    """Light mode should use warm editorial surfaces and subtle dividers."""
    source = APP_SOURCE.read_text(encoding="utf-8")

    assert "--background: #f7f5ef;" in source
    assert "--sidebar-bg: #f7f5ef;" in source
    assert "--card: #fffefa;" in source
    assert "--muted: #ece8df;" in source
    assert "--border: rgba(25, 24, 23, 0.12);" in source
    assert "--muted-foreground: #6f6a60;" in source


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


def test_app_markup_contains_editorial_readcv_hooks():
    """The app should expose semantic hooks for the minimalist editorial redesign."""
    source = APP_SOURCE.read_text(encoding="utf-8")

    assert "brand-profile" in source
    assert "process-meta" in source
    assert "score-editorial" in source
    assert "evidence-grid" in source
    assert "archive-summary" in source


def test_css_keeps_streamlit_sidebar_and_theme_controls_accessible():
    """Custom shell CSS should hide only native theme choices and keep sidebar controls visible."""
    css = (APP_SOURCE.parent / "assets" / "styles.css").read_text(encoding="utf-8")

    assert '[data-testid="stThemeSelector"]' in css
    assert '[data-testid="stAppOptions"]' not in css
    assert '[data-testid="collapsedControl"]' in css
    assert '[data-testid="stSidebarCollapseButton"]' in css
    assert "visibility: visible !important;" in css
