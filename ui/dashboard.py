import tkinter as tk
from tkinter import ttk
from ui.table_factory import create_table
from utils.placeholder_entry import PlaceholderEntry
from utils.scrollable_frame import ScrollableFrame
from config.config import (
    COLOR_ACCENT, COLOR_TEXT_LIGHT, FONT_FAMILY, FONT_SMALL_ITALIC,
    COLOR_PRIMARY, COLOR_SUCCESS, PAD_SMALL, PAD_LARGE, PAD_MEDIUM,
    COLOR_BG, COLOR_SURFACE, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, FONT_HEADER
)
import datetime
from PIL import Image, ImageTk
from utils.resource_path import resource_path


# ==========================================
# DASHBOARD
# ==========================================

def dashboard(app):
    app.clear_content()

    # --- Dashboard Grid ---
    grid = ttk.Frame(app.content_frame)
    grid.pack(fill="x", pady=(0, PAD_MEDIUM))

    for i in range(4):
        grid.columnconfigure(i, weight=1)

    cards = [
        ("assets/icons/users.png", "Total Patients", app.db.get_total_patients_count(), COLOR_PRIMARY, lambda: app.show_patients()),
        ("assets/icons/calendar.png", "Today’s Visits", len(app.db.get_today_visits()), COLOR_PRIMARY, lambda: app.show_today_visits()),
        ("assets/icons/money.png","Earning Today", f"PKR {app.db.get_today_earnings()}", COLOR_SUCCESS, lambda: app.show_earnings()),
        ("assets/icons/today.png","New Patients (Today)", app.db.get_new_patients_today(), COLOR_PRIMARY, lambda: app.show_new_patients("today")),
    ]


    for col, card in enumerate(cards):
        create_dashboard_card(grid, col, *card)

    # =========================
    # SINGLE COLUMN LAYOUT
    # =========================
    
    # Activity Section (Full Width)
    build_recent_activity_section(app.content_frame, app)


def build_recent_activity_section(parent, app):
    section = ttk.Frame(parent)
    section.pack(fill="both", expand=True, pady=PAD_LARGE)

    # --- Header with Integrated Actions ---
    header_frame = ttk.Frame(section)
    header_frame.pack(fill="x", padx=(PAD_MEDIUM, 0), pady=(0, PAD_MEDIUM))

    # Title
    ttk.Label(
        header_frame,
        text="Recent Activity",
        style="SubTitle.TLabel"
    ).pack(side="left", anchor="center")

    # Integrated Quick Actions (Right aligned)
    btn_box = ttk.Frame(header_frame)
    btn_box.pack(side="right")

    ttk.Button(
        btn_box, 
        text="➕ New Patient", 
        style="Accent.TButton", # Highlighted
        command=app.open_patient_form,
        width=15,
        cursor="hand2"
    ).pack(side="left", padx=(0, PAD_SMALL))

    ttk.Button(
        btn_box, 
        text="➕ New Visit", 
        style="Quick.TButton", # Or normal
        command=app.open_quick_visit,
        width=15,
        cursor="hand2"
    ).pack(side="left")

    # --- Activity Table ---
    columns = ("Date", "Patient", "Info", "Complaint")
    
    # Configure columns
    col_config = {
        "Date": {"width": 180, "anchor": "center"},
        "Patient": {"width": 200, "anchor": "w"},
        "Info": {"width": 100, "anchor": "center"}, # Gender/Age
        "Complaint": {"stretch": True, "anchor": "w"}
    }

    tree = create_table(section, columns, col_config, scrollbar=False)

    # Fetch Data
    activity_data = app.db.get_recent_activity(limit=15)

    # Populate Table
    for i, row in enumerate(activity_data):
        tag = "even" if i % 2 == 0 else "odd"
        # row: (visit_date, name, gender, age, complaints, patient_id)
        
        # Format Date
        try:
            dt = row[0]
            if isinstance(dt, str):
                parsed = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                date_str = parsed.strftime("%d %b, %I:%M %p") # 12 Oct, 10:30 AM
            else:
                date_str = str(dt)
        except:
            date_str = str(row[0])

        # Format Info (Sex / Age)
        gender_short = row[2][0] if row[2] else "?"
        info_str = f"{gender_short} / {row[3]}"

        display_row = (date_str, row[1], info_str, row[4])
        
        tree.insert("", "end", values=display_row, tags=(tag,)) # We can alternate tags if we want

    # Bind Double Click -> Open Patient Profile
    def on_row_click(event):
        sel = tree.selection()
        if not sel: return
        item = tree.item(sel)
        
        index = tree.index(sel)
        if index < len(activity_data):
            p_id = activity_data[index][5]
            app.open_patient_profile(p_id)

    tree.bind("<Double-1>", on_row_click)
    tree.bind("<Return>", on_row_click)


# ==========================================
# CARD COMPONENT
# ==========================================

def create_dashboard_card(parent, column, icon_path, title, value, color, on_click=None):

    # Outer wrapper (spacing)
    outer = ttk.Frame(parent, style="Outer.TFrame", padding=1)
    outer.grid(row=0, column=column, padx=PAD_SMALL, sticky="nsew")

    # Main card
    card = tk.Frame(
        outer,
        bg=COLOR_SURFACE,
        bd=1,
        relief="solid"
    )
    card.pack(fill="both", expand=True)

    # Left color strip (🔥 MAZA YAHAN SE AATA HAI)
    strip = tk.Frame(card, bg=color, width=6)
    strip.pack(side="left", fill="y")

    content = tk.Frame(card, bg=COLOR_SURFACE, padx=PAD_LARGE, pady=PAD_LARGE)
    content.pack(side="left", fill="both", expand=True)

    # Load icon safely
    full_path = resource_path(icon_path)
    img = Image.open(full_path).resize((40, 40))
    icon = ImageTk.PhotoImage(img)

    # Prevent garbage collection
    if not hasattr(parent, "dashboard_icons"):
        parent.dashboard_icons = []
    parent.dashboard_icons.append(icon)

    # Icon
    tk.Label(
        content,
        image=icon,
        bg=COLOR_SURFACE
    ).pack(anchor="w")

    # Value (main focus)
    tk.Label(
        content,
        text=value,
        font=(FONT_FAMILY, 22, "bold"),
        fg=COLOR_TEXT_MAIN,
        bg=COLOR_SURFACE
    ).pack(anchor="w", pady=(4, 0))

    # Title (muted)
    tk.Label(
        content,
        text=title,
        font=FONT_SMALL_ITALIC,
        fg=COLOR_TEXT_MUTED,
        bg=COLOR_SURFACE
    ).pack(anchor="w")

    # --------------------
    # Hover + Click Effects
    # --------------------
    def on_enter(e):
        card.config(bg=COLOR_ACCENT)
        content.config(bg=COLOR_ACCENT)
        for w in content.winfo_children():
            w.config(bg=COLOR_ACCENT)
        card.config(cursor="hand2")

    def on_leave(e):
        card.config(bg=COLOR_SURFACE)
        content.config(bg=COLOR_SURFACE)
        for w in content.winfo_children():
            w.config(bg=COLOR_SURFACE)
        card.config(cursor="")

    card.bind("<Enter>", on_enter)
    card.bind("<Leave>", on_leave)

    if on_click:
        card.bind("<Button-1>", lambda e: on_click())
        content.bind("<Button-1>", lambda e: on_click())
        for child in content.winfo_children():
            child.bind("<Button-1>", lambda e: on_click())


def on_tree_double_click(app, tree):
    sel = tree.selection()
    if not sel:
        return
    patient_id = tree.item(sel)["values"][0]
    app.open_patient_profile(patient_id)

