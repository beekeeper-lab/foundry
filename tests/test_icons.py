"""Tests for foundry_app.ui.icons — icon loader and tinting."""

import pytest

from foundry_app.ui.icons import (
    ICON_NAMES,
    _tint_svg,
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


