import tkinter as tk
from tkinter import ttk
from ui.table_factory import create_table
from utils.placeholder_entry import PlaceholderEntry
from config.config import (
    PAD_SMALL, PAD_MEDIUM, PAD_LARGE,
    FONT_HEADER
)
import datetime

# ==============================
# PATIENTS LIST SCREEN
# ==============================

def show_patients_list(app, filter_type=None):
    app.clear_content()

    # ---- state ----
    app.current_filter = filter_type
    app.current_sort = None
    app.current_sort_order = "asc"
    app.filtered_patients = []

    # ---- load once from DB ----
    app.all_patients = app.db.get_all_patients()
    app.visits_count_map = app.db.get_visits_count_map()


    # --- Action Bar ---
    action_bar = ttk.Frame(app.content_frame)
    action_bar.pack(fill="x", pady=(0, PAD_LARGE))

    app.search_var = tk.StringVar()

    entry_search = PlaceholderEntry(
        action_bar,
        "🔍 Search Patient by Name, ID or Phone...",
        textvariable=app.search_var,
        width=70,
        font=FONT_HEADER
    )
    entry_search.pack(side="left", padx=(0, PAD_MEDIUM))
    entry_search.bind("<KeyRelease>", lambda e: apply_search(app))
    entry_search.bind("<Return>", lambda e: apply_search(app))

    # Right buttons
    right_actions = ttk.Frame(action_bar)
    right_actions.pack(side="right")

    ttk.Button(
        right_actions,
        text="➕ New Patient",
        style="Accent.TButton",
        command=app.open_patient_form
    ).pack(side="left", padx=PAD_SMALL)

    # --- Filter Bar ---
    filter_bar = ttk.Frame(app.content_frame)
    filter_bar.pack(fill="x", pady=(0, PAD_MEDIUM))

    ttk.Label(filter_bar, text="Filter:").pack(side="left")

    ttk.Button(
        filter_bar, text="All",
        command=lambda: set_filter(app, None)
    ).pack(side="left", padx=PAD_SMALL)

    ttk.Button(
        filter_bar, text="New Today",
        command=lambda: set_filter(app, "today")
    ).pack(side="left", padx=PAD_SMALL)

    ttk.Button(
        filter_bar, text="This Week",
        command=lambda: set_filter(app, "week")
    ).pack(side="left", padx=PAD_SMALL)

    ttk.Button(
        filter_bar, text="This Month",
        command=lambda: set_filter(app, "month")
    ).pack(side="left", padx=PAD_SMALL)

    # --- Patients Table ---
    columns = (
            "ID",
            "Name",
            "Phone",
            "Age",
            "Gender",
            "Address",
            "Reg Date",
            "Visits"
        )

    app.tree = create_table(
        app.content_frame,
        columns,
        {
            "ID": {"width": 80, "anchor": "center"},
            "Name": {"stretch": True},
            "Phone": {"width": 160},
            "Age": {"width": 80, "anchor": "center"},
            "Gender": {"width": 100},
            "Address": {"width": 150},
            "Reg Date": {"width": 150, "anchor": "center"},
            "Visits": {"width": 80, "anchor": "center"}
        }
    )
    for col in columns:
        app.tree.heading(
            col,
            command=lambda c=col: sort_by_column(app, c)
        )

    app.tree.bind("<Double-1>", lambda e: on_patient_select(app))
    app.tree.bind("<Return>", lambda e: on_patient_select(app))

    apply_filters(app)


# ==============================
# FILTER + SORT LOGIC
# ==============================

def set_filter(app, filter_type):
    app.current_filter = filter_type
    apply_filters(app)


def apply_filters(app):
    today = datetime.date.today()
    data = app.all_patients.copy()

    if app.current_filter == "today":
        data = [
            p for p in data
            if datetime.datetime.fromisoformat(p[7]).date() == today
        ]

    elif app.current_filter == "week":
        start = today - datetime.timedelta(days=7)
        data = [
            p for p in data
            if start <= datetime.datetime.fromisoformat(p[7]).date() <= today
        ]

    elif app.current_filter == "month":
        data = [
            p for p in data
            if datetime.datetime.fromisoformat(p[7]).month == today.month
            and datetime.datetime.fromisoformat(p[7]).year == today.year
        ]

    # store filtered base
    app.filtered_patients = data
    load_patients(app, data)

def apply_search(app):
    q = app.search_var.get().strip().lower()

    if len(q) < 2:
        load_patients(app, app.filtered_patients)
        return

    data = [
        p for p in app.filtered_patients
        if q in str(p[0]).lower()
        or q in p[1].lower()
        or (p[2] and q in p[2].lower())
    ]

    load_patients(app, data)



def sort_by_column(app, col):
    idx_map = {
        "ID": 0,
        "Name": 1,
        "Phone": 2,
        "Age": 3,
        "Gender": 4,
        "Address": 5,
        "Reg Date": 7,
        "Visits": None
    }

    reverse = app.current_sort == col and app.current_sort_order == "asc"
    idx = idx_map[col]

    data = app.filtered_patients.copy()

    if col == "Visits":
        data.sort(
            key=lambda p: app.visits_count_map.get(p[0], 0),
            reverse=reverse
        )
    else:
        data.sort(key=lambda p: p[idx], reverse=reverse)

    app.current_sort = col
    app.current_sort_order = "desc" if reverse else "asc"
    app.filtered_patients = data

    load_patients(app, data)


# ==============================
# TABLE HELPERS
# ==============================

def load_patients(app, patients):
    app.tree.delete(*app.tree.get_children())

    for i, p in enumerate(patients):
        created = datetime.datetime.fromisoformat(p[7]).strftime("%d %b %Y")
        visits = app.visits_count_map.get(p[0], 0)

        tag = "even" if i % 2 == 0 else "odd"

        app.tree.insert(
            "",
            "end",
            values=(
                p[0],        # ID
                p[1],        # Name
                p[2],        # Phone
                p[3],        # Age
                p[4],        # Gender
                p[5],        # Address
                created,     # Reg Date
                visits       # Total Visits
            ),
            tags=(tag,)
        )


def on_patient_select(app):
    sel = app.tree.selection()
    if not sel:
        return

    patient_id = app.tree.item(sel)["values"][0]
    app.open_patient_profile(patient_id)

