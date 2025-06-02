from PyQt5.QtCore import QObject, pyqtSignal
from ui_qt.style_config import set_active_palette, NeumorphPalette, PALETTES

class PaletteManager(QObject):
    palette_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._current_palette = None

    def set_palette(self, palette_name):
        palette_dict = PALETTES.get(palette_name)
        if palette_dict:
            set_active_palette(NeumorphPalette(palette_dict))
            self._current_palette = palette_name
            self.palette_changed.emit()

    def current_palette(self):
        return self._current_palette

# Singleton instance
palette_manager = PaletteManager() 