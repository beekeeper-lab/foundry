"""Tests for foundry_app.ui.icons — icon loader and tinting."""

import pytest

from foundry_app.ui.icons import (
    ICON_NAMES,
    _tint_svg,
    available_icons,
    icon_path,
)


class TestIconPath:
    """Tests for icon_path() — filesystem resolution."""

    def test_returns_path_for_valid_icon(self):
        path = icon_path("builder")
        assert path.exists()
        assert path.suffix == ".svg"

    def test_raises_for_unknown_icon(self):
        with pytest.raises(FileNotFoundError, match="Icon not found: nonexistent"):
            icon_path("nonexistent")

    @pytest.mark.parametrize("name", ICON_NAMES)
    def test_all_declared_icons_exist(self, name: str):
        """Every name in ICON_NAMES must resolve to an existing SVG file."""
        path = icon_path(name)
        assert path.is_file(), f"Missing SVG for icon: {name}"


class TestAvailableIcons:
    """Tests for available_icons() — disk scan."""

    def test_returns_sorted_list(self):
        icons = available_icons()
        assert icons == sorted(icons)

    def test_contains_expected_icons(self):
        icons = available_icons()
        for name in ["builder", "settings", "search", "success", "error"]:
            assert name in icons

    def test_count_at_least_15(self):
        """Acceptance criterion: at least 15 icons."""
        assert len(available_icons()) >= 15


class TestTintSvg:
    """Tests for _tint_svg() — color replacement."""

    def test_replaces_stroke_color(self):
        svg = b'<svg stroke="#ffffff" fill="none">'
        result = _tint_svg(svg, "#c9a84c")
        assert b'stroke="#c9a84c"' in result
        assert b'fill="none"' in result  # fill="none" unchanged (not a hex color)

    def test_replaces_fill_color(self):
        svg = b'<svg stroke="#ffffff" fill="#000000">'
        result = _tint_svg(svg, "#ff0000")
        assert b'stroke="#ff0000"' in result
        assert b'fill="#ff0000"' in result

    def test_no_change_when_no_colors(self):
        svg = b'<svg fill="none" stroke="none">'
        result = _tint_svg(svg, "#aabbcc")
        assert result == svg


class TestSvgFileQuality:
    """Verify SVG files are well-formed and consistent."""

    @pytest.mark.parametrize("name", ICON_NAMES)
    def test_svg_has_viewbox(self, name: str):
        content = icon_path(name).read_text()
        assert 'viewBox="0 0 24 24"' in content

    @pytest.mark.parametrize("name", ICON_NAMES)
    def test_svg_is_monochrome_white(self, name: str):
        content = icon_path(name).read_text()
        assert 'stroke="#ffffff"' in content

    @pytest.mark.parametrize("name", ICON_NAMES)
    def test_svg_has_consistent_stroke_width(self, name: str):
        content = icon_path(name).read_text()
        assert 'stroke-width="2"' in content
