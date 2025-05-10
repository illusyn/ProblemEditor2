# Centralized style configuration for the Math Editor UI

import sys

# DPI scaling support
_scale = 1.0

def set_scale_from_dpi(dpi, base_dpi=96, min_scale=0.8, max_scale=1.5):
    """Set the global scaling factor based on screen DPI."""
    global _scale
    scale = dpi / base_dpi
    _scale = max(min_scale, min(scale, max_scale))

def get_scale():
    return _scale

# Font settings
FONT_FAMILY = "Courier"  # Base font family
FONT_WEIGHT = "Bold"     # Base font weight
LABEL_FONT_SIZE = int(14 * _scale)
SECTION_LABEL_FONT_SIZE = int(17 * _scale)
BUTTON_FONT_SIZE = int(16 * _scale)
ENTRY_FONT_SIZE = int(16 * _scale)
NOTES_FONT_SIZE = int(16 * _scale)
SAT_TYPE_FONT_SIZE = int(16 * _scale)
DOMAIN_BTN_FONT_SIZE = int(16 * _scale)
ENTRY_LABEL_FONT_SIZE = int(17 * _scale)

# Base colors
BASE_FONT_COLOR = "#664103"  # Darker text for better contrast
LABEL_FONT_COLOR = BASE_FONT_COLOR
SECTION_LABEL_FONT_COLOR = BASE_FONT_COLOR
BUTTON_FONT_COLOR = BASE_FONT_COLOR
ENTRY_FONT_COLOR = BASE_FONT_COLOR
NOTES_FONT_COLOR = BASE_FONT_COLOR
SAT_TYPE_FONT_COLOR = BASE_FONT_COLOR

# Neumorphic theme variables
NEUMORPH_BG_COLOR = "#f0f0f3"  # Main panel and widget background
NEUMORPH_SHADOW_DARK = "#c4c2b8"  # Warmer shadow color for depth
NEUMORPH_SHADOW_LIGHT = "#ffffff"  # Highlight color for raised effect
NEUMORPH_TEXT_COLOR = BASE_FONT_COLOR
NEUMORPH_GRADIENT_START = "#f7f7fa"
NEUMORPH_GRADIENT_END = NEUMORPH_BG_COLOR
NEUMORPH_RADIUS = int(18 * _scale)

# Component-specific colors
BUTTON_BG_COLOR = NEUMORPH_BG_COLOR
BUTTON_HOVER_COLOR = "#f2f2f2"
BUTTON_BORDER_RADIUS = NEUMORPH_RADIUS
BUTTON_HIGHLIGHT_COLOR = "#cce5ff"

ENTRY_BG_COLOR = "#e8e8e8"  # Slightly darker for contrast
ENTRY_BORDER_RADIUS = int(14 * _scale)
ENTRY_SHADOW_COLOR = "#c8c8c8"

NOTES_BG_COLOR = NEUMORPH_BG_COLOR
NOTES_BORDER_RADIUS = NEUMORPH_RADIUS
NOTES_PADDING = int(16 * _scale)

# Layout and sizing
CONTROL_BTN_WIDTH = int(240 * _scale)
CONTROL_BTN_HEIGHT = int(56 * _scale)
ENTRY_HEIGHT = int(44 * _scale)
NOTES_MIN_HEIGHT = int(100 * _scale)
PADDING = int(40 * _scale)
SPACING = int(28 * _scale)
SECTION_SPACING = int(18 * _scale)

# Entry field specific widths
PROB_ID_ENTRY_WIDTH = int(120 * _scale)
SEARCH_TEXT_ENTRY_WIDTH = int(280 * _scale)
ANSWER_ENTRY_WIDTH = int(320 * _scale)

# Entry field label padding
SEARCH_TEXT_LABEL_PADDING = f"padding-left: {int(16*_scale)}px; padding-bottom: {int(4*_scale)}px;"
ANSWER_LABEL_PADDING = f"padding-left: {int(50*_scale)}px; padding-bottom: {int(4*_scale)}px;"
DEFAULT_LABEL_PADDING = f"padding-bottom: {int(4*_scale)}px;"

# Layout spacing adjustments
ROW_SPACING_REDUCTION = int(-14 * _scale)
NOTES_FIXED_HEIGHT = int(75 * _scale)

# Shadow and highlight effects
SHADOW_OFFSETS = [int(x*_scale) for x in [8, 6, 4]]  # Multiple layers for depth
SHADOW_ALPHAS = [40, 60, 90]  # Increasing opacity for each layer
HIGHLIGHT_ALPHAS = [30, 50, 80]  # Slightly less intense than shadows

# Math Domains specific
MATH_DOMAINS_BG = NEUMORPH_BG_COLOR
MATH_DOMAINS_BTN_BG = NEUMORPH_BG_COLOR
MATH_DOMAINS_BTN_HOVER = "#f2f2f2"
MATH_DOMAINS_BTN_TEXT = BASE_FONT_COLOR

# Left Panel specific
LEFT_PANEL_WIDTH = int(820 * _scale)
LEFT_PANEL_BG = NEUMORPH_BG_COLOR
LEFT_PANEL_PADDING = PADDING
LEFT_PANEL_SPACING = SPACING

# Checkbox styling
CHECKBOX_SIZE = int(22 * _scale)
CHECKBOX_PADDING = int(8 * _scale)
CHECKBOX_BORDER_RADIUS = int(12 * _scale)

# Category panel/button specific
CATEGORY_BTN_WIDTH = int(120 * _scale)
CATEGORY_BTN_HEIGHT = int(32 * _scale)
CATEGORY_BTN_SELECTED_COLOR = "#cce5ff"
CATEGORY_PANEL_SPACING = int(8 * _scale)

SAT_TYPE_PANEL_SPACING = int(6 * _scale)
DOMAIN_GRID_SPACING = int(13 * _scale)
DOMAIN_BTN_WIDTH = int(220 * _scale)
DOMAIN_BTN_HEIGHT = int(58 * _scale)
SECTION_LABEL_PADDING_TOP = f"padding-top: {int(10*_scale)}px;"

EDITOR_FONT_FAMILY = FONT_FAMILY
EDITOR_FONT_SIZE = LABEL_FONT_SIZE
PREVIEW_LABEL_MIN_WIDTH = int(400 * _scale)
PREVIEW_LABEL_MIN_HEIGHT = int(300 * _scale)

BUTTON_MIN_WIDTH = int(140 * _scale)
BUTTON_MIN_HEIGHT = int(56 * _scale)
ENTRY_MIN_HEIGHT = int(44 * _scale)
ENTRY_PADDING_LEFT = int(14 * _scale)
TEXTEDIT_PADDING = int(16 * _scale)
SHADOW_RECT_ADJUST = int(8 * _scale)  # Used for rect.adjusted(8, 8, -8, -8)

CONTROL_BTN_FONT_SIZE = int(17 * _scale)

# ... rest of the file remains unchanged ... 