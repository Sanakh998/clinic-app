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
    # QUICK ACTIONS BAR
    # =========================
    quick_bar = ttk.Frame(app.content_frame, style="Card.TFrame", padding=PAD_SMALL)
    quick_bar.pack(fill="x", pady=(PAD_SMALL, 0))

    # Buttons container
    actions_box = ttk.Frame(quick_bar)
    actions_box.pack()

    # --- Create New Patient ---
    btn_new_patient = ttk.Button(
        actions_box,
        text="➕ Create New Patient",
        style="Quick.TButton",
        command=app.open_patient_form
    )
    btn_new_patient.pack(side="left", padx=PAD_MEDIUM)

    # --- Add Quick Visit ---
    btn_quick_visit = ttk.Button(
        actions_box,
        text="🩺 Add Quick Visit",
        style="Quick.TButton",
        command=app.open_quick_visit
    )
    btn_quick_visit.pack(side="left", padx=PAD_MEDIUM)


    build_recent_patients_section(app)


# ==========================================
# RECENT PATIENTS + SEARCH
# ==========================================

def build_recent_patients_section(app):
    section = ttk.Frame(app.content_frame)
    section.pack(fill="both", expand=True, pady=(PAD_LARGE, 0))

    header = ttk.Frame(section)
    header.pack(fill="x", padx=(PAD_MEDIUM, 0))

    # Title
    ttk.Label(
        header,
        text="Recently Interacted Patients",
        style="SubTitle.TLabel"
    ).pack(side="left", anchor="w", pady=(0, PAD_SMALL), padx=(PAD_MEDIUM, 0))

    # 🔹 SEARCH BAR (NEW)
    search_var = tk.StringVar()

    search_entry = PlaceholderEntry(
        header,
        "🔍 Search Patient by Name, ID or Phone...",
        textvariable=search_var,
        font=FONT_HEADER
    )
    search_entry.pack(side="left", fill="x", pady=(0, PAD_SMALL), padx=(PAD_MEDIUM, 0), expand=True)

    # # --- Scrollable table ---
    # scroll_container = ScrollableFrame(section)
    # scroll_container.pack(fill="both", expand=True)

    # # 🔹 IMPORTANT FIX
    # scroll_container.scrollable_frame.pack(fill="both", expand=True)

    columns = ("Patient ID", "Name", "Phone", "Last Visit")

    tree = create_table(
        section,
        columns,
        {
            "Patient ID": {"width": 150, "anchor": "center"},
            "Name": {"stretch": True},
            "Phone": {"width": 250},
            "Last Visit": {"width": 250, "anchor": "center"}
        }
    )

    # Load data once
    all_patients = app.db.get_recent_interacted_patients(limit=50)

    def load_rows(data):
        tree.delete(*tree.get_children())
        for i, row in enumerate(data):
            tag = "even" if i % 2 == 0 else "odd"
            tree.insert("", "end", values=row, tags=(tag,))

    load_rows(all_patients)

    # 🔹 SEARCH LOGIC
    def on_search(*_):
        q = search_var.get().lower().strip()
        if not q:
            load_rows(all_patients)
            return

        filtered = [
            r for r in all_patients
            if q in str(r[0]).lower()
            or q in r[1].lower()
            or q in r[2].lower()
        ]
        load_rows(filtered)

    search_var.trace_add("write", on_search)

    tree.bind("<Double-1>", lambda e: on_tree_double_click(app, tree))
    tree.bind("<Return>", lambda e: on_tree_double_click(app, tree))


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




# import tkinter as tk
# from tkinter import ttk, messagebox
# from utils.scrollable_frame import ScrollableFrame
# from forms.patient_form import PatientForm
# from forms.visit_form import VisitForm
# from config.config import (
#     COLOR_ACCENT, COLOR_TEXT_LIGHT, FONT_FAMILY, FONT_SMALL_ITALIC, COLOR_PRIMARY, COLOR_SUCCESS, PAD_SMALL,
#     PAD_LARGE, PAD_MEDIUM, COLOR_BG, COLOR_SURFACE, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED
# )

# # ==========================================
# # DASHBOARD 
# # ==========================================

# def dashboard(app):
#     app.clear_content()

#     # --- Dashboard Grid ---
#     grid = ttk.Frame(app.content_frame)
#     grid.pack(fill="x", pady=(0, PAD_LARGE))

#     for i in range(4):
#         grid.columnconfigure(i, weight=1)

#     # Fetch stats
#     total_patients = app.db.get_total_patients_count()
#     today_visits = len(app.db.get_today_visits())
#     today_earnings = app.db.get_today_earnings()
#     new_patients = app.db.get_new_patients_today() 

#     cards = [
#         ("👥", "Total Patients", total_patients, COLOR_PRIMARY),
#         ("📅", "Today’s Visits", today_visits, COLOR_PRIMARY),
#         ("💰", "Earnings Today", f"PKR {today_earnings}", COLOR_SUCCESS),
#         ("🆕", "New Patients (Today)", new_patients, COLOR_PRIMARY),
#     ]

