# Centralized style configuration for the Math Editor UI

import sys
import json
import os
import json as _json
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QPainter, QColor, QBrush, QFont
from PyQt5.QtCore import Qt

# --- Base (unscaled) values ---
# Font Sizes
BASE_HEAD_1_FONT_SIZE = 20
BASE_HEAD_2_FONT_SIZE = 18
BASE_HEAD_3_FONT_SIZE = 15
BASE_HEAD_4_FONT_SIZE = 13
BASE_TEXT_1_FONT_SIZE = 14
BASE_TEXT_2_FONT_SIZE = 13
BASE_TEXT_3_FONT_SIZE = 12

BASE_CONTROL_BTN_WIDTH = 240
BASE_CONTROL_BTN_HEIGHT = 56
BASE_ENTRY_HEIGHT = 44
BASE_NOTES_MIN_HEIGHT = 100
BASE_PADDING = 30
BASE_SPACING = 28
BASE_SECTION_SPACING = 18
BASE_PROB_ID_ENTRY_WIDTH = 120
BASE_SEARCH_TEXT_ENTRY_WIDTH = 280
BASE_ANSWER_ENTRY_WIDTH = 320
BASE_ROW_SPACING_REDUCTION = -24
BASE_NOTES_FIXED_HEIGHT = 75
BASE_LEFT_PANEL_WIDTH = 1000
BASE_CHECKBOX_SIZE = 22
BASE_CHECKBOX_PADDING = 8
BASE_CHECKBOX_BORDER_RADIUS = 12
BASE_CATEGORY_BTN_WIDTH = 180
BASE_CATEGORY_BTN_HEIGHT = 36
BASE_CATEGORY_PANEL_SPACING = 8
BASE_DOMAIN_GRID_SPACING = 13
BASE_DOMAIN_BTN_WIDTH = 220
BASE_DOMAIN_BTN_HEIGHT = 58
BASE_SECTION_LABEL_PADDING_TOP = 10
BASE_BUTTON_MIN_WIDTH = 220
BASE_BUTTON_MIN_HEIGHT = 56
BASE_BUTTON_TEXT_PADDING = 40  # Padding on each side of button text
BASE_ENTRY_MIN_HEIGHT = 44
BASE_ENTRY_PADDING_LEFT = 14
BASE_TEXTEDIT_PADDING = 16
BASE_SHADOW_RECT_ADJUST = 8

# --- Scaled values (set by set_scale) ---
LABEL_FONT_SIZE = None
SECTION_LABEL_FONT_SIZE = None
BUTTON_FONT_SIZE = None
ENTRY_FONT_SIZE = None
NOTES_FONT_SIZE = None
CONTROL_BTN_FONT_SIZE = None
CONTROL_BTN_WIDTH = None
CONTROL_BTN_HEIGHT = None
ENTRY_HEIGHT = None
NOTES_MIN_HEIGHT = None
PADDING = None
SPACING = None
SECTION_SPACING = None
PROB_ID_ENTRY_WIDTH = None
SEARCH_TEXT_ENTRY_WIDTH = None
ANSWER_ENTRY_WIDTH = None
ROW_SPACING_REDUCTION = None
NOTES_FIXED_HEIGHT = None
LEFT_PANEL_WIDTH = None
CHECKBOX_SIZE = None
CHECKBOX_PADDING = None
CHECKBOX_BORDER_RADIUS = None
CATEGORY_BTN_WIDTH = None
CATEGORY_BTN_HEIGHT = None
CATEGORY_PANEL_SPACING = None
DOMAIN_GRID_SPACING = None
DOMAIN_BTN_WIDTH = None
DOMAIN_BTN_HEIGHT = None
SECTION_LABEL_PADDING_TOP = None
BUTTON_MIN_WIDTH = None
BUTTON_MIN_HEIGHT = None
BUTTON_TEXT_PADDING = None
ENTRY_MIN_HEIGHT = None
ENTRY_PADDING_LEFT = None
TEXTEDIT_PADDING = None
SHADOW_RECT_ADJUST = None
SET_EDITOR_BTN_FONT_SIZE = None
SET_EDITOR_HEAD_FONT_SIZE = None
SET_EDITOR_CONTROL_BUTTON_FONT_SIZE = None
SET_EDITOR_BUTTON_FONT_SIZE = None
SET_EDITOR_LABEL_FONT_SIZE = None

# --- Scaling profiles ---
SCALING_PROFILES = {
    "main": 1.0,
    "laptop": 0.8
}

_scale = 1.0

