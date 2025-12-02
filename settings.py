import tkinter as tk
from tkinter import ttk
from theme import *

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("400x300")
        self.configure(bg=BG_SIDEBAR)

        main_frame = ttk.Frame(self, style='TFrame')
        main_frame.pack(padx=PAD_LARGE, pady=PAD_LARGE, fill='both', expand=True)

        placeholder_label = ttk.Label(main_frame, text="Settings will be here.", font=FONT_HEADING, background=BG_SIDEBAR)
        placeholder_label.pack(pady=PAD_LARGE)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side='bottom', fill='x', pady=(PAD_MEDIUM, 0))

        ok_button = ttk.Button(button_frame, text="OK", command=self.destroy)
        ok_button.pack(side='right', padx=PAD_SMALL)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side='right')

        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)
