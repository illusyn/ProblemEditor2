import tkinter as tk
from tkinter import ttk

class SatTypePanel(ttk.Frame):
    """Panel for multi-selecting SAT problem types"""
    def __init__(self, parent, types=None):
        super().__init__(parent)
        self.types = types or []
        self.selected_types = set()
        self.buttons = {}
        self.vars = {}  # Store BooleanVars for each type
        self._build_panel()

    def _build_panel(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.buttons.clear()
        self.vars.clear()
        for t in self.types:
            var = tk.BooleanVar(value=(t in self.selected_types))
            btn = ttk.Checkbutton(
                self,
                text=t,
                variable=var,
                command=lambda t=t: self.toggle_type(t)
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            self.buttons[t] = btn
            self.vars[t] = var

    def set_types(self, types):
        self.types = types
        self._build_panel()

    def toggle_type(self, t):
        var = self.vars[t]
        if var.get():
            self.selected_types.add(t)
        else:
            self.selected_types.discard(t)
        # No need to call update_button_states; vars drive UI

    def set_selected_types(self, types):
        self.selected_types = set(types)
        for t, var in self.vars.items():
            var.set(t in self.selected_types)

    def get_selected_types(self):
        # Return types where the variable is True
        return [t for t, var in self.vars.items() if var.get()] 