import datetime
from tkinter import ttk
from config.config import (
    PAD_LARGE, PAD_MEDIUM,
    FONT_HEADER, FONT_BODY_BOLD,
    COLOR_TEXT_MUTED, COLOR_SUCCESS
)
from ui.table_factory import create_table

# ==============================
# EARNINGS / REVENUE SCREEN
# ==============================

def show_earnings_report(app):
    app.clear_content()

    today = datetime.date.today()

    # --- Container ---
    container = ttk.Frame(app.content_frame)
    container.pack(fill="both", expand=True, padx=PAD_LARGE, pady=PAD_LARGE)

    # --- Title ---
    ttk.Label(
        container,
        text="Revenue Report",
        font=FONT_HEADER
    ).pack(anchor="w", pady=(0, PAD_MEDIUM))

    # --- Summary Bar ---
    summary = ttk.Frame(container)
    summary.pack(fill="x", pady=(0, PAD_LARGE))

    for i in range(3):
        summary.columnconfigure(i, weight=1)

    def summary_card(parent, col, title, var_name):
        outer = ttk.Frame(parent, padding=2)
        outer.grid(row=0, column=col, padx=PAD_MEDIUM, sticky="nsew")

        card = ttk.Frame(outer, style="Card.TFrame", padding=PAD_MEDIUM)
        card.pack(fill="both", expand=True)

        ttk.Label(
            card,
            text=title,
            style="Muted.TLabel"
        ).pack(anchor="w")

        lbl = ttk.Label(
            card,
            text="PKR 0",
            font=FONT_BODY_BOLD,
            foreground=COLOR_SUCCESS
        )
        lbl.pack(anchor="w", pady=(5, 0))

        setattr(app, var_name, lbl)

    summary_card(summary, 0, "Today", "lbl_today")
    summary_card(summary, 1, "Selected Range", "lbl_range")
    summary_card(summary, 2, "All Time", "lbl_all")

    # --- Filter Bar ---
    filter_bar = ttk.Frame(container)
    filter_bar.pack(fill="x", pady=(0, PAD_MEDIUM))

    ttk.Button(
        filter_bar, text="Today",
        command=lambda: apply_revenue_filter(app, "today")
    ).pack(side="left", padx=5)

    ttk.Button(
        filter_bar, text="This Week",
        command=lambda: apply_revenue_filter(app, "week")
    ).pack(side="left", padx=5)

    ttk.Button(
        filter_bar, text="This Month",
        command=lambda: apply_revenue_filter(app, "month")
    ).pack(side="left", padx=5)

    # --- Date Range (manual) ---
    range_bar = ttk.Frame(filter_bar)
    range_bar.pack(side="right", fill="x", pady=(0, PAD_MEDIUM))

    ttk.Label(range_bar, text="From:").pack(side="left")
    app.rev_from = ttk.Entry(range_bar, width=12)
    app.rev_from.pack(side="left", padx=5)

    ttk.Label(range_bar, text="To:").pack(side="left")
    app.rev_to = ttk.Entry(range_bar, width=12)
    app.rev_to.pack(side="left", padx=5)

    ttk.Button(
        range_bar, text="Apply",
        command=lambda: apply_revenue_filter(app, "range")
    ).pack(side="left", padx=5)

    ttk.Label(
        range_bar,
        text="(YYYY-MM-DD)",
        foreground=COLOR_TEXT_MUTED
    ).pack(side="left", padx=5)

    # --- Table ---
    columns = ("Date", "Patient", "Fees")

    app.rev_tree = create_table(
        container,
        columns,
        {
            "Date": {"width": 250, "anchor": "center"},
            "Patient": {"stretch": True},
            "Fees": {"width": 250, "anchor": "center"}
        }
    )

    apply_revenue_filter(app, "today")


# ==============================
# FILTER LOGIC
# ==============================

def apply_revenue_filter(app, mode):
    today = datetime.date.today()

    if mode == "today":
        start = end = today

    elif mode == "week":
        start = today - datetime.timedelta(days=7)
        end = today

    elif mode == "month":
        start = today.replace(day=1)
        end = today

    elif mode == "range":
        try:
            start = datetime.date.fromisoformat(app.rev_from.get())
            end = datetime.date.fromisoformat(app.rev_to.get())
        except ValueError:
            return

    else:
        return

    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")

    # --- summary ---
    today_total = app.db.get_today_earnings()
    range_total = app.db.get_earnings_by_date_range(start_str, end_str)
    all_total = app.db.get_total_earnings()

    app.lbl_today.config(text=f"PKR {today_total}")
    app.lbl_range.config(text=f"PKR {range_total}")
    app.lbl_all.config(text=f"PKR {all_total}")

    # --- table ---
    load_revenue_table(app, start_str, end_str)


def load_revenue_table(app, start_date, end_date):
    app.rev_tree.delete(*app.rev_tree.get_children())

    visits = app.db.get_visits_by_date_range(start_date, end_date)

    for i, v in enumerate(visits):
        visit_date = v[2][:16]
        patient_name = v[7]
        fees = v[5] or 0

        tag = "even" if i % 2 == 0 else "odd"

        app.rev_tree.insert(
            "",
            "end",
            values=(visit_date, patient_name, fees),
            tags=(tag,)
        )
