import tkinter as tk
from tkinter import ttk
from config.config import (
    PAD_LARGE, PAD_MEDIUM, PAD_SMALL, FONT_HEADER, FONT_BODY_BOLD, COLOR_TEXT_MUTED
)
from utils.scrollable_frame import ScrollableFrame
from ui.visit_cards import load_visits

# ==========================================
# PATIENT PROFILE SCREEN
# ==========================================
def show_patient_details(app, patient_id):
    app.clear_content()
    patient = app.db.get_patient_by_id(patient_id)
    visits_count = len(app.db.get_visits(patient_id))
    if not patient: return

    # -- Top Actions Row --
    top_bar = ttk.Frame(app.content_frame)
    top_bar.pack(fill="x", pady=(0, PAD_MEDIUM))
    
    ttk.Button(top_bar, text="← Back to List", command=app.show_dashboard).pack(side="left")
    ttk.Label(top_bar, text=f"Patient ID: #{patient[0]}", style="Muted.TLabel").pack(side="right", pady=5)

    # -- Info Card --
    info_frame = ttk.LabelFrame(app.content_frame, text="Patient Profile", padding=PAD_LARGE)
    info_frame.pack(fill="x", pady=(0, PAD_LARGE))
    
    # Grid Layout for details
    grid_frame = ttk.Frame(info_frame)
    grid_frame.pack(fill="x")
    
    # Helper for key-value pairs
    def add_detail(row, col, label, value, colspan=1):
        ttk.Label(grid_frame, text=label, font=FONT_HEADER, foreground=COLOR_TEXT_MUTED).grid(row=row, column=col, sticky="w", padx=(0, PAD_MEDIUM), pady=PAD_SMALL)
        ttk.Label(grid_frame, text=value, font=FONT_BODY_BOLD).grid(row=row, column=col+1, sticky="w", padx=(0, PAD_LARGE), columnspan=colspan, pady=PAD_SMALL)

    add_detail(0, 0, "Name:", patient[1])
    add_detail(0, 2, "Age:", f"{patient[3]} Yrs")
    add_detail(0, 4, "Gender:", patient[4])
    
    add_detail(1, 0, "Phone:", patient[2])
    add_detail(1, 2, "Address:", patient[5], colspan=3)
    
    if patient[6]:
        add_detail(2, 0, "Medical Notes:", patient[6], colspan=5)

    # -- Profile Actions --
    btn_frame = ttk.Frame(info_frame)
    btn_frame.pack(fill="x", pady=(PAD_LARGE, 0))
    
    ttk.Button(btn_frame, text="✏️ Edit Profile", 
                command=lambda: app.edit_patient(lambda: app.open_patient_profile(patient_id), patient)).pack(side="left", padx=(0, PAD_SMALL))
    
    ttk.Button(btn_frame, text="⎙ Print Report", 
                command=lambda: app.print_profile(patient)).pack(side="left", padx=PAD_SMALL)
    
    ttk.Button(btn_frame, text="✖️ Delete Profile", style="Danger.TButton",
                command=lambda: app.delete_patient_confirm(patient[0])).pack(side="left", padx=PAD_SMALL)

    ttk.Button(btn_frame, text="➕ Add New Visit", style="Accent.TButton",
                command=lambda: app.add_new_visit(patient_id, lambda: refresh())).pack(side="right")

    # -- History Section --
    title_row = ttk.Frame(app.content_frame)
    title_row.pack(fill="x", pady=(PAD_MEDIUM, PAD_SMALL))

    history_lbl = ttk.Label(
        title_row,
        text="Visit History",
        style="SubTitle.TLabel"
    )
    history_lbl.pack(side="left")

    count_lbl = ttk.Label(
        title_row,
        text=f"(Total: {visits_count})",   # 👈 COUNT HERE
        style="Muted.TLabel"
    )
    count_lbl.pack(side="left", padx=PAD_SMALL)

    
    container = ScrollableFrame(app.content_frame)
    container.pack(fill="both", expand=True)
    
    def refresh():
        visits = app.db.get_visits(patient_id)
        load_visits(app, container.scrollable_frame, visits, refresh)
        count_lbl.config(text=f"(Total: {len(visits)})")

    refresh()

