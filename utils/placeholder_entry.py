import tkinter as tk
from tkinter import ttk


class PlaceholderEntry(ttk.Entry):
    def __init__(self, master, placeholder, **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.insert(0, placeholder)
        self.config(foreground="#898989")
        self.bind("<FocusIn>", self.remove_placeholder)
        self.bind("<FocusOut>", self.add_placeholder)
    
    def remove_placeholder(self, event=None):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(foreground="#111111")

    def add_placeholder(self, event=None):
        if self.get() == "":
            self.insert(0, self.placeholder)
            self.config(foreground="#898989")