def set_scale(profile="main"):
    global _scale
    _scale = SCALING_PROFILES.get(profile, 1.0)
    global LABEL_FONT_SIZE, SECTION_LABEL_FONT_SIZE, BUTTON_FONT_SIZE, ENTRY_FONT_SIZE, NOTES_FONT_SIZE, CONTROL_BTN_FONT_SIZE
    global CONTROL_BTN_WIDTH, CONTROL_BTN_HEIGHT, ENTRY_HEIGHT, NOTES_MIN_HEIGHT, PADDING, SPACING, SECTION_SPACING
    global PROB_ID_ENTRY_WIDTH, SEARCH_TEXT_ENTRY_WIDTH, ANSWER_ENTRY_WIDTH, ROW_SPACING_REDUCTION, NOTES_FIXED_HEIGHT
    global LEFT_PANEL_WIDTH, CHECKBOX_SIZE, CHECKBOX_PADDING, CHECKBOX_BORDER_RADIUS
    global CATEGORY_BTN_WIDTH, CATEGORY_BTN_HEIGHT, CATEGORY_PANEL_SPACING
    global DOMAIN_GRID_SPACING, DOMAIN_BTN_WIDTH, DOMAIN_BTN_HEIGHT, SECTION_LABEL_PADDING_TOP
    global BUTTON_MIN_WIDTH, BUTTON_MIN_HEIGHT, ENTRY_MIN_HEIGHT, ENTRY_PADDING_LEFT, TEXTEDIT_PADDING, SHADOW_RECT_ADJUST
    global SET_EDITOR_BTN_FONT_SIZE, SET_EDITOR_HEAD_FONT_SIZE, SET_EDITOR_CONTROL_BUTTON_FONT_SIZE, SET_EDITOR_BUTTON_FONT_SIZE, SET_EDITOR_LABEL_FONT_SIZE
    SECTION_LABEL_FONT_SIZE = int(BASE_HEAD_1_FONT_SIZE * _scale)
    CONTROL_BTN_FONT_SIZE = int(BASE_HEAD_2_FONT_SIZE * _scale)
    BUTTON_FONT_SIZE = int(BASE_HEAD_3_FONT_SIZE * _scale)
    LABEL_FONT_SIZE = int(BASE_TEXT_1_FONT_SIZE * _scale)
    ENTRY_FONT_SIZE = int(BASE_TEXT_2_FONT_SIZE * _scale)
    NOTES_FONT_SIZE = ENTRY_FONT_SIZE
    SET_EDITOR_BTN_FONT_SIZE = int(BASE_HEAD_4_FONT_SIZE * _scale)
    SET_EDITOR_HEAD_FONT_SIZE = int(BASE_HEAD_2_FONT_SIZE * _scale)
    SET_EDITOR_CONTROL_BUTTON_FONT_SIZE = int(BASE_HEAD_3_FONT_SIZE * _scale)
    SET_EDITOR_BUTTON_FONT_SIZE = int(BASE_TEXT_1_FONT_SIZE * _scale)
    SET_EDITOR_LABEL_FONT_SIZE = int(BASE_TEXT_1_FONT_SIZE * _scale)
    CONTROL_BTN_WIDTH = int(BASE_CONTROL_BTN_WIDTH * _scale)
    CONTROL_BTN_HEIGHT = int(BASE_CONTROL_BTN_HEIGHT * _scale)
    ENTRY_HEIGHT = int(BASE_ENTRY_HEIGHT * _scale)
    NOTES_MIN_HEIGHT = int(BASE_NOTES_MIN_HEIGHT * _scale)
    PADDING = int(BASE_PADDING * _scale)
    SPACING = int(BASE_SPACING * _scale)
    SECTION_SPACING = int(BASE_SECTION_SPACING * _scale)
    PROB_ID_ENTRY_WIDTH = int(BASE_PROB_ID_ENTRY_WIDTH * _scale)
    SEARCH_TEXT_ENTRY_WIDTH = int(BASE_SEARCH_TEXT_ENTRY_WIDTH * _scale)
    ANSWER_ENTRY_WIDTH = int(BASE_ANSWER_ENTRY_WIDTH * _scale)
    ROW_SPACING_REDUCTION = int(BASE_ROW_SPACING_REDUCTION * _scale)
    NOTES_FIXED_HEIGHT = int(BASE_NOTES_FIXED_HEIGHT * _scale)
    LEFT_PANEL_WIDTH = int(BASE_LEFT_PANEL_WIDTH * _scale)
    CHECKBOX_SIZE = int(BASE_CHECKBOX_SIZE * _scale)
    CHECKBOX_PADDING = int(BASE_CHECKBOX_PADDING * _scale)
    CHECKBOX_BORDER_RADIUS = int(BASE_CHECKBOX_BORDER_RADIUS * _scale)
    CATEGORY_BTN_WIDTH = int(BASE_CATEGORY_BTN_WIDTH * _scale)
    CATEGORY_BTN_HEIGHT = int(BASE_CATEGORY_BTN_HEIGHT * _scale)
    CATEGORY_PANEL_SPACING = int(BASE_CATEGORY_PANEL_SPACING * _scale)
    DOMAIN_GRID_SPACING = int(BASE_DOMAIN_GRID_SPACING * _scale)
    DOMAIN_BTN_WIDTH = int(BASE_DOMAIN_BTN_WIDTH * _scale)
    DOMAIN_BTN_HEIGHT = int(BASE_DOMAIN_BTN_HEIGHT * _scale)
    SECTION_LABEL_PADDING_TOP = f"padding-top: {int(BASE_SECTION_LABEL_PADDING_TOP*_scale)}px;"
    BUTTON_MIN_WIDTH = int(BASE_BUTTON_MIN_WIDTH * _scale)
    BUTTON_MIN_HEIGHT = int(BASE_BUTTON_MIN_HEIGHT * _scale)
    BUTTON_TEXT_PADDING = int(BASE_BUTTON_TEXT_PADDING * _scale)
    ENTRY_MIN_HEIGHT = int(BASE_ENTRY_MIN_HEIGHT * _scale)
    ENTRY_PADDING_LEFT = int(BASE_ENTRY_PADDING_LEFT * _scale)
    TEXTEDIT_PADDING = int(BASE_TEXTEDIT_PADDING * _scale)
    SHADOW_RECT_ADJUST = int(BASE_SHADOW_RECT_ADJUST * _scale)

