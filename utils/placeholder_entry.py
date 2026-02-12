import tkinter as tk
from tkinter import ttk
from config.config import COLOR_TEXT_MAIN, COLOR_TEXT_MUTED
class PlaceholderEntry(ttk.Entry):
    def __init__(self, master, placeholder, show=None, **kwargs):
        super().__init__(master, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = COLOR_TEXT_MUTED
        self.default_fg = COLOR_TEXT_MAIN

        self.show_character = show  # actual masking character
        self.is_password = show is not None

        self.put_placeholder()

        self.bind("<FocusIn>", self.remove_placeholder)
        self.bind("<FocusOut>", self.add_placeholder)

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self.config(foreground=self.placeholder_color)

        # IMPORTANT: placeholder should NOT be masked
        if self.is_password:
            self.config(show="")

    def remove_placeholder(self, event=None):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(foreground=self.default_fg)

            # Enable masking when user starts typing
            if self.is_password:
                self.config(show=self.show_character)

    def add_placeholder(self, event=None):
        if not self.get():
            self.put_placeholder()
