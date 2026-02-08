"""Foundry theme — industrial dark palette with brass/gold accents.

Centralised visual identity: color palette, typography scale, spacing
constants, and reusable QSS template strings.  Import constants directly
or call ``apply_theme(app)`` to set the application-wide stylesheet.

Palette philosophy: precision workshop / modern forge — confident,
stable, not playful.  Gold/brass accents are reserved for focus and
active states, not decoration.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------

# Backgrounds — deep charcoal with blue undertone
BG_BASE = "#1a1a2e"  # primary window background
BG_SURFACE = "#252540"  # cards, panels, elevated surfaces
BG_OVERLAY = "#2e2e4a"  # tooltips, dropdowns, popovers
BG_INSET = "#141424"  # recessed areas, input fields

# Borders
BORDER_DEFAULT = "#3a3a55"  # standard separator / border
BORDER_SUBTLE = "#2e2e48"  # low-emphasis dividers

# Accent — muted brass / warm gold (use sparingly: focus, active states)
ACCENT_PRIMARY = "#c9a84c"  # primary interactive accent
ACCENT_PRIMARY_HOVER = "#d4b65a"  # hover state for primary accent
ACCENT_PRIMARY_MUTED = "#a08839"  # disabled / low-emphasis variant

# Secondary — steel blue / blueprint blue
ACCENT_SECONDARY = "#5b8fb9"  # secondary interactive accent
ACCENT_SECONDARY_HOVER = "#6ba0ca"  # hover state for secondary accent
ACCENT_SECONDARY_MUTED = "#4a7495"  # disabled / low-emphasis variant

# Text
TEXT_PRIMARY = "#e0e0e8"  # high-contrast body text
TEXT_SECONDARY = "#9999b0"  # labels, captions, muted copy
TEXT_DISABLED = "#5c5c72"  # disabled / placeholder text
TEXT_ON_ACCENT = "#1a1a2e"  # text rendered on accent-colored backgrounds

# Status
STATUS_SUCCESS = "#5e9a6f"  # restrained green — success indicators
STATUS_ERROR = "#b85c5c"  # muted red — error indicators
STATUS_WARNING = "#c9a84c"  # amber — warning indicators (shares brass tone)
STATUS_INFO = "#5b8fb9"  # blue — informational indicators (shares steel)

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------

FONT_FAMILY = "Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"

# Size scale (px)
FONT_SIZE_XS = 11  # fine print, badges
FONT_SIZE_SM = 12  # captions, helper text
FONT_SIZE_MD = 14  # body text, list items
FONT_SIZE_LG = 16  # section headings, emphasis
FONT_SIZE_XL = 20  # page titles, brand
FONT_SIZE_XXL = 26  # hero / splash headings

# Weights (Qt-compatible integer values)
FONT_WEIGHT_NORMAL = 400
FONT_WEIGHT_MEDIUM = 500
FONT_WEIGHT_BOLD = 700

# ---------------------------------------------------------------------------
# Spacing
# ---------------------------------------------------------------------------

SPACE_XS = 4  # tight inner padding
SPACE_SM = 8  # compact gaps
SPACE_MD = 12  # standard padding
SPACE_LG = 16  # section gaps
SPACE_XL = 24  # major section separation
SPACE_XXL = 32  # page-level margins

RADIUS_SM = 4  # subtle rounding (inputs, small cards)
RADIUS_MD = 6  # standard rounding (cards, panels)
RADIUS_LG = 10  # prominent rounding (dialogs, modals)

# ---------------------------------------------------------------------------
# QSS template strings
# ---------------------------------------------------------------------------

QSS_CARD = f"""
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD}px;
    padding: {SPACE_LG}px;
"""

QSS_INPUT = f"""
    background-color: {BG_INSET};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_SM}px;
    padding: {SPACE_SM}px {SPACE_MD}px;
    color: {TEXT_PRIMARY};
    font-size: {FONT_SIZE_MD}px;
    selection-background-color: {ACCENT_SECONDARY_MUTED};
"""

QSS_BUTTON_PRIMARY = f"""
    background-color: {ACCENT_PRIMARY};
    color: {TEXT_ON_ACCENT};
    border: none;
    border-radius: {RADIUS_SM}px;
    padding: {SPACE_SM}px {SPACE_LG}px;
    font-size: {FONT_SIZE_MD}px;
    font-weight: {FONT_WEIGHT_BOLD};
