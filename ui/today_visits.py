
from tkinter import ttk
from config.config import PAD_MEDIUM, PAD_SMALL
from ui.visit_cards import load_visits
from utils.scrollable_frame import ScrollableFrame

def show_today_visits(app):
    app.clear_content()
    visits = app.db.get_today_visits()

    header = ttk.Frame(app.content_frame)
    header.pack(fill="x", pady=(0, PAD_MEDIUM))
    
    ttk.Label(header, text="Today’s Visit", style="SubTitle.TLabel").pack(side="left")
    ttk.Label(header, text=f"(Total: {len(visits) or 0})", style="Muted.TLabel").pack(side="left", padx=PAD_SMALL, pady=(5,0))

     #     ttk.Button(header, text="➕ Quick Visit", style="Accent.TButton",
    #         command=lambda: VisitForm(self, self.db, patient_id=0, callback=self.show_today_visits, visit_data=None, allow_patient_select=True)
    #     ).pack(side="right")
    btn_quick_visit = ttk.Button(
        header,
        text="➕ Quick Visit",
        style="Accent.TButton",
        command=lambda: app.open_quick_visit()
    )
    btn_quick_visit.pack(side="right")

     # -- Visits List --


    container = ScrollableFrame(app.content_frame)
    container.pack(fill="both", expand=True)



    def refresh():
        visits = app.db.get_today_visits()
        load_visits(
            app,
            container.scrollable_frame,
            visits,
            refresh,
            show_patient_name=True
        )

    refresh()
