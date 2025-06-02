from ui_qt.palette_manager import palette_manager

class PaletteAwareMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        palette_manager.palette_changed.connect(self.on_palette_changed)

    def on_palette_changed(self):
        self.update()  # Override in your widget to update style or cached values 