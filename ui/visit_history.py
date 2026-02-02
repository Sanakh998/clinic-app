from tkinter import ttk
import datetime
from config.config import PAD_MEDIUM, PAD_SMALL
from ui.visit_cards import load_visits
from utils.scrollable_frame import ScrollableFrame

# ==============================
# VISIT HISTORY (ALL VISITS)
# ==============================

def show_visit_history(app):
    app.clear_content()

    # ---- load once ----
    app.all_visits = app.db.get_all_visits_with_patient()

    app.current_visit_filter = None
    app.filtered_visits = []

    # --- Header ---
    header = ttk.Frame(app.content_frame)
    header.pack(fill="x", pady=(0, PAD_MEDIUM))

    ttk.Label(
        header,
        text="Visit History",
        style="SubTitle.TLabel"
    ).pack(side="left")

    ttk.Label(
        header,
        text=f"(Total: {len(app.filtered_visits) or 0})",
        style="Muted.TLabel"
    ).pack(side="left", padx=PAD_SMALL, pady=(5, 0))

    ttk.Button(
        header,
        text="➕ Quick Visit",
        style="Accent.TButton",
        command=app.open_quick_visit
    ).pack(side="right")

    # --- Filter Bar ---
    filter_bar = ttk.Frame(app.content_frame)
    filter_bar.pack(fill="x", pady=(0, PAD_MEDIUM))

    ttk.Button(
        filter_bar, text="All",
        command=lambda: apply_visit_filter(app, None)
    ).pack(side="left", padx=PAD_SMALL)

    ttk.Button(
        filter_bar, text="Today",
        command=lambda: apply_visit_filter(app, "today")
    ).pack(side="left", padx=PAD_SMALL)

    ttk.Button(
        filter_bar, text="This Week",
        command=lambda: apply_visit_filter(app, "week")
    ).pack(side="left", padx=PAD_SMALL)

    ttk.Button(
        filter_bar, text="This Month",
        command=lambda: apply_visit_filter(app, "month")
    ).pack(side="left", padx=PAD_SMALL)

    # --- Cards Container ---
    container = ScrollableFrame(app.content_frame)
    container.pack(fill="both", expand=True)

    app.visits_container = container

    apply_visit_filter(app, None)


# ==============================
# FILTER LOGIC
# ==============================

def apply_visit_filter(app, filter_type):
    today = datetime.date.today()
    visits = app.all_visits.copy()

    if filter_type == "today":
        visits = [
            v for v in visits
            if datetime.datetime.fromisoformat(v[2]).date() == today
        ]

    elif filter_type == "week":
        start = today - datetime.timedelta(days=7)
        visits = [
            v for v in visits
            if start <= datetime.datetime.fromisoformat(v[2]).date() <= today
        ]

    elif filter_type == "month":
        visits = [
            v for v in visits
            if datetime.datetime.fromisoformat(v[2]).month == today.month
            and datetime.datetime.fromisoformat(v[2]).year == today.year
        ]

    app.filtered_visits = visits

    load_visits(
        app,
        app.visits_container.scrollable_frame,
        visits,
        lambda: apply_visit_filter(app, filter_type),
        show_patient_name=True
    )
