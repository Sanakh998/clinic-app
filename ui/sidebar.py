import tkinter as tk
from tkinter import ttk
from config.config import (PAD_SMALL, PAD_MEDIUM, COLOR_SURFACE, COLOR_ACCENT)
from PIL import Image, ImageTk
from utils.resource_path import resource_path

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
        ("Dashboard", "assets/icons/home.png", app.show_dashboard),
        ("New Patient", "assets/icons/add-user.png", app.open_patient_form),
        ("Patients List", "assets/icons/list.png", app.show_patients),
        ("Add Visit", "assets/icons/add-visit.png", app.open_quick_visit),
        ("Visit History", "assets/icons/history.png", app.show_visit_history),
        ("Reports", "assets/icons/chart.png", app.show_earnings),
        ("Medicines", "assets/icons/pill.png", app.show_medicine_inventory),
        ("Settings", "assets/icons/settings.png", app.open_user_management),
    ]


    app.sidebar_icons = {}

    for text, icon_path, command in nav_items:

        full_path = resource_path(icon_path)
        img = Image.open(full_path).resize((20, 20))
        icon = ImageTk.PhotoImage(img)

        app.sidebar_icons[text] = icon  # prevent garbage collection

        btn = ttk.Button(
            app.sidebar_frame,
            text="  " + text,
            image=icon,
            compound="left",
            style="Sidebar.TButton",
            cursor="hand2",
            command=lambda c=command, t=text: on_sidebar_click(app, t, c)
        )
        btn.pack(fill="x", pady=2)
        btn.bind("<Enter>", lambda e, b=btn: on_hover_enter(app, b))
        btn.bind("<Leave>", lambda e, b=btn: on_hover_leave(app, b))

        app.sidebar_buttons[text] = btn
    # default active

    set_active_sidebar(app, "Dashboard")


# -----------------------------------
# Hover Effects
# -----------------------------------
def on_hover_enter(app, button):
    if button != app.sidebar_buttons.get(app.active_sidebar):
        button.configure(style="SidebarHover.TButton")


def on_hover_leave(app, button):
    if button != app.sidebar_buttons.get(app.active_sidebar):
        button.configure(style="Sidebar.TButton")



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