import tkinter as tk
from tkinter import ttk, messagebox, filedialog
try:
    import sv_ttk
    SV_TTK_AVAILABLE = True
except ImportError:
    SV_TTK_AVAILABLE = False
import datetime
from database.database import DatabaseManager
from reports.report_generator import ReportGenerator
from forms.patient_form import PatientForm
from forms.visit_form import VisitForm
from ui.styles import setup_styles
from ui.sidebar import setup_sidebar
from config.config import *


class MainApp(tk.Tk):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.title(f"{APP_TITLE} v{APP_VERSION}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        
        # =========================
        # THEME & STYLING SETUP
        # =========================
        if SV_TTK_AVAILABLE:
            sv_ttk.set_theme("light")
        self.configure(background=COLOR_BG)
        
        self.style = ttk.Style()
        setup_styles(self.style)

        # Database Init
        self.db = DatabaseManager(DB_NAME)
        
        # Build UI
        self.setup_ui()
        self.show_dashboard()

    def setup_ui(self):
        # --- Header Section ---
        self.header_frame = ttk.Frame(self, padding=(PAD_LARGE, PAD_MEDIUM))
        self.header_frame.pack(fill="x")

        # --- Main Container ---
        self.main_frame = ttk.Frame(self, padding=PAD_MEDIUM)
        self.main_frame.pack(fill="both", expand=True)

        # --- Sidebar Container ---
        setup_sidebar(self)


        # Clinic Info
        lbl_clinic = tk.Label(
            self.header_frame,
            text=CLINIC_NAME,
            font=FONT_TITLE_MAIN,
            fg=COLOR_PRIMARY,
            bg=COLOR_BG
        )
        lbl_clinic.pack(side="left", anchor="w")

        lbl_doctor = tk.Label(
            self.header_frame,
            text=DOCTOR_NAME,
            font=(FONT_FAMILY, 14, "italic"),
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_BG
        )
        lbl_doctor.pack(side="right", anchor="e")

        # --- Main Content Area ---
        self.content_frame = ttk.Frame(self.main_frame, padding=PAD_MEDIUM)
        self.content_frame.pack(fill="both", expand=True)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()


    # --- Logic Methods (Kept largely the same, just utilizing new variables) ---
    def show_patients(self):
        from ui.patients_list import show_patients_list
        show_patients_list(self)

    def show_today_visits(self):
        from ui.today_visits import show_today_visits
        show_today_visits(self)

    def show_visit_history(self):
        from ui.visit_history import show_visit_history
        show_visit_history(self)

    def open_patient_form(self):
        from forms.patient_form import PatientForm
        PatientForm(self, self.db, self.show_patients)

    def open_quick_visit(self):
        from forms.visit_form import VisitForm
        VisitForm(self, self.db, 0, self.show_today_visits, None, True)

    def open_patient_profile(self, patient_id):
        from ui.patient_profile import show_patient_details
        show_patient_details(self, patient_id)

    def show_dashboard(self):
        from ui.dashboard import dashboard
        dashboard(self)

    def open_user_management(self):
        from ui.user_management import UserManagementWindow
        UserManagementWindow(self, self.current_user)

    def edit_patient(self, cb, patient):
        PatientForm(self, self.db, cb, patient_data=patient)

    def add_new_visit(self, p_id, cb):
        VisitForm(self, self.db, p_id, callback=cb, visit_data=None, allow_patient_select=False)

    def show_earnings(self):
        from ui.earnings_report import show_earnings_report
        show_earnings_report(self)

    def show_new_patients(self, filter_type):
        """
        filter_type:
            - 'today'  -> sirf aaj register hone wale patients
            - future me aur filters add ho sakte hain
        """
        from ui.patients_list import show_patients_list
        show_patients_list(self, filter_type=filter_type)



    def export_data(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"patients_export_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
        )
        if filepath:
            if self.db.export_patients_csv(filepath):
                messagebox.showinfo("Export", "Data exported successfully.")

    def load_visits(self, patient_id):
        # Clear existing
        for widget in self.visits_container.scrollable_frame.winfo_children():
            widget.destroy()

        visits = self.db.get_visits(patient_id)
        
        if not visits:
            empty_frame = ttk.Frame(self.visits_container.scrollable_frame, padding=PAD_XL)
            empty_frame.pack(fill="x", expand=True)
            ttk.Label(empty_frame, text="No visits recorded yet.", font=FONT_BODY_BOLD, foreground=COLOR_TEXT_MUTED).pack()
            ttk.Label(empty_frame, text="Click 'Add New Visit' to begin consultation.", font=FONT_SMALL_ITALIC).pack()
            return

        for v in visits:
            self.create_visit_card(v)

    def delete_patient_confirm(self, patient_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient and ALL their history?\nThis cannot be undone."):
            if self.db.delete_patient(patient_id):
                self.show_patients()

    # ==========================================
    # TODAY'S VISITS SCREEN
    # ==========================================
    # def show_today_visits(self):
    #     self.clear_content()
    #     visits = self.db.get_today_visits()

    #     # Header
    #     header = ttk.Frame(self.content_frame)
    #     header.pack(fill="x", pady=(0, PAD_MEDIUM))
        
    #     ttk.Button(header, text="← Back", command=self.show_home).pack(side="left", padx=(0, PAD_MEDIUM))
    #     ttk.Label(header, text="Today’s Queue", style="SubTitle.TLabel").pack(side="left")
    #     ttk.Label(header, text=f"(Total: {len(visits)})", style="Muted.TLabel").pack(side="left", padx=PAD_SMALL, pady=(5,0))
        
    #     ttk.Button(header, text="➕ Quick Visit", style="Accent.TButton",
    #         command=lambda: VisitForm(self, self.db, patient_id=0, callback=self.show_today_visits, visit_data=None, allow_patient_select=True)
    #     ).pack(side="right")

    #     # Content
    #     if not visits:
    #         ttk.Label(self.content_frame, text="No visits recorded for today.", font=FONT_HEADER, foreground=COLOR_TEXT_MUTED).pack(pady=50)
    #         return

    #     container = ScrollableFrame(self.content_frame)
    #     container.pack(fill="both", expand=True)

    #     for v in visits:
    #         self.create_today_visit_card(container.scrollable_frame, v)

    # ==========================================
    # CARD GENERATORS (UI COMPONENTS)
    # # ==========================================
    
    # def create_common_card_layout(self, parent, visit, is_today_view=False):
    #     """
    #     Shared logic to create a consistent card look.
    #     visit: (visit_id, patient_id, date, complaints, medicine, fees, remarks, patient_name [if today view])
    #     """
    #     # --- Card Container ---
    #     outer = ttk.Frame(parent, padding=(PAD_SMALL, PAD_SMALL))
    #     outer.pack(fill="x", padx=PAD_MEDIUM)
        
    #     card = ttk.Frame(outer, style="Card.TFrame", padding=PAD_MEDIUM)
    #     card.pack(fill="x")

    #     # --- Header Row ---
    #     header = ttk.Frame(card)
    #     header.pack(fill="x", pady=(0, PAD_MEDIUM))
        
    #     # Left Side of Header
    #     if is_today_view:
    #         # Show Patient Name clickable
    #         name_box = ttk.Frame(header)
    #         name_box.pack(side="left")
    #         name_lbl = ttk.Label(name_box, text=visit[7], font=FONT_HEADER, foreground=COLOR_PRIMARY, cursor="hand2")
    #         name_lbl.pack(anchor="w")
    #         name_lbl.bind("<Button-1>", lambda e: self.show_patient_details(visit[1]))
    #         ttk.Label(name_box, text=f"Time: {visit[2]}", font=FONT_SMALL_ITALIC).pack(anchor="w")
    #     else:
    #         # Just show Date
    #         ttk.Label(header, text=f"📅 {visit[2]}", font=FONT_HEADER, foreground=COLOR_PRIMARY).pack(side="left")

    #     # Right Side (Buttons)
    #     btn_box = ttk.Frame(header)
    #     btn_box.pack(side="right")
        
    #     cb_func = self.show_today_visits if is_today_view else lambda: self.load_visits(visit[1])
        
    #     ttk.Button(btn_box, text="Edit", width=6,
    #                command=lambda: VisitForm(self, self.db, visit[1], cb_func, visit)).pack(side="left", padx=(0, PAD_SMALL))
        
    #     ttk.Button(btn_box, text="Delete", width=6, style="Danger.TButton",
    #                command=lambda: self.delete_visit_confirm(visit[0], visit[1])).pack(side="left")

    #     # --- Content Grid ---
    #     # We replace tk.Message with ttk.Label using wraplength for cleaner look
    #     content = ttk.Frame(card)
    #     content.pack(fill="x")
    #     content.columnconfigure(1, weight=1) # Make detail column expand

    #     def add_row(label, text, color=COLOR_TEXT_MAIN, is_fee=False):
    #         row_frame = ttk.Frame(content)
    #         row_frame.pack(fill="x", pady=2)
            
    #         lbl = ttk.Label(row_frame, text=label, font=FONT_BODY_BOLD, width=12, foreground=COLOR_TEXT_MUTED)
    #         lbl.pack(side="left", anchor="n")
            
    #         # Text wrapping calc
    #         val_font = FONT_BODY_BOLD if is_fee else FONT_BODY
    #         val_color = COLOR_SUCCESS if is_fee else color
            
    #         val = ttk.Label(row_frame, text=text, font=val_font, foreground=val_color, wraplength=700)
    #         val.pack(side="left", anchor="w", fill="x", expand=True)

    #     add_row("Diagnosis:", visit[3])
    #     add_row("Rx/Meds:", visit[4])
    #     add_row("Fees:", f"PKR {visit[5]}", is_fee=True)
    #     if visit[6]:
    #         add_row("Notes:", visit[6], color=COLOR_TEXT_MUTED)

    # def create_visit_card(self, visit):
    #     self.create_common_card_layout(self.visits_container.scrollable_frame, visit, is_today_view=False)

    # def create_today_visit_card(self, parent, visit):
    #     self.create_common_card_layout(parent, visit, is_today_view=True)

    # def delete_visit_confirm(self, visit_id, patient_id):
    #     if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this visit?"):
    #         if self.db.delete_visit(visit_id):
    #             # Reload whichever view is active (simple check based on context, 
    #             # but here we just try to reload patient view if we have ID, logic handled in callbacks mostly)
    #             # For safety, we just pass control back to the specific view via callbacks usually, 
    #             # but since this triggers from a button inside the view, we can just:
    #             # But here, simpler to just trigger the UI refresh.
                
    #             # If we are in patient details:
    #             self.load_visits(patient_id)
    #             # If we were in today's view, the callback passed in create_common_card would handle it if we strictly used it,
    #             # but since we are calling this method directly, we might need a refresh.
    #             # A quick hack for the 'Today' view refresh without complex state tracking:
    #             if hasattr(self, 'search_var') and self.search_var.get() == "": 
    #                # If we are potentially on home/today screen logic could vary, 
    #                # but generally load_visits updates the scrollable frame if it exists.
    #                pass

    def print_profile(self, patient):
        visits = self.db.get_visits(patient[0], limit=3)
        ReportGenerator.generate_patient_profile(patient, visits)