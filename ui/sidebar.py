import tkinter as tk
from tkinter import ttk
from config.config import (PAD_SMALL, PAD_MEDIUM)

def setup_sidebar(app):
    """Left sidebar styled from config colors, with active button handling"""

    app.sidebar_buttons = {}
    app.active_sidebar = None

    app.sidebar_frame = ttk.Frame(
        app.main_frame,
        width=220,
        style="Card.TFrame",
        padding=(PAD_SMALL, PAD_MEDIUM)
    )
    app.sidebar_frame.pack(side="left", fill="y")
    app.sidebar_frame.pack_propagate(False)

    # --- Sidebar Buttons ---
    nav_items = [
        ("🏠 Dashboard", app.show_dashboard),
        ("➕ New Patient", app.open_patient_form),
        ("📋 Patients List", app.show_patients),
        ("➕ Add Visit", app.open_quick_visit),
        ("📜 Visit History", app.show_visit_history),
        ("📊 Reports", app.show_dashboard),
        ("⚙️ Settings", app.open_user_management),
    ]

    for text, command in nav_items:
        btn = ttk.Button(
            app.sidebar_frame,
            text=text,
            command=lambda c=command, t=text: on_sidebar_click(app, t, c),
            style="Sidebar.TButton"
        )
        btn.pack(fill="x", pady=2)
        app.sidebar_buttons[text] = btn

    # default active

    set_active_sidebar(app, "🏠 Dashboard")


def on_sidebar_click(app, label, callback):
    set_active_sidebar(app, label)
    callback()


def set_active_sidebar(app, label):
    if app.active_sidebar:
        app.sidebar_buttons[app.active_sidebar].configure(
            style="Sidebar.TButton"
        )

    app.active_sidebar = label
    app.sidebar_buttons[label].configure(
        style="SidebarActive.TButton"
    )