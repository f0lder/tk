import tkinter as tk
from tkinter import ttk
import theme
from theme import (
    BG_SIDEBAR, BG_DARK, ACCENT_PRIMARY, TEXT_MUTED,
    FONT_HEADING, FONT_LABEL, FONT_VALUE_MEDIUM, FONT_TINY,
    PAD_LARGE, PAD_MEDIUM, PAD_SMALL,
    set_font_scale, get_font_scale
)

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings")
        self.geometry("400x300")
        self.configure(bg=BG_SIDEBAR)

        main_frame = ttk.Frame(self, style='TFrame')
        main_frame.pack(padx=PAD_LARGE, pady=PAD_LARGE, fill='both', expand=True)

        # Font Size Section
        font_section = ttk.Frame(main_frame, style='TFrame')
        font_section.pack(fill='x', pady=PAD_MEDIUM)
        
        font_header = ttk.Label(font_section, text="Font Size", font=FONT_HEADING, background=BG_SIDEBAR)
        font_header.pack(anchor='w')
        
        font_row = ttk.Frame(font_section, style='TFrame')
        font_row.pack(fill='x', pady=PAD_SMALL)
        
        ttk.Label(font_row, text="Scale:", font=FONT_LABEL, background=BG_SIDEBAR).pack(side='left')
        
        # Get current scale
        current_scale = int(get_font_scale() * 100)
        self.font_scale = tk.IntVar(value=current_scale)
        
        self.scale_label = ttk.Label(font_row, text=f"{self.font_scale.get()}%", font=FONT_VALUE_MEDIUM, 
                                      foreground=ACCENT_PRIMARY, background=BG_SIDEBAR, width=5)
        self.scale_label.pack(side='right')
        
        self.font_slider = ttk.Scale(
            font_section, from_=70, to=150,
            variable=self.font_scale, 
            command=self.on_font_scale_change,
            style='Horizontal.TScale'
        )
        self.font_slider.pack(fill='x', pady=PAD_SMALL)
        
        # Scale labels
        scale_labels = ttk.Frame(font_section, style='TFrame')
        scale_labels.pack(fill='x')
        ttk.Label(scale_labels, text="70%", font=FONT_TINY, foreground=TEXT_MUTED, background=BG_SIDEBAR).pack(side='left')
        ttk.Label(scale_labels, text="150%", font=FONT_TINY, foreground=TEXT_MUTED, background=BG_SIDEBAR).pack(side='right')

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side='bottom', fill='x', pady=(PAD_MEDIUM, 0))

        ok_button = ttk.Button(button_frame, text="Apply", command=self.apply_settings)
        ok_button.pack(side='right', padx=PAD_SMALL)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side='right')

        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def on_font_scale_change(self, value):
        """Update the scale label as slider moves"""
        scale = int(float(value))
        self.scale_label.config(text=f"{scale}%")
    
    def apply_settings(self):
        """Apply font scale and refresh the UI"""
        scale = self.font_scale.get() / 100.0
        set_font_scale(scale)
        
        # Update the static font tuples in the theme module
        self._update_theme_fonts(scale)
        
        # Close settings window first
        self.destroy()
        
        # Rebuild the sidebar UI
        if hasattr(self.parent, 'rebuild_sidebar'):
            self.parent.rebuild_sidebar()
    
    def _update_theme_fonts(self, scale):
        """Update the static font tuples in theme module"""
        def scaled(base_size, bold=False):
            size = max(6, int(base_size * scale))
            if bold:
                return (theme.FONT_FAMILY, size, "bold")
            return (theme.FONT_FAMILY, size)
        
        # Update all font constants
        theme.FONT_TITLE = scaled(14, bold=True)
        theme.FONT_HEADING = scaled(12, bold=True)
        theme.FONT_NORMAL = scaled(10)
        theme.FONT_SMALL = scaled(9)
        theme.FONT_TINY = scaled(8)
        theme.FONT_MINI = scaled(7)
        theme.FONT_MICRO = scaled(6)
        theme.FONT_VALUE_LARGE = scaled(20, bold=True)
        theme.FONT_VALUE_MEDIUM = scaled(12, bold=True)
        theme.FONT_VALUE_SMALL = scaled(10, bold=True)
        theme.FONT_LABEL = scaled(9)
        theme.FONT_LABEL_BOLD = scaled(9, bold=True)
        theme.FONT_SCORE = scaled(11, bold=True)
        theme.FONT_STATUS = scaled(8, bold=True)
        
        # Update padding to scale with fonts
        theme.update_padding_scale()
