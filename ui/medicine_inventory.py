
import tkinter as tk
from tkinter import ttk, messagebox
from config.config import (
    FONT_TITLE_SUB, FONT_HEADER, FONT_BODY,
    COLOR_BG, COLOR_SURFACE, COLOR_PRIMARY, PAD_MEDIUM, PAD_SMALL, PAD_LARGE
)
from ui.table_factory import create_table

class MedicineInventoryFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.db = app.db
        self.configure(padding=PAD_MEDIUM)
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Top Bar: Title + Add Button + Search
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", pady=(0, PAD_MEDIUM))

        # Title
        lbl_title = ttk.Label(
            top_frame, 
            text="Medicine Inventory", 
            style="SubTitle.TLabel"
        )
        lbl_title.pack(side="left")

        # Search
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side="right", padx=PAD_MEDIUM)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search)
        
        ttk.Label(search_frame, text="Search:", font=FONT_HEADER).pack(side="left", padx=5)
        ttk.Entry(search_frame, textvariable=self.search_var, width=25).pack(side="left")

        # Add Button
        btn_add = ttk.Button(
            top_frame,
            text="+ Add Medicine",
            command=self.open_add_dialog,
            style="Accent.TButton"
        )
        btn_add.pack(side="right")

        # Table
        columns = ("ID", "Name", "Type", "Quantity", "Price", "Description")
        column_config = {
            "ID": {"width": 50, "anchor": "center"},
            "Name": {"width": 200, "anchor": "w"},
            "Type": {"width": 100, "anchor": "center"},
            "Quantity": {"width": 80, "anchor": "center"},
            "Price": {"width": 80, "anchor": "e"},
            "Description": {"width": 250, "anchor": "w", "stretch": True}
        }
        self.tree = create_table(self, columns, column_config)
        

        
        # Bind double click to edit
        self.tree.bind("<Double-1>", self.on_double_click)

    def load_data(self, query=None):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        if query:
            rows = self.db.search_medicines(query)
        else:
            rows = self.db.get_all_medicines()

        for row in rows:
            # row: (id, name, type, quantity, price, desc, created_at)
            # Display: ID, Name, Type, Quantity, Price, Description
            display_values = (row[0], row[1], row[2], row[3], f"{row[4]:.2f}", row[5])
            self.tree.insert("", "end", values=display_values)

    def on_search(self, *args):
        query = self.search_var.get().strip()
        self.load_data(query)

    def on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        
        values = self.tree.item(item_id, "values")
        if values:
            medicine_id = values[0]
            # Fetch full details from DB to be sure
            # Actually values has enough info for now except created_at which we don't edit
            self.open_edit_dialog(values)

    def open_add_dialog(self):
        MedicineForm(self.app, self.db, callback=self.load_data)

    def open_edit_dialog(self, values):
        MedicineForm(self.app, self.db, callback=self.load_data, medicine_data=values)


class MedicineForm(tk.Toplevel):
    def __init__(self, parent, db, callback, medicine_data=None):
        super().__init__(parent)
        self.db = db
        self.callback = callback
        self.medicine_data = medicine_data # Tuple of values from tree

        mode = "Edit" if medicine_data else "Add"
        self.title(f"{mode} Medicine")
        self.geometry("400x500")
        self.configure(padx=PAD_LARGE, pady=PAD_LARGE, bg=COLOR_BG)
        
        self.setup_form()
        
        # Center and modal
        self.transient(parent)
        self.grab_set()
        # parent.eval(f'tk::PlaceWindow {self} center') # Simple center
        # Or reuse center_window utility if available
        try:
            from utils.center_window import center_window
            center_window(self, parent)
        except ImportError:
            pass

    def setup_form(self):
        # Name
        ttk.Label(self, text="Medicine Name:", font=FONT_HEADER).pack(anchor="w", pady=(0, 5))
        self.entry_name = ttk.Entry(self, font=FONT_BODY)
        self.entry_name.pack(fill="x", pady=(0, 15))

        # Type
        ttk.Label(self, text="Type:", font=FONT_HEADER).pack(anchor="w", pady=(0, 5))
        self.entry_type = ttk.Combobox(self, values=["Dilution", "Mother Tincture", "Trituration", "Biochemic", "Ointment", "Drops", "Other"], font=FONT_BODY)
        self.entry_type.pack(fill="x", pady=(0, 15))

        # Quantity
        ttk.Label(self, text="Quantity:", font=FONT_HEADER).pack(anchor="w", pady=(0, 5))
        self.entry_qty = ttk.Entry(self, font=FONT_BODY)
        self.entry_qty.pack(fill="x", pady=(0, 15))

        # Price
        ttk.Label(self, text="Price:", font=FONT_HEADER).pack(anchor="w", pady=(0, 5))
        self.entry_price = ttk.Entry(self, font=FONT_BODY)
        self.entry_price.pack(fill="x", pady=(0, 15))

        # Description
        ttk.Label(self, text="Description:", font=FONT_HEADER).pack(anchor="w", pady=(0, 5))
        self.entry_desc = ttk.Entry(self, font=FONT_BODY)
        self.entry_desc.pack(fill="x", pady=(0, 15))

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=(20, 0))

        if self.medicine_data:
            ttk.Button(btn_frame, text="Update", command=self.save_medicine, style="Accent.TButton").pack(side="right", padx=5)
            ttk.Button(btn_frame, text="Delete", command=self.delete_medicine, style="Danger.TButton").pack(side="left", padx=5)
        else:
            ttk.Button(btn_frame, text="Save", command=self.save_medicine, style="Accent.TButton").pack(side="right", padx=5)

        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right")

        self.populate_fields()

    def populate_fields(self):
        if self.medicine_data:
            # values: ID, Name, Type, Quantity, Price, Description
            self.entry_name.insert(0, self.medicine_data[1])
            self.entry_type.set(self.medicine_data[2])
            self.entry_qty.insert(0, self.medicine_data[3])
            self.entry_price.insert(0, self.medicine_data[4])
            
            # Helper safely insert if description not empty
            desc = self.medicine_data[5]
            if desc and desc != "None":
                self.entry_desc.insert(0, desc)

    def save_medicine(self):
        name = self.entry_name.get().strip()
        m_type = self.entry_type.get().strip()
        qty = self.entry_qty.get().strip() or "0"
        price = self.entry_price.get().strip() or "0.0"
        desc = self.entry_desc.get().strip()

        if not name:
            messagebox.showwarning("Validation", "Medicine Name is required.")
            return

        try:
            qty = int(qty)
            price = float(price)
        except ValueError:
            messagebox.showerror("Validation", "Quantity must be integer and Price must be number.")
            return

        if self.medicine_data:
            # Update
            m_id = self.medicine_data[0]
            success = self.db.update_medicine(m_id, name, m_type, qty, price, desc)
        else:
            # Add
            success = self.db.add_medicine(name, m_type, qty, price, desc)

        if success:
            self.callback()
            self.destroy()

    def delete_medicine(self):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this medicine?"):
            m_id = self.medicine_data[0]
            if self.db.delete_medicine(m_id):
                self.callback()
                self.destroy()

def show_medicine_inventory(app):
    app.clear_content()
    MedicineInventoryFrame(app.content_frame, app).pack(fill="both", expand=True)