#     for col, card in enumerate(cards):
#         create_dashboard_card(grid, col, *card)

#     # =========================
#     # QUICK ACTIONS BAR
#     # =========================
#     quick_bar = ttk.Frame(app.content_frame, style="Card.TFrame", padding=PAD_LARGE)
#     quick_bar.pack(fill="x", pady=(PAD_LARGE, 0))

#     # Buttons container
#     actions_box = ttk.Frame(quick_bar)
#     actions_box.pack()

#     # --- Create New Patient ---
#     btn_new_patient = ttk.Button(
#         actions_box,
#         text="➕ Create New Patient",
#         style="Quick.TButton",
#         command=app.open_patient_form
#     )
#     btn_new_patient.pack(side="left", padx=PAD_MEDIUM)

#     # --- Add Quick Visit ---
#     btn_quick_visit = ttk.Button(
#         actions_box,
#         text="🩺 Add Quick Visit",
#         style="Quick.TButton",
#         command=app.open_quick_visit
#     )
#     btn_quick_visit.pack(side="left", padx=PAD_MEDIUM)

#     build_recent_patients_section(app)

#     # =========================
#     # RECENTLY INTERACTED PATIENTS
#     # =========================
# def build_recent_patients_section(app):
#     section = ttk.Frame(app.content_frame)
#     section.pack(fill="both", expand=True, pady=(PAD_LARGE, 0))

#     ttk.Label(
#         section,
#         text="Recently Interacted Patients",
#         style="SubTitle.TLabel"
#     ).pack(anchor="w", pady=(0, PAD_SMALL))

#     # --- Scrollable table ---
#     scroll_container = ScrollableFrame(section)
#     scroll_container.pack(fill="both", expand=True)

#     columns = ("id", "name", "phone", "last_visit") # , "actions"

#     tree = ttk.Treeview(
#         scroll_container.scrollable_frame,
#         columns=columns,
#         show="headings",
#         style="Dashboard.Treeview",
#         selectmode="browse",
#         height=10  # visible rows
#     )

#     # Define headings
#     for col, text in zip(columns, ["Patient ID", "Name", "Phone", "Last Visit"]):
#         tree.heading(col, text=text)

    

#     # Column widths
#     tree.column("id", width=80, anchor="center")
#     tree.column("name", width=200)
#     tree.column("phone", width=140)
#     tree.column("last_visit", width=150)
#     # tree.column("actions", width=160, anchor="center")

#     tree.pack(fill="both", expand=True)

#     # Load recent patients
#     recent_patients = app.db.get_recent_interacted_patients(limit=20)  # max 20

#     for index, row in enumerate(recent_patients):
#         tag = "even" if index % 2 == 0 else "odd"
#         tree.insert(
#             "",
#             "end",
#             values=(
#                 row[0],
#                 row[1],
#                 row[2],
#                 row[3] if row[3] else "—"
#             ),
#             tags=(tag,)
#         )

#     tree.tag_configure("even", background=COLOR_SURFACE)
#     tree.tag_configure("odd", background=COLOR_BG)
#     tree.tag_configure("hover", background=COLOR_ACCENT)
#     tree.tag_configure("selected", background=COLOR_PRIMARY, foreground=COLOR_TEXT_LIGHT)
#     tree.bind("<Double-1>", lambda e: on_tree_double_click(app, tree))

# # ==========================================
# # DASHBOARD CARD COMPONENT
# # ==========================================
# def create_dashboard_card(parent, column, icon, title, value, color):
#     # Shadow wrapper
#     outer = ttk.Frame(parent, padding=(2, 2), style="Outer.TFrame")
#     outer.grid(row=0, column=column, padx=PAD_SMALL, sticky="nsew")

#     # Card
#     card = ttk.Frame(
#         outer,
#         style="Card.TFrame",
#         padding=PAD_LARGE
#     )
#     card.pack(fill="both", expand=True)

#     # Icon
#     tk.Label(
#         card,
#         text=icon,
#         font=(FONT_FAMILY, 28),
#         fg=color,
#         bg=COLOR_SURFACE
#     ).pack(anchor="w")

#     # Value
#     tk.Label(
#         card,
#         text=value,
#         font=(FONT_FAMILY, 22, "bold"),
#         fg=COLOR_TEXT_MAIN,
#         bg=COLOR_SURFACE
#     ).pack(anchor="w", pady=(PAD_SMALL, 0))

#     # Title
#     tk.Label(
#         card,
#         text=title,
#         font=FONT_SMALL_ITALIC,
#         fg=COLOR_TEXT_MUTED,
#         bg=COLOR_SURFACE
#     ).pack(anchor="w")

# def on_tree_double_click(app, tree):
#     selected = tree.selection()
#     if not selected:
#         return
#     item = tree.item(selected)
#     patient_id = item['values'][0]  # assuming first column is ID
#     app.open_patient_profile(patient_id)