# Set initial scale (choose "main" or "laptop")
set_scale("main")

print(f"===================SECTION_LABEL_FONT_SIZE: {SECTION_LABEL_FONT_SIZE}")
print(f"===================CONTROL_BTN_FONT_SIZE: {CONTROL_BTN_FONT_SIZE}")
print(f"===================BUTTON_FONT_SIZE: {BUTTON_FONT_SIZE}")
print(f"===================LABEL_FONT_SIZE: {LABEL_FONT_SIZE}")
print(f"===================ENTRY_FONT_SIZE: {ENTRY_FONT_SIZE}")
print(f"===================NOTES_FONT_SIZE: {NOTES_FONT_SIZE}")

# Font settings
FONT_FAMILY = "Courier"  # Base font family
FONT_WEIGHT = "Bold"     # Base font weight
LABEL_FONT_COLOR = "#031282"
SECTION_LABEL_FONT_COLOR = "#031282"
BUTTON_FONT_COLOR = "#031282"
ENTRY_FONT_COLOR = "#031282"
NOTES_FONT_COLOR = "#031282"

# Base colors
BASE_FONT_COLOR = "#031282"  # Darker text for better contrast

# --- Palette support ---
class NeumorphPalette:
    def __init__(self, d):
        self.name = d.get("name", "Unnamed")
        self.window_bg_color = d.get("window_bg_color", d.get("bg_color", "#f0f0f3"))
        self.bg_color = d.get("bg_color", "#f0f0f3")
        self.entry_bg_color = d.get("entry_bg_color", "#e8e8e8")
        self.editor_bg_color = d.get("editor_bg_color", "#ffffff")
        self.shadow_dark = d.get("shadow_dark", "#c4c2b8")
        self.shadow_light = d.get("shadow_light", "#ffffff")
        self.text_color = d.get("text_color", "#031282")
        self.gradient_start = d.get("gradient_start", "#f7f7fa")
        self.gradient_end = d.get("gradient_end", "#f0f0f3")
        self.radius = d.get("radius", 18)
        self.button_radius = d.get("button_radius", 12)
        self.button_padding = d.get("button_padding", "10px 20px")

active_palette = None
WINDOW_BG_COLOR = None
ENTRY_BG_COLOR = "#e8e8e8"
EDITOR_BG_COLOR = "#ffffff"

