import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sv_ttk
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

    # def load_visits(self, patient_id):
    #     # Clear existing
    #     for widget in self.visits_container.scrollable_frame.winfo_children():
    #         widget.destroy()

    #     visits = self.db.get_visits(patient_id)
        
    #     if not visits:
    #         empty_frame = ttk.Frame(self.visits_container.scrollable_frame, padding=PAD_XL)
    #         empty_frame.pack(fill="x", expand=True)
    #         ttk.Label(empty_frame, text="No visits recorded yet.", font=FONT_BODY_BOLD, foreground=COLOR_TEXT_MUTED).pack()
    #         ttk.Label(empty_frame, text="Click 'Add New Visit' to begin consultation.", font=FONT_SMALL_ITALIC).pack()
    #         return

    #     for v in visits:
    #         self.create_visit_card(v)

    def delete_patient_confirm(self, patient_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this patient and ALL their history?\nThis cannot be undone."):
            if self.db.delete_patient(patient_id):
                self.show_patients()

    def print_profile(self, patient):
        visits = self.db.get_visits(patient[0], limit=3)
        ReportGenerator.generate_patient_profile(patient, visits)