import tkinter as tk
from tkinter import ttk
from theme import *
import webbrowser
from ttkbootstrap_icons_fa.icon import FAIcon

class AboutWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About Neuro-Traffic")
        self.geometry("400x300")
        self.configure(bg=BG_SIDEBAR)

        outer_frame = ttk.Frame(self, style='TFrame')
        outer_frame.pack(fill='both', expand=True)

        main_frame = ttk.Frame(outer_frame, style='TFrame')
        
        title_label = ttk.Label(main_frame, text="Neuro-Traffic", font=FONT_TITLE, foreground=ACCENT_PRIMARY, background=BG_SIDEBAR)
        title_label.pack(pady=(0, PAD_SMALL))
        
        desc_text = "A real-time traffic simulation with an intelligent fuzzy logic controller."
        desc_label = ttk.Label(main_frame, text=desc_text, wraplength=350, justify='center', background=BG_SIDEBAR)
        desc_label.pack(pady=PAD_SMALL)

        version_label = ttk.Label(main_frame, text="Version 1.0", font=FONT_SMALL, foreground=TEXT_MUTED, background=BG_SIDEBAR)
        version_label.pack()

        tech_frame = ttk.Frame(main_frame, style='TFrame')
        tech_frame.pack(pady=PAD_LARGE)

        tech_title = ttk.Label(tech_frame, text="Built with:", font=FONT_LABEL_BOLD, background=BG_SIDEBAR)
        tech_title.pack(pady=(0, PAD_SMALL))

        icons_frame = ttk.Frame(tech_frame, style='TFrame')
        icons_frame.pack()

        self.create_icon(icons_frame, "python", "Python", style='brands')
        self.create_icon(icons_frame, "window-maximize", "Tkinter")
        self.create_icon(icons_frame, "brain", "Fuzzy Logic")

        portfolio_label = ttk.Label(main_frame, text="https://fldr.xyz", font=FONT_SMALL, foreground=ACCENT_PRIMARY, background=BG_SIDEBAR)
        portfolio_label.pack(pady=PAD_MEDIUM)
        portfolio_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://fldr.xyz"))
        portfolio_label.bind("<Enter>", lambda e: portfolio_label.config(cursor="hand2"))
        portfolio_label.bind("<Leave>", lambda e: portfolio_label.config(cursor=""))

        made_by_label = ttk.Label(main_frame, text="Made with <3 by f0lder", font=FONT_SMALL, foreground=TEXT_MUTED, background=BG_SIDEBAR)
        made_by_label.pack(pady=(PAD_LARGE, 0))
        
        ok_button = ttk.Button(main_frame, text="OK", command=self.destroy)
        ok_button.pack(pady=(PAD_LARGE, 0))

        main_frame.place(relx=0.5, rely=0.5, anchor='center')

        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def create_icon(self, parent, icon_name, text, style=None):
        icon_frame = ttk.Frame(parent, style='TFrame')
        
        # Icon image
        img = FAIcon(icon_name, color=ACCENT_PRIMARY, size=24, style=style).image
        icon_label = ttk.Label(icon_frame, image=img, background=BG_SIDEBAR)
        icon_label.image = img
        icon_label.pack()
        
        # Text label
        label = ttk.Label(icon_frame, text=text, font=FONT_TINY, background=BG_SIDEBAR)
        label.pack()
        
        icon_frame.pack(side='left', padx=PAD_SMALL)