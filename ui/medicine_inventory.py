import tkinter as tk
from tkinter import ttk, messagebox
from config.config import (
    FONT_HEADER, FONT_BODY, FONT_BODY_BOLD,
    COLOR_BG, PAD_MEDIUM, PAD_LARGE
)
from ui.table_factory import create_table

class MedicineInventoryFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.db = app.db
        self.configure(padding=PAD_MEDIUM)

        self.sort_column = None
        self.sort_reverse = False
        self.current_filter = "ALL"

        self.empty_frame = None
        self.table_container = None

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # ================= TOP BAR =================
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", pady=(0, PAD_MEDIUM))

        lbl_title = ttk.Label(
            top_frame,
            text="Homeopathic Medicine Usage",
            style="SubTitle.TLabel"
        )
        lbl_title.pack(side="left")

        btn_add = ttk.Button(
            top_frame,
            text="+ Add Medicine",
            command=self.open_add_dialog,
            style="Accent.TButton"
        )
        btn_add.pack(side="right", padx=PAD_MEDIUM)

        # ================= MAIN CONTAINER =================
        self.table_container = ttk.Frame(self)
        self.table_container.pack(fill="both", expand=True)

        # ================= FILTER BAR =================
        self.filter_frame = ttk.Frame(self.table_container)
        self.filter_frame.pack(fill="x", pady=(0, PAD_MEDIUM))

        ttk.Button(self.filter_frame, text="All",
                   command=lambda: self.apply_filter("ALL")).pack(side="left", padx=5)

        ttk.Button(self.filter_frame, text="Most Used",
                   command=lambda: self.apply_filter("MOST")).pack(side="left", padx=5)

        ttk.Button(self.filter_frame, text="Recently Used",
                   command=lambda: self.apply_filter("RECENT")).pack(side="left", padx=5)

        ttk.Button(self.filter_frame, text="Never Used",
                   command=lambda: self.apply_filter("NEVER")).pack(side="left", padx=5)

        # ================= SEARCH =================
        search_frame = ttk.Frame(self.filter_frame)
        search_frame.pack(side="right", padx=PAD_MEDIUM)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search)

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        ttk.Entry(search_frame, textvariable=self.search_var, width=25).pack(side="left")

        # ================= TABLE =================
        columns = ("ID", "Name", "Times Used", "Last Used", "Description")

        column_config = {
            "ID": {"width": 50, "anchor": "center"},
            "Name": {"width": 250, "anchor": "w"},
            "Times Used": {"width": 120, "anchor": "center"},
            "Last Used": {"width": 150, "anchor": "center"},
            "Description": {"width": 250, "anchor": "w", "stretch": True}
        }

        self.tree = create_table(self.table_container, columns, column_config)

        for col in columns:
            self.tree.heading(col, text=col,
                              command=lambda c=col: self.sort_by_column(c))

        self.tree.bind("<Double-1>", self.on_double_click)

    # ================= LOAD DATA =================
    def load_data(self, query=None):
        rows = self.db.search_medicines(query) if query else self.db.get_all_medicines()

        # Empty state
        if not rows:
            self.show_empty_state()
            return
        else:
            self.hide_empty_state()

        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = self.filter_rows(rows)

        if self.sort_column:
            rows = self.sort_rows(rows)

        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            display_values = (
                row[0],
                row[1],
                row[3],
                row[4] if row[4] else "-",
                row[2] if row[2] else ""
            )
            self.tree.insert("", "end", values=display_values, tags=(tag,))

    # ================= EMPTY STATE =================
    def show_empty_state(self):
        if self.table_container:
            self.table_container.pack_forget()

        if not self.empty_frame:
            self.empty_frame = ttk.Frame(self)
            self.empty_frame.pack(fill="both", expand=True)

            ttk.Label(
                self.empty_frame,
                text="No Medicines Found",
                style="SubTitle.TLabel"
            ).pack(pady=(120, 20))

            ttk.Button(
                self.empty_frame,
                text="Load Default Medicines",
                style="Accent.TButton",
                command=self.load_default_medicines
            ).pack()

        else:
            self.empty_frame.pack(fill="both", expand=True)

    def hide_empty_state(self):
        if self.empty_frame:
            self.empty_frame.pack_forget()

        if self.table_container:
            self.table_container.pack(fill="both", expand=True)

    def load_default_medicines(self):
        self.db.load_common_medicines()
        self.load_data()

    # ================= FILTER =================
    def apply_filter(self, filter_type):
        self.current_filter = filter_type
        self.load_data(self.search_var.get().strip())

    def filter_rows(self, rows):
        if self.current_filter == "MOST":
            return sorted(rows, key=lambda r: r[3], reverse=True)

        elif self.current_filter == "RECENT":
            return sorted(rows,
                          key=lambda r: r[4] if r[4] else "",
                          reverse=True)

        elif self.current_filter == "NEVER":
            return [r for r in rows if r[3] == 0]

        return rows

    # ================= SORT =================
    def sort_by_column(self, col):
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        self.load_data(self.search_var.get().strip())

    def sort_rows(self, rows):
        col_index_map = {
            "ID": 0,
            "Name": 1,
            "Times Used": 3,
            "Last Used": 4,
            "Description": 2
        }

        idx = col_index_map[self.sort_column]

        return sorted(
            rows,
            key=lambda r: r[idx] if r[idx] is not None else "",
            reverse=self.sort_reverse
        )

    # ================= SEARCH =================
    def on_search(self, *args):
        self.load_data(self.search_var.get().strip())

    # ================= EDIT =================
    def on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        values = self.tree.item(item_id, "values")
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
        self.geometry("350x250")
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
        ttk.Label(self, text="Medicine Name:", font=FONT_HEADER).pack(anchor="w", pady=(0, 5))
        self.entry_name = ttk.Entry(self, font=FONT_BODY)
        self.entry_name.pack(fill="x", pady=(0, 15))
        self.entry_name.focus_set()

        ttk.Label(self, text="Description:", font=FONT_HEADER).pack(anchor="w", pady=(0, 5))
        self.entry_desc = ttk.Entry(self, font=FONT_BODY)
        self.entry_desc.pack(fill="x", pady=(0, 15))

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
            self.entry_name.insert(0, self.medicine_data[1])
            if self.medicine_data[4]:
                self.entry_desc.insert(0, self.medicine_data[4])

    def save_medicine(self):
        name = self.entry_name.get().strip()
        desc = self.entry_desc.get().strip()

        if not name:
            messagebox.showwarning("Validation", "Medicine Name is required.")
            return

        if self.medicine_data:
            m_id = self.medicine_data[0]
            self.db.update_medicine(m_id, name, desc)
        else:
            self.db.add_medicine(name, desc)

        self.callback()
        self.destroy()

    def delete_medicine(self):
        if messagebox.askyesno("Confirm Delete", "Delete this medicine?"):
            m_id = self.medicine_data[0]
            self.db.delete_medicine(m_id)
            self.callback()
            self.destroy()



def show_medicine_inventory(app):
    app.clear_content()
    inventory_frame = MedicineInventoryFrame(app.content_frame, app)
    inventory_frame.pack(fill="both", expand=True)