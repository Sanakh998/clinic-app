import tkinter as tk
from tkinter import ttk, messagebox
from utils import center_window
from config.config import FONT_HEADER, FONT_MAIN, FONT_BODY, PAD_LARGE
from utils.center_window import center_window


class PatientForm(tk.Toplevel):
    def __init__(self, parent, db, callback, patient_data=None):
        super().__init__(parent)
        self.db = db
        self.callback = callback
        self.patient_data = patient_data 
        
        self.title("Edit Patient" if patient_data else "Add New Patient")
        # self.geometry("450x550") # Let content dictate height
        self.configure(padx=PAD_LARGE, pady=PAD_LARGE)
        
        self.create_widgets()
        
        # self.wait_visibility()
        center_window(self, parent)
        
        self.transient(parent)
        self.grab_set()

    def create_widgets(self):
        heading = ttk.Label(
            self, 
            text="Patient Information", 
            style="SubTitle.TLabel"
        )
        heading.pack(pady=(0, 15), anchor="center")

        labels = ["Name (Required)", "Phone", "Age", "Gender", "Address", "Medical Notes"]
        self.vars = {}
        self.entries = []  # ye list focus order maintain karne ke liye hai

        for label_text in labels:
            ttk.Label(self, text=label_text, font=FONT_HEADER).pack(anchor="w", pady=(0, 5))
            key = label_text.split(" ")[0].lower()

            if key == "gender":
                # Gender ke liye Combobox
                var = tk.StringVar(value="Male")
                cb = ttk.Combobox(
                    self, 
                    textvariable=var, 
                    values=["Male", "Female", "Other"], 
                    state="readonly",
                    font=FONT_BODY
                )
                cb.pack(fill="x", pady=(0, 15))

                self.vars["gender"] = var
                self.entries.append(cb)  # focus chain mein add

            elif key == "medical":
                # Medical Notes ke liye Text widget
                txt = tk.Text(self, height=3, width=50, font=FONT_BODY)
                txt.pack(fill="x", pady=(0, 15))

                self.vars["notes"] = txt
                self.entries.append(txt)

            else:
                # Normal Entry fields
                var = tk.StringVar()
                entry = ttk.Entry(self, textvariable=var, font=FONT_BODY)
                entry.pack(fill="x", pady=(0, 15))

                self.vars[key] = var
                self.entries.append(entry)

        # Agar patient update ho raha ho to existing data fill karo
        if self.patient_data:
            self.vars["name"].set(self.patient_data[1])
            self.vars["phone"].set(self.patient_data[2])
            self.vars["age"].set(self.patient_data[3])
            self.vars["gender"].set(self.patient_data[4])
            self.vars["address"].set(self.patient_data[5])
            self.vars["notes"].insert("1.0", self.patient_data[6])

        # ================= FOCUS & ENTER KEY LOGIC =================

        # Form open hote hi cursor Name field mein
        self.entries[0].focus_set()

        # Har widget par Enter key ka behavior set kar rahe hain
        for i, widget in enumerate(self.entries):
            # Last field ke baad Enter dabane par Save hoga
            if i == len(self.entries) - 1:
                widget.bind("<Return>", lambda e: self.save())
            else:
                # Text widget mein Enter normal rehne do
                if isinstance(widget, tk.Text):
                    continue
                # Entry / Combobox mein Enter se next field
                widget.bind(
                    "<Return>", 
                    lambda e, next_w=self.entries[i + 1]: next_w.focus_set()
                )

        ttk.Button(self, text="Save Record", command=self.save, style="Accent.TButton").pack(pady=20, fill="x")

    def save(self):
        # Name required hai
        name = self.vars["name"].get().strip()
        if not name:
            messagebox.showerror("Error", "Patient Name is required!")
            self.entries[0].focus_set()
            return

        data = {
            "name": name,
            "phone": self.vars["phone"].get().strip(),
            "age": self.vars["age"].get().strip() or 0,
            "gender": self.vars["gender"].get(),
            "address": self.vars["address"].get().strip(),
            "notes": self.vars["notes"].get("1.0", tk.END).strip()
        }

        if self.patient_data:
            self.db.update_patient(self.patient_data[0], **data)
            messagebox.showinfo("Success", "Patient details updated.")
        else:
            self.db.add_patient(**data)
            messagebox.showinfo("Success", "New patient added.")

        self.callback()
        self.destroy()