def set_active_palette(palette: NeumorphPalette):
    global active_palette
    active_palette = palette
    global NEUMORPH_BG_COLOR, NEUMORPH_SHADOW_DARK, NEUMORPH_SHADOW_LIGHT, NEUMORPH_TEXT_COLOR
    global NEUMORPH_GRADIENT_START, NEUMORPH_GRADIENT_END, NEUMORPH_RADIUS
    global WINDOW_BG_COLOR, ENTRY_BG_COLOR, EDITOR_BG_COLOR
    NEUMORPH_BG_COLOR = palette.bg_color
    NEUMORPH_SHADOW_DARK = palette.shadow_dark
    NEUMORPH_SHADOW_LIGHT = palette.shadow_light
    NEUMORPH_TEXT_COLOR = palette.text_color
    NEUMORPH_GRADIENT_START = palette.gradient_start
    NEUMORPH_GRADIENT_END = palette.gradient_end
    NEUMORPH_RADIUS = int(palette.radius * _scale)
    WINDOW_BG_COLOR = palette.window_bg_color
    ENTRY_BG_COLOR = palette.entry_bg_color
    EDITOR_BG_COLOR = palette.editor_bg_color

# Default palette (used if no palette is loaded)
default_palette_dict = {
    "name": "Light",
    "bg_color": "#f0f0f3",
    "shadow_dark": "#c4c2b8",
    "shadow_light": "#ffffff",
    "text_color": "#031282",
    "gradient_start": "#f7f7fa",
    "gradient_end": "#f0f0f3",
    "radius": 18,
    "button_radius": 12,
    "button_padding": "10px 20px"
}
set_active_palette(NeumorphPalette(default_palette_dict))

# Component-specific colors
BUTTON_BG_COLOR = NEUMORPH_BG_COLOR
BUTTON_HOVER_COLOR = "#f2f2f2"
BUTTON_BORDER_RADIUS = NEUMORPH_RADIUS
BUTTON_HIGHLIGHT_COLOR = "#cce5ff"

ENTRY_BORDER_RADIUS = int(14 * _scale)
ENTRY_SHADOW_COLOR = "#c8c8c8"

NOTES_BG_COLOR = NEUMORPH_BG_COLOR
NOTES_BORDER_RADIUS = NEUMORPH_RADIUS
NOTES_PADDING = int(16 * _scale)

# Layout and sizing
CONTROL_BTN_WIDTH = int(240 * _scale)
CONTROL_BTN_HEIGHT = int(56 * _scale)
ENTRY_HEIGHT = int(48 * _scale)
NOTES_MIN_HEIGHT = int(1 * _scale)
PADDING = int(10 * _scale)
SPACING = int(10 * _scale)
SECTION_SPACING = int(28 * _scale)

# Entry field specific widths
PROB_ID_ENTRY_WIDTH = int(120 * _scale)
SEARCH_TEXT_ENTRY_WIDTH = int(280 * _scale)
ANSWER_ENTRY_WIDTH = int(320 * _scale)

# Entry field label padding
SEARCH_TEXT_LABEL_PADDING = f"padding-left: {int(16*_scale)}px; padding-bottom: {int(4*_scale)}px;"
ANSWER_LABEL_PADDING = f"padding-left: {int(50*_scale)}px; padding-bottom: {int(4*_scale)}px;"
DEFAULT_LABEL_PADDING = f"padding-bottom: {int(4*_scale)}px;"

# Layout spacing adjustments
NOTES_FIXED_HEIGHT = int(75 * _scale)

# Enhanced shadow and highlight effects for more pronounced neumorphism
SHADOW_OFFSETS = [int(x*_scale) for x in [12, 8, 6, 4]]  # More layers with greater depth
SHADOW_ALPHAS = [35, 50, 70, 95]  # Increasing opacity for each layer
HIGHLIGHT_OFFSETS = [int(x*_scale) for x in [10, 6, 4, 2]]  # Separate offsets for highlights
HIGHLIGHT_ALPHAS = [40, 60, 85, 110]  # More intense highlights for better contrast

# Blue-tinted shadow color to complement navy blue text (#031282)
NEUMORPH_SHADOW_BLUE = "#9ba3c7"  # Subtle blue-gray shadow that harmonizes with navy text

# Math Domains specific
MATH_DOMAINS_BG = NEUMORPH_BG_COLOR
MATH_DOMAINS_BTN_BG = NEUMORPH_BG_COLOR
MATH_DOMAINS_BTN_HOVER = "#f2f2f2"
MATH_DOMAINS_BTN_TEXT = "#031282"

# Left Panel specific
# LEFT_PANEL_WIDTH = int(820 * _scale)
LEFT_PANEL_BG = NEUMORPH_BG_COLOR
print(f"---------------LEFT_PANEL_BG: {LEFT_PANEL_BG}")
LEFT_PANEL_PADDING = PADDING
LEFT_PANEL_SPACING = SPACING

