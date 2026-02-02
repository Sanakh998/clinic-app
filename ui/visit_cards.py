import tkinter as tk
from tkinter import ttk, messagebox
from forms.visit_form import VisitForm
from config.config import (
    FONT_HEADER, FONT_SMALL_ITALIC, PAD_SMALL, PAD_MEDIUM, COLOR_TEXT_MUTED,
    FONT_BODY, FONT_BODY_BOLD, COLOR_SUCCESS
)

def load_visits(app, parent, visits, refresh_callback, show_patient_name=False):
    for w in parent.winfo_children():
        w.destroy()

    if not visits and not show_patient_name:
        ttk.Label(
            parent,
            text="No visits recorded for this patient.",
            foreground=COLOR_TEXT_MUTED,
            font=FONT_HEADER,
        ).pack(pady=50, anchor="center")
        return

    if not visits and show_patient_name:
        ttk.Label(
            parent,
            text="No visits recorded for today.",
            foreground=COLOR_TEXT_MUTED,
            font=FONT_HEADER,
        ).pack(pady=50, anchor="center")
        return

    # 🔹 GRID CONTAINER (NEW)
    grid = ttk.Frame(parent)
    grid.pack(fill="both", expand=True)

    COLUMNS = 3  # 👈 2 cards per row

    for c in range(COLUMNS):
        grid.columnconfigure(c, weight=1)

    for index, visit in enumerate(visits):
        row = index // COLUMNS
        col = index % COLUMNS

        card = create_visit_card(
            app,
            grid,
            visit,
            refresh_callback,
            show_patient_name
        )

        card.grid(
            row=row,
            column=col,
            sticky="nsew",
            padx=PAD_SMALL,
            pady=PAD_SMALL
        )


def create_visit_card(app, parent, visit, refresh_callback, show_patient_name):
    card = ttk.Frame(parent, style="Card.TFrame", padding=(PAD_MEDIUM, PAD_SMALL))

    # =========================
    # HEADER
    # =========================
    header = ttk.Frame(card)
    header.pack(fill="x", pady=(0, PAD_SMALL))

    title_text = visit[7] if show_patient_name else f"📅 {visit[2]}"
    ttk.Label(
        header,
        text=title_text,
        font=FONT_BODY_BOLD
    ).pack(side="left", anchor="w")

    btns = ttk.Frame(header)
    btns.pack(side="right")

    ttk.Button(
        btns,
        text="Edit",
        width=6,
        command=lambda: VisitForm(
            app,
            app.db,
            visit[1],
            refresh_callback,
            visit
        )
    ).pack(side="left", padx=(PAD_MEDIUM, PAD_SMALL))

    ttk.Button(
        btns,
        text="Delete",
        width=6,
        style="Danger.TButton",
        command=lambda: delete_visit(app, visit[0], refresh_callback)
    ).pack(side="left")

    # =========================
    # MAIN CONTENT
    # =========================
    content = ttk.Frame(card)
    content.pack(fill="x")

    def row(label, value, bold=False, color=None):
        r = ttk.Frame(content)
        r.pack(fill="x", pady=2)

        ttk.Label(
            r,
            text=label,
            width=10,
            foreground=COLOR_TEXT_MUTED,
            anchor="nw"
        ).pack(side="left")

        ttk.Label(
            r,
            text=value,
            wraplength=700,
            justify="left",
            font=FONT_BODY_BOLD if bold else FONT_BODY,
            foreground=color
        ).pack(side="left", fill="x", expand=True)

    row("History:", visit[3])
    row("Medicine:", visit[4])
    row("Fees:", f"PKR {visit[5]}", bold=True, color=COLOR_SUCCESS)

    # =========================
    # REMARKS
    # =========================
    if visit[6]:
        ttk.Separator(card).pack(fill="x", pady=(PAD_SMALL, PAD_SMALL))

        ttk.Label(
            card,
            text="Remarks: ",
            foreground=COLOR_TEXT_MUTED,
            font=FONT_SMALL_ITALIC
        ).pack(side="left")

        ttk.Label(
            card,
            text=visit[6],
            wraplength=750,
            foreground=COLOR_TEXT_MUTED,
            font=FONT_SMALL_ITALIC
        ).pack(side="left")

    return card  # 👈 IMPORTANT


def delete_visit(app, visit_id, refresh_callback):
    if messagebox.askyesno("Confirm", "Delete this visit?"):
        app.db.delete_visit(visit_id)
        refresh_callback()









# import tkinter as tk
# from tkinter import ttk, messagebox
# from forms.visit_form import VisitForm
# from config.config import (
#     FONT_HEADER, PAD_SMALL, PAD_MEDIUM, COLOR_TEXT_MUTED,
#     FONT_BODY, FONT_BODY_BOLD, COLOR_SUCCESS
# )

# def load_visits(app, parent, visits, refresh_callback, show_patient_name=False):
#     for w in parent.winfo_children():
#         w.destroy()

#     if not visits and not show_patient_name:
#         ttk.Label(
#             parent,
#             text="No visits recorded for this patient.",
#             foreground=COLOR_TEXT_MUTED,
#             font=FONT_HEADER,
#         ).pack(pady=50, anchor="center")
#         return
#     if not visits and show_patient_name:
#         ttk.Label(
#             parent,
#             text="No visits recorded for today.",
#             foreground=COLOR_TEXT_MUTED,
#             font=FONT_HEADER,
#         ).pack(pady=50, anchor="center")
#         return

#     for visit in visits:
#         create_visit_card(
#             app,
#             parent,
#             visit,
#             refresh_callback,
#             show_patient_name
#         )

# def create_visit_card(app, parent, visit, refresh_callback, show_patient_name):
#     card = ttk.Frame(parent, style="Card.TFrame", padding=(PAD_MEDIUM, PAD_SMALL))
#     card.pack(fill="x", pady=(0, PAD_SMALL))

#     # =========================
#     # HEADER
#     # =========================
#     header = ttk.Frame(card)
#     header.pack(fill="x", pady=(0, PAD_SMALL))

#     title_text = visit[7] if show_patient_name else f"📅 {visit[2]}"
#     ttk.Label(
#         header,
#         text=title_text,
#         font=FONT_BODY_BOLD
#     ).pack(side="left", anchor="w")

#     btns = ttk.Frame(header)
#     btns.pack(side="right")

#     ttk.Button(
#         btns,
#         text="Edit",
#         width=6,
#         command=lambda: VisitForm(
#             app,
#             app.db,
#             visit[1],
#             refresh_callback,
#             visit
#         )
#     ).pack(side="left", padx=PAD_SMALL)

#     ttk.Button(
#         btns,
#         text="Delete",
#         width=6,
#         style="Danger.TButton",
#         command=lambda: delete_visit(app, visit[0], refresh_callback)
#     ).pack(side="left")

#     # =========================
#     # MAIN CONTENT
#     # =========================
#     content = ttk.Frame(card)
#     content.pack(fill="x")

#     def row(label, value, bold=False, color=None):
#         r = ttk.Frame(content)
#         r.pack(fill="x", pady=2)

#         ttk.Label(
#             r,
#             text=label,
#             width=12,
#             foreground=COLOR_TEXT_MUTED,
#             anchor="nw"
#         ).pack(side="left")

#         ttk.Label(
#             r,
#             text=value,
#             wraplength=700,
#             justify="left",
#             font=FONT_BODY_BOLD if bold else FONT_BODY,
#             foreground=color
#         ).pack(side="left", fill="x", expand=True)

#     row("History:", visit[3])
#     row("Medicine:", visit[4])
#     row("Fees:", f"PKR {visit[5]}", bold=True, color=COLOR_SUCCESS)

#     # =========================
#     # REMARKS (OPTIONAL)
#     # =========================
#     if visit[6]:  # 👈 REMARKS
#         sep = ttk.Separator(card)
#         sep.pack(fill="x", pady=(PAD_SMALL, PAD_SMALL))

#         ttk.Label(
#             card,
#             text="Remarks:",
#             foreground=COLOR_TEXT_MUTED
#         ).pack(side="left")

#         ttk.Label(
#             card,
#             text=visit[6],
#             wraplength=750,
#             justify="left",
#             foreground=COLOR_TEXT_MUTED
#         ).pack(side="left", pady=(2, 0))

# def delete_visit(app, visit_id, refresh_callback):
#     if messagebox.askyesno("Confirm", "Delete this visit?"):
#         app.db.delete_visit(visit_id)
#         refresh_callback()
