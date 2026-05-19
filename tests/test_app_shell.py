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


def test_light_theme_sidebar_tokens_are_visibly_separated():
    """Light theme sidebar surfaces need clear separation from the page."""
    source = APP_SOURCE.read_text(encoding="utf-8")

    assert "--background: #faf9f7;" in source
    assert "--sidebar-bg: #f2f0e8;" in source
    assert "--muted: #f2f0e8;" in source
    assert "--border: rgba(0, 0, 0, 0.08);" in source
    assert "--muted-foreground: #555e59;" in source


def test_css_uses_restrained_surface_and_motion_contracts():
    """Core visual tokens should match the premium UI contract."""
    css = (APP_SOURCE.parent / "assets" / "styles.css").read_text(encoding="utf-8")

    assert "--radius: 8px;" in css
    assert "transition: background 180ms ease, border-color 180ms ease, transform 120ms ease" in css
    assert "min-height: 44px;" in css
    assert "transform: translateY(-1px);" in css
    assert "transform: scale(1.05)" not in css


def test_css_keeps_streamlit_sidebar_and_theme_controls_accessible():
    """Custom shell CSS should hide only native theme choices and keep sidebar controls visible."""
    css = (APP_SOURCE.parent / "assets" / "styles.css").read_text(encoding="utf-8")

    assert '[data-testid="stThemeSelector"]' in css
    assert '[data-testid="stAppOptions"]' not in css
    assert '[data-testid="collapsedControl"]' in css
    assert '[data-testid="stSidebarCollapseButton"]' in css
    assert "visibility: visible !important;" in css