# Checkbox styling
CHECKBOX_SIZE = int(22 * _scale)
CHECKBOX_PADDING = int(8 * _scale)
CHECKBOX_BORDER_RADIUS = int(12 * _scale)

# Category panel/button specific
CATEGORY_BTN_WIDTH = int(BASE_CATEGORY_BTN_WIDTH * _scale)
CATEGORY_BTN_HEIGHT = int(BASE_CATEGORY_BTN_HEIGHT * _scale)
CATEGORY_BTN_SELECTED_COLOR = "#cce5ff"
CATEGORY_PANEL_SPACING = int(BASE_CATEGORY_PANEL_SPACING * _scale)

DOMAIN_GRID_SPACING = int(13 * _scale)
DOMAIN_BTN_WIDTH = int(220 * _scale)
DOMAIN_BTN_HEIGHT = int(58 * _scale)
SECTION_LABEL_PADDING_TOP = f"padding-top: {int(10*_scale)}px;"

EDITOR_FONT_FAMILY = FONT_FAMILY
EDITOR_FONT_SIZE = LABEL_FONT_SIZE
PREVIEW_LABEL_MIN_WIDTH = int(400 * _scale)
PREVIEW_LABEL_MIN_HEIGHT = int(300 * _scale)

BUTTON_MIN_WIDTH = int(160 * _scale)
BUTTON_MIN_HEIGHT = int(56 * _scale)
BUTTON_TEXT_PADDING = int(40 * _scale)
ENTRY_MIN_HEIGHT = int(44 * _scale)
ENTRY_PADDING_LEFT = int(14 * _scale)
TEXTEDIT_PADDING = int(16 * _scale)
SHADOW_RECT_ADJUST = int(8 * _scale)  # Used for rect.adjusted(8, 8, -8, -8)

def _load_palette_name():
    config_path = os.path.join(os.getcwd(), "default_config.json")
    if not os.path.exists(config_path):
        return None
    with open(config_path, "r") as f:
        config = _json.load(f)
    return config.get("palette_name", None)

def _load_palettes():
    palettes_path = os.path.join(os.getcwd(), "resources", "palettes.json")
    if not os.path.exists(palettes_path):
        return [NeumorphPalette(default_palette_dict)]
    with open(palettes_path, "r") as f:
        data = _json.load(f)
    palettes_data = data["palettes"] if isinstance(data, dict) and "palettes" in data else data
    return [NeumorphPalette(d) for d in palettes_data]

def _choose_palette(palettes, name):
    for p in palettes:
        if getattr(p, "name", None) == name:
            return p
    return palettes[0] if palettes else NeumorphPalette(default_palette_dict)

# Load and set the palette at import time
_palette_name = _load_palette_name()
_palettes = _load_palettes()
_selected_palette = _choose_palette(_palettes, _palette_name)
# set_active_palette(_selected_palette)

class MultiShadowButton(QPushButton):
    def __init__(self, text, palette, parent=None):
        super().__init__(text, parent)
        self.palette = palette
        self.setFont(QFont(FONT_FAMILY, BUTTON_FONT_SIZE, QFont.Bold))
        self.setStyleSheet(f"""
            QPushButton {{
                border-radius: {palette.button_radius}px;
                color: {palette.text_color};
                padding: {palette.button_padding};
                background: {palette.bg_color} !important;
                background-color: {palette.bg_color} !important;
            }}
            QPushButton:hover {{
                background-color: {palette.shadow_light} !important;
            }}
        """)
        self.setMinimumHeight(40)

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            rect = self.rect().adjusted(4, 4, -4, -4)
            radius = self.palette.button_radius
            # First shadow (shadow_dark, offset down/right)
            shadow1_color = QColor(self.palette.shadow_dark)
            shadow1_color.setAlpha(80)
            painter.setBrush(QBrush(shadow1_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect.translated(3, 3), radius, radius)
            # Second shadow (gradient_start, offset up/left)
            shadow2_color = QColor(self.palette.gradient_start)
            shadow2_color.setAlpha(50)
            painter.setBrush(QBrush(shadow2_color))
            painter.drawRoundedRect(rect.translated(-2, -2), radius, radius)
            # Button background
            painter.setBrush(QBrush(QColor(self.palette.bg_color)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect, radius, radius)
            # Draw the button text and icon as usual
            painter.setFont(QFont(FONT_FAMILY, BUTTON_FONT_SIZE, QFont.Bold))
            super().paintEvent(event)
        finally:
            painter.end() 