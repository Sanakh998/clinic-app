import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from utils.center_window import center_window
from config.config import FONT_HEADER, FONT_MAIN


class VisitForm(tk.Toplevel):
    def __init__(self, parent, db, patient_id, callback, visit_data=None, allow_patient_select=False):
        super().__init__(parent)
        self.db = db
        self.patient_id = patient_id
        self.callback = callback
        self.visit_data = visit_data
        self.allow_patient_select = allow_patient_select
        self.patient = None

        if patient_id:
            self.patient = self.db.get_patient_by_id(patient_id)

        mode = "Edit" if visit_data else "Add New"
        self.title(f"{mode} Visit")
        self.geometry("450x550")
        self.configure(padx=20, pady=20)
        
        self.create_widgets()
        
        # self.wait_visibility()
        center_window(self, parent)
        
        self.transient(parent)
        self.grab_set()

    def create_widgets(self):
        heading = ttk.Label(
            self, 
            text="Visit Information", 
            font=("Helvetica", 15, "bold")
        )
        heading.pack(pady=(0, 15), anchor="center")

        self.entries = []  # focus order maintain karne ke liye

        if self.allow_patient_select:
            ttk.Label(self, text="Select Patient:", font=FONT_HEADER).pack(anchor="w")

            patients = self.db.get_all_patients()
            self.patient_map = {f"{p[1]} (ID: {p[0]})": p[0] for p in patients}

            self.patient_var = tk.StringVar()
            cb = ttk.Combobox(
                self,
                textvariable=self.patient_var,
                values=list(self.patient_map.keys()),
            )
            cb.pack(fill="x", pady=(0, 15))

            all_patients = list(self.patient_map.keys())

            def filter_patients(event):
                typed = self.patient_var.get().lower()
                filtered = [p for p in all_patients if typed in p.lower()]
                cb["values"] = filtered

            cb.bind("<KeyRelease>", filter_patients)

            cb.current(0)
            self.patient_id = self.patient_map[cb.get()]

            def on_patient_change(event):
                self.patient_id = self.patient_map[self.patient_var.get()]

            cb.bind("<<ComboboxSelected>>", on_patient_change)
            self.entries.append(cb)


        # Patient Info Banner
        if not self.allow_patient_select and self.patient:
            info_frame = ttk.Frame(self, padding=5)
            info_frame.pack(fill="x", pady=(0, 10))

            ttk.Label(
                info_frame,
                text=f"Patient: {self.patient[1]}",
                font=("Segoe UI", 12, "bold"),
                foreground="#103c68"
            ).pack(side="left")

            ttk.Label(
                info_frame,
                text=f"ID: {self.patient[0]}",
                font=("Segoe UI", 10),
                foreground="#555"
            ).pack(side="right")

        # ================= Date =================
        ttk.Label(self, text="Date:", font=FONT_HEADER).pack(anchor="w")
        initial_date = self.visit_data[2] if self.visit_data else datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.date_var = tk.StringVar(value=initial_date)
        entry_date = ttk.Entry(self, textvariable=self.date_var)
        entry_date.pack(fill="x", pady=(0, 10))
        self.entries.append(entry_date)

        # ================= History =================
        ttk.Label(self, text="History:", font=FONT_HEADER).pack(anchor="w")
        self.txt_complaints = tk.Text(self, height=3, font=FONT_MAIN)
        self.txt_complaints.pack(fill="x", pady=(0, 10))
        self.entries.append(self.txt_complaints)

        if self.visit_data:
            self.txt_complaints.insert("1.0", self.visit_data[3])

        # ================= Medicine =================
        ttk.Label(self, text="Medicine:", font=FONT_HEADER).pack(anchor="w")
        self.txt_medicine = tk.Text(self, height=3, font=FONT_MAIN)
        self.txt_medicine.pack(fill="x", pady=(0, 10))
        self.entries.append(self.txt_medicine)

        if self.visit_data:
            self.txt_medicine.insert("1.0", self.visit_data[4])

        # ================= FEES =================
        ttk.Label(self, text="Fees:", font=FONT_HEADER).pack(anchor="w")
        self.entry_fees = ttk.Entry(self, font=FONT_MAIN)
        self.entry_fees.pack(fill="x", pady=(0, 20))
        self.entries.append(self.entry_fees)

        if self.visit_data:
            self.entry_fees.insert(0, self.visit_data[5])

        # ================= Remarks =================
        ttk.Label(self, text="Remarks:", font=FONT_HEADER).pack(anchor="w")
        self.entry_remarks = ttk.Entry(self, font=FONT_MAIN)
        self.entry_remarks.pack(fill="x", pady=(0, 20))
        self.entries.append(self.entry_remarks)

        if self.visit_data:
            self.entry_remarks.insert(0, self.visit_data[6])

        # ================= Autocomplete Logic =================
        self.suggestion_box = None
        self.medicines_list = [m[1] for m in self.db.get_all_medicines()]
        
        self.txt_medicine.bind("<KeyRelease>", self.on_medicine_type)
        self.txt_medicine.bind("<FocusOut>", self.hide_suggestions)
        # Bind Down arrow to move focus to listbox if visible
        self.txt_medicine.bind("<Down>", self.focus_suggestion)


        # ================= Focus & Enter Logic =================

        # Form open hote hi cursor Date field mein
        self.entries[0].focus_set()

        for i, widget in enumerate(self.entries):
            # Last field (Remarks) par Enter dabane se Save ho
            if i == len(self.entries) - 1:
                widget.bind("<Return>", lambda e: self.save_visit())
            else:
                # Text widgets mein Enter normal kaam kare (new line)
                if isinstance(widget, tk.Text):
                    continue
                # Entry widget mein Enter se next field
                widget.bind(
                    "<Return>",
                    lambda e, next_w=self.entries[i + 1]: next_w.focus_set()
                )

        # ================= Buttons =================
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x")
        
        save_text = "Update Visit" if self.visit_data else "Save Visit"
        ttk.Button(btn_frame, text=save_text, command=self.save_visit).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right")

    def on_medicine_type(self, event):
        # Ignore navigation keys
        if event.keysym in ("Up", "Down", "Left", "Right", "Return", "Escape", "Tab"):
            return

        # Get current line text
        try:
            current_line_idx = self.txt_medicine.index("insert linestart")
            current_line_end = self.txt_medicine.index("insert lineend")
            line_text = self.txt_medicine.get(current_line_idx, current_line_end).strip()
            
            # Simple logic: match last word being typed if multiple medicines separated by newline
            # Or simplified: check if line match any medicine
            # Let's try to match from the beginning of the line or last word
            # For simplicity, let's match the whole line content against medicine names
            
            typed = line_text.lower()
            if not typed:
                self.hide_suggestions(None)
                return

            msg_matches = [m for m in self.medicines_list if typed in m.lower()]
            
            if msg_matches:
                self.show_suggestions(msg_matches)
            else:
                self.hide_suggestions(None)
        except Exception:
            pass

    def show_suggestions(self, matches):
        if self.suggestion_box:
            self.suggestion_box.destroy()

        # Position popup near cursor
        # Get cursor stats
        try:
            x, y, w, h = self.txt_medicine.bbox("insert")
            # bbox returns relative coordinates in text widget
            
            # Absolute position
            root_x = self.txt_medicine.winfo_rootx() + x
            root_y = self.txt_medicine.winfo_rooty() + y + h
            
            self.suggestion_box = tk.Toplevel(self)
            self.suggestion_box.wm_overrideredirect(True)
            self.suggestion_box.geometry(f"200x150+{root_x}+{root_y}")
            
            self.lb_suggestions = tk.Listbox(self.suggestion_box, font=FONT_MAIN, height=5)
            self.lb_suggestions.pack(fill="both", expand=True)
            
            for m in matches:
                self.lb_suggestions.insert(tk.END, m)
                
            self.lb_suggestions.bind("<<ListboxSelect>>", self.on_suggestion_select)
            self.lb_suggestions.bind("<Return>", self.on_suggestion_select)
            self.lb_suggestions.bind("<Escape>", self.hide_suggestions)
            
            # Selection focus
            self.lb_suggestions.select_set(0)
        except:
            pass
            
    def hide_suggestions(self, event):
        if self.suggestion_box:
            # Check if focus is moving to the suggestion box
            if self.focus_get() == self.lb_suggestions:
                return
            self.suggestion_box.destroy()
            self.suggestion_box = None

    def focus_suggestion(self, event):
        if self.suggestion_box:
            self.lb_suggestions.focus_set()
            return "break" # Prevent default scrolling

    def on_suggestion_select(self, event):
        if not self.suggestion_box:
            return
            
        selection = self.lb_suggestions.curselection()
        if selection:
            medicine = self.lb_suggestions.get(selection[0])
            
            # Insert into Text widget
            # Replace current line with selected medicine
            current_line_start = self.txt_medicine.index("insert linestart")
            current_line_end = self.txt_medicine.index("insert lineend")
            
            self.txt_medicine.delete(current_line_start, current_line_end)
            self.txt_medicine.insert(current_line_start, medicine)
            self.txt_medicine.mark_set("insert", f"{current_line_start} + {len(medicine)}c")
            
            self.hide_suggestions(None)
            self.txt_medicine.focus_set()
            
        return "break"

    def save_visit(self):
        date_str = self.date_var.get()
        complaints = self.txt_complaints.get("1.0", tk.END).strip()
        medicine = self.txt_medicine.get("1.0", tk.END).strip()
        fees = self.entry_fees.get().strip()
        remarks = self.entry_remarks.get().strip()

        if not complaints and not medicine:
            messagebox.showwarning("Validation", "Please enter at least history or medicine.")
            self.txt_complaints.focus_set()
            return

        if self.visit_data:
            success = self.db.update_visit(
                self.visit_data[0], complaints, medicine, fees, remarks, date_str
            )
        else:
            success = self.db.add_visit(
                self.patient_id, complaints, medicine, fees, remarks, date_str
            )

        if success:
            self.callback()
            self.destroy()

