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
        ("👥", "Total Patients", app.db.get_total_patients_count(), COLOR_PRIMARY, lambda: app.show_patients()),
        ("📅", "Today’s Visits", len(app.db.get_today_visits()), COLOR_PRIMARY, lambda: app.show_today_visits()),
        ("💰", "Earnings Today", f"PKR {app.db.get_today_earnings()}", COLOR_SUCCESS, lambda: app.show_earnings()),
        ("🆕", "New Patients (Today)", app.db.get_new_patients_today(), COLOR_PRIMARY, lambda: app.show_new_patients("today")),
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
        width=15
    ).pack(side="left", padx=(0, PAD_SMALL))

    ttk.Button(
        btn_box, 
        text="🩺 New Visit", 
        style="Accented.TButton", # Or normal
        command=app.open_quick_visit,
        width=15
    ).pack(side="left")

    # --- Activity Table ---
    columns = ("Date", "Patient", "Info", "Complaint")
    
    # Configure columns
    col_config = {
        "Date": {"width": 150, "anchor": "w"},
        "Patient": {"width": 200, "anchor": "w"},
        "Info": {"width": 100, "anchor": "center"}, # Gender/Age
        "Complaint": {"stretch": True, "anchor": "w"}
    }

    tree = create_table(section, columns, col_config, scrollbar=False)

    # Fetch Data
    activity_data = app.db.get_recent_activity(limit=15)

    # Populate Table
    for row in activity_data:
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
        
        tree.insert("", "end", values=display_row, tags=("even",)) # We can alternate tags if we want

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

def create_dashboard_card(parent, column, icon, title, value, color, on_click=None):
    # outer = ttk.Frame(parent, padding=2)
    # outer.grid(row=0, column=column, padx=PAD_SMALL, sticky="nsew")
    outer = ttk.Frame(parent, padding=(2, 2), style="Outer.TFrame")
    outer.grid(row=0, column=column, padx=PAD_SMALL, sticky="nsew")

    card = ttk.Frame(outer, style="Card.TFrame", padding=PAD_LARGE)
    card.pack(fill="both", expand=True)

    tk.Label(card, text=icon, font=(FONT_FAMILY, 28),
             fg=color, bg=COLOR_SURFACE).pack(anchor="w")

    tk.Label(card, text=value, font=(FONT_FAMILY, 22, "bold"),
             fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE).pack(anchor="w")

    tk.Label(card, text=title, font=FONT_SMALL_ITALIC,
             fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE).pack(anchor="w")
    
    if on_click:
        card.bind("<Button-1>", lambda e: on_click())
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e: on_click())



def on_tree_double_click(app, tree):
    sel = tree.selection()
    if not sel:
        return
    patient_id = tree.item(sel)["values"][0]
    app.open_patient_profile(patient_id)