"""

QSS_BUTTON_SECONDARY = f"""
    background-color: transparent;
    color: {ACCENT_SECONDARY};
    border: 1px solid {ACCENT_SECONDARY};
    border-radius: {RADIUS_SM}px;
    padding: {SPACE_SM}px {SPACE_LG}px;
    font-size: {FONT_SIZE_MD}px;
    font-weight: {FONT_WEIGHT_MEDIUM};
"""

QSS_SCROLLBAR = f"""
    QScrollBar:vertical {{
        background: {BG_BASE};
        width: 10px;
        margin: 0;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background: {BORDER_DEFAULT};
        min-height: 30px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {TEXT_SECONDARY};
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: {BG_BASE};
        height: 10px;
        margin: 0;
        border: none;
    }}
    QScrollBar::handle:horizontal {{
        background: {BORDER_DEFAULT};
        min-width: 30px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {TEXT_SECONDARY};
    }}
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
"""

QSS_LIST_ITEM = f"""
    padding: {SPACE_MD}px {SPACE_LG}px;
    border-bottom: 1px solid {BORDER_SUBTLE};
    color: {TEXT_PRIMARY};
    font-size: {FONT_SIZE_MD}px;
"""

QSS_SECTION_HEADER = f"""
    color: {TEXT_SECONDARY};
    font-size: {FONT_SIZE_SM}px;
    font-weight: {FONT_WEIGHT_BOLD};
    text-transform: uppercase;
    padding: {SPACE_SM}px 0;
    border-bottom: 1px solid {BORDER_DEFAULT};
    margin-bottom: {SPACE_MD}px;
"""

# ---------------------------------------------------------------------------
# Base application stylesheet
# ---------------------------------------------------------------------------

_BASE_STYLESHEET = f"""
/* Global defaults */
* {{
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE_MD}px;
}}

QMainWindow {{
    background-color: {BG_BASE};
}}

QWidget {{
    color: {TEXT_PRIMARY};
}}

QToolTip {{
    background-color: {BG_OVERLAY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_DEFAULT};
    padding: {SPACE_XS}px {SPACE_SM}px;
    border-radius: {RADIUS_SM}px;
    font-size: {FONT_SIZE_SM}px;
}}

/* Menu bar */
QMenuBar {{
    background-color: {BG_INSET};
    color: {TEXT_PRIMARY};
    border-bottom: 1px solid {BORDER_DEFAULT};
    padding: 2px;
}}
QMenuBar::item:selected {{
    background-color: {BG_SURFACE};
}}
QMenu {{
    background-color: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_DEFAULT};
}}
QMenu::item:selected {{
    background-color: {BG_OVERLAY};
}}

/* Scroll bars */
{QSS_SCROLLBAR}

/* Focus indicators — brass/gold border for keyboard navigation */
QPushButton:focus {{
    outline: none;
    border: 2px solid {ACCENT_PRIMARY};
    border-radius: {RADIUS_SM}px;
}}
QComboBox:focus {{
    border: 2px solid {ACCENT_PRIMARY};
}}
QListWidget:focus {{
    border: 2px solid {ACCENT_PRIMARY};
    border-radius: {RADIUS_SM}px;
}}
QTreeWidget:focus {{
    border: 2px solid {ACCENT_PRIMARY};
    border-radius: {RADIUS_SM}px;
}}
QLineEdit:focus {{
    border: 2px solid {ACCENT_PRIMARY};
}}
QTextEdit:focus {{
    border: 2px solid {ACCENT_PRIMARY};
    border-radius: {RADIUS_SM}px;
}}
QPlainTextEdit:focus {{
    border: 2px solid {ACCENT_PRIMARY};
    border-radius: {RADIUS_SM}px;
}}
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_theme(app: object) -> None:
    """Apply the Foundry base stylesheet to a QApplication instance.

    Parameters
    ----------
    app:
        A ``QApplication`` (or compatible) instance exposing
        ``setStyleSheet(str)``.
    """
    app.setStyleSheet(_BASE_STYLESHEET)
