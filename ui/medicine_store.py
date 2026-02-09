import tkinter as tk
from tkinter import ttk, messagebox
from config.config import (
    FONT_TITLE_SUB, FONT_HEADER, FONT_BODY, FONT_SMALL_ITALIC,
    COLOR_BG, COLOR_SURFACE, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, PAD_MEDIUM, PAD_SMALL, PAD_LARGE
)
from ui.table_factory import create_table
from database.medicine_database import MedicineDatabaseManager
from services.medicine_service import MedicineService
from services.inventory_service import InventoryService
import datetime

class MedicineStoreDashboard(ttk.Frame):
    """Main Medicine Store Dashboard - Entry point for medicine inventory module."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        # Initialize Medicine Database (separate from main clinic db)
        self.med_db = MedicineDatabaseManager("clinic_medicine.db")
        self.medicine_service = MedicineService(self.med_db)
        self.inventory_service = InventoryService(self.med_db)
        
        self.configure(padding=PAD_MEDIUM)
        self.setup_ui()
        self.load_dashboard_stats()

    def setup_ui(self):
        # === HEADER ===
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, PAD_LARGE))
        
        ttk.Label(
            header_frame,
            text="🧪 Medicine Store",
            style="Title.TLabel"
        ).pack(side="left")
        
        # Quick Actions
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side="right")
        
        ttk.Button(
            btn_frame,
            text="➕ Add Medicine",
            style="Accent.TButton",
            command=self.open_add_medicine_wizard
        ).pack(side="left", padx=PAD_SMALL)
        
        ttk.Button(
            btn_frame,
            text="📦 Manage Inventory",
            command=self.open_inventory_tabs
        ).pack(side="left", padx=PAD_SMALL)

        # === STATISTICS CARDS ===
        stats_container = ttk.Frame(self)
        stats_container.pack(fill="x", pady=(0, PAD_LARGE))
        
        for i in range(4):
            stats_container.columnconfigure(i, weight=1)
        
        # Create stat cards
        self.card_labels = {}
        cards_data = [
            ("total_medicines", "📋", "Total Medicines", "0", COLOR_PRIMARY),
            ("active_variants", "💊", "Active Variants", "0", COLOR_PRIMARY),
            ("low_stock", "⚠️", "Low Stock Alerts", "0", COLOR_WARNING),
            ("expiring_soon", "⏰", "Expiring Soon", "0", COLOR_DANGER)
        ]
        
        for idx, (key, icon, title, value, color) in enumerate(cards_data):
            self.card_labels[key] = self.create_stat_card(
                stats_container, idx, icon, title, value, color
            )

        # === TWO COLUMN LAYOUT ===
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True)
        
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left: Low Stock Alerts
        self.build_low_stock_section(content_frame)
        
        # Right: Recent Additions / Quick Access
        self.build_quick_access_section(content_frame)

    def create_stat_card(self, parent, column, icon, title, value, color):
        """Create a statistics card."""
        outer = ttk.Frame(parent, padding=2, style="Outer.TFrame")
        outer.grid(row=0, column=column, padx=PAD_SMALL, sticky="nsew")
        
        card = ttk.Frame(outer, style="Card.TFrame", padding=PAD_LARGE)
        card.pack(fill="both", expand=True)
        
        tk.Label(
            card, text=icon, font=("Segoe UI", 28),
            fg=color, bg=COLOR_SURFACE
        ).pack(anchor="w")
        
        value_label = tk.Label(
            card, text=value, font=("Segoe UI", 22, "bold"),
            fg=COLOR_TEXT_MAIN, bg=COLOR_SURFACE
        )
        value_label.pack(anchor="w")
        
        tk.Label(
            card, text=title, font=FONT_SMALL_ITALIC,
            fg=COLOR_TEXT_MUTED, bg=COLOR_SURFACE
        ).pack(anchor="w")
        
        return value_label

    def build_low_stock_section(self, parent):
        """Build low stock alerts section."""
        section = ttk.Frame(parent, style="Card.TFrame", padding=PAD_MEDIUM)
        section.grid(row=0, column=0, sticky="nsew", padx=(0, PAD_SMALL))
        
        # Header
        ttk.Label(
            section,
            text="⚠️ Low Stock Alerts",
            style="SubTitle.TLabel"
        ).pack(anchor="w", pady=(0, PAD_MEDIUM))
        
        # Table
        columns = ("Medicine", "Potency", "Stock", "Min Level")
        col_config = {
            "Medicine": {"width": 150, "anchor": "w"},
            "Potency": {"width": 80, "anchor": "center"},
            "Stock": {"width": 60, "anchor": "center"},
            "Min Level": {"width": 80, "anchor": "center"}
        }
        
        self.low_stock_tree = create_table(section, columns, col_config)

    def build_quick_access_section(self, parent):
        """Build quick access / category section."""
        section = ttk.Frame(parent, style="Card.TFrame", padding=PAD_MEDIUM)
        section.grid(row=0, column=1, sticky="nsew", padx=(PAD_SMALL, 0))
        
        ttk.Label(
            section,
            text="📂 Quick Access",
            style="SubTitle.TLabel"
        ).pack(anchor="w", pady=(0, PAD_MEDIUM))
        
        # Category buttons
        categories = [
            ("💧 Dilutions", "DILUTION"),
            ("🌿 Mother Tinctures (Q)", "Q"),
            ("⚗️ Biochemic Salts", "BIOCHEMIC"),
            ("🔬 Complexes", "COMPLEX"),
            ("⚠️ Nosodes", "NOSODE"),
            ("⚪ Globules", "GLOBULE")
        ]
        
        for label, category in categories:
            btn = ttk.Button(
                section,
                text=label,
                command=lambda c=category: self.open_category_view(c),
                width=30
            )
            btn.pack(fill="x", pady=PAD_SMALL)

    def load_dashboard_stats(self):
        """Load and update dashboard statistics."""
        # Total medicines (count from medicine_master)
        conn = self.med_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM medicine_master WHERE is_active = 1")
        total_medicines = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM medicine_variants")
        total_variants = cursor.fetchone()[0]
        
        conn.close()
        
        # Low stock count
        low_stock = self.inventory_service.check_low_stock()
        low_stock_count = len(low_stock)
        
        # Update cards
        self.card_labels["total_medicines"].config(text=str(total_medicines))
        self.card_labels["active_variants"].config(text=str(total_variants))
        self.card_labels["low_stock"].config(text=str(low_stock_count))
        self.card_labels["expiring_soon"].config(text="0")  # Implement later
        
        # Update low stock table
        for item in self.low_stock_tree.get_children():
            self.low_stock_tree.delete(item)
        
        for row in low_stock:
            # row: (name, potency, form, stock, min_level)
            display = (row[0], row[1] or "N/A", row[3], row[4])
            self.low_stock_tree.insert("", "end", values=display)

    def open_add_medicine_wizard(self):
        """Open wizard to add new medicine."""
        AddMedicineWizard(self, self.med_db, self.medicine_service, callback=self.load_dashboard_stats)

    def open_inventory_tabs(self):
        """Open full inventory management view."""
        InventoryTabsView(self.app, self.med_db, self.medicine_service, self.inventory_service)

    def open_category_view(self, category):
        """Open filtered view for a specific category."""
        messagebox.showinfo("Category View", f"Opening {category} view")
        # TODO: Implement filtered inventory view


class AddMedicineWizard(tk.Toplevel):
    """Multi-step wizard for adding new medicine."""
    
    def __init__(self, parent, med_db, medicine_service, callback):
        super().__init__(parent)
        self.med_db = med_db
        self.medicine_service = medicine_service
        self.callback = callback
        
        self.title("Add New Medicine")
        self.geometry("500x600")
        self.configure(padx=PAD_LARGE, pady=PAD_LARGE, bg=COLOR_BG)
        
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        ttk.Label(
            self,
            text="Add New Medicine",
            style="Title.TLabel"
        ).pack(pady=(0, PAD_LARGE))
        
        # Medicine Name
        ttk.Label(self, text="Medicine Name:", font=FONT_HEADER).pack(anchor="w", pady=(0, 5))
        self.entry_name = ttk.Entry(self, font=FONT_BODY)
        self.entry_name.pack(fill="x", pady=(0, 15))
        
        # Category
        ttk.Label(self, text="Category:", font=FONT_HEADER).pack(anchor="w", pady=(0, 5))
        self.combo_category = ttk.Combobox(
            self,
            values=["DILUTION", "Q", "BIOCHEMIC", "COMPLEX", "NOSODE", "GLOBULE", "OTHER"],
            font=FONT_BODY,
            state="readonly"
        )
        self.combo_category.pack(fill="x", pady=(0, 15))
        self.combo_category.current(0)
        
        # Manufacturer
        ttk.Label(self, text="Manufacturer (Optional):", font=FONT_HEADER).pack(anchor="w", pady=(0, 5))
        self.entry_manufacturer = ttk.Entry(self, font=FONT_BODY)
        self.entry_manufacturer.pack(fill="x", pady=(0, 15))
        
        # Is Restricted (Nosode warning)
        self.var_restricted = tk.BooleanVar()
        ttk.Checkbutton(
            self,
            text="⚠️ Restricted (Requires special handling)",
            variable=self.var_restricted
        ).pack(anchor="w", pady=(0, 15))
        
        # Notes
        ttk.Label(self, text="Notes:", font=FONT_HEADER).pack(anchor="w", pady=(0, 5))
        self.text_notes = tk.Text(self, font=FONT_BODY, height=4)
        self.text_notes.pack(fill="x", pady=(0, 15))
        
        # === VARIANT SECTION ===
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=PAD_MEDIUM)
        
        ttk.Label(
            self,
            text="Initial Variant (Optional)",
            font=FONT_HEADER
        ).pack(anchor="w", pady=(0, 10))
        
        variant_frame = ttk.Frame(self)
        variant_frame.pack(fill="x")
        
        # Potency
        ttk.Label(variant_frame, text="Potency:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_potency = ttk.Entry(variant_frame, width=15)
        self.entry_potency.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        
        # Form
        ttk.Label(variant_frame, text="Form:").grid(row=0, column=2, sticky="w", pady=5, padx=(15, 0))
        self.combo_form = ttk.Combobox(
            variant_frame,
            values=["liquid", "tablet", "globule", "ointment"],
            width=12,
            state="readonly"
        )
        self.combo_form.grid(row=0, column=3, sticky="ew", pady=5, padx=5)
        self.combo_form.current(0)
        
        # Bottle Size
        ttk.Label(variant_frame, text="Size:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_size = ttk.Entry(variant_frame, width=15)
        self.entry_size.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        
        # Unit
        ttk.Label(variant_frame, text="Unit:").grid(row=1, column=2, sticky="w", pady=5, padx=(15, 0))
        self.combo_unit = ttk.Combobox(
            variant_frame,
            values=["ml", "tablets", "pills", "gm"],
            width=12,
            state="readonly"
        )
        self.combo_unit.grid(row=1, column=3, sticky="ew", pady=5, padx=5)
        self.combo_unit.current(0)
        
        variant_frame.columnconfigure(1, weight=1)
        variant_frame.columnconfigure(3, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=(PAD_LARGE, 0))
        
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side="right", padx=5)
        
        ttk.Button(
            btn_frame,
            text="Save Medicine",
            style="Accent.TButton",
            command=self.save_medicine
        ).pack(side="right")
        
    def save_medicine(self):
        """Save the new medicine and variant."""
        name = self.entry_name.get().strip()
        category = self.combo_category.get()
        manufacturer = self.entry_manufacturer.get().strip()
        is_restricted = self.var_restricted.get()
        notes = self.text_notes.get("1.0", "end-1c").strip()
        
        if not name:
            messagebox.showwarning("Validation", "Medicine name is required")
            return
        
        # Create medicine
        medicine_id = self.medicine_service.create_medicine(
            name, category, manufacturer, is_restricted, notes
        )
        
        if not medicine_id:
            messagebox.showerror("Error", "Failed to create medicine")
            return
        
        # Create variant if provided
        potency = self.entry_potency.get().strip()
        if potency:
            form = self.combo_form.get()
            size = self.entry_size.get().strip()
            unit = self.combo_unit.get()
            
            variant_id = self.medicine_service.add_variant(
                medicine_id, potency, form, size, unit, min_stock_level=5
            )
            
            if not variant_id:
                messagebox.showwarning("Warning", "Medicine created but variant failed")
        
        messagebox.showinfo("Success", "Medicine added successfully!")
        self.callback()
        self.destroy()


class InventoryTabsView(tk.Toplevel):
    """Full inventory view with tabs for different categories."""
    
    def __init__(self, app, med_db, medicine_service, inventory_service):
        super().__init__(app)
        self.med_db = med_db
        self.medicine_service = medicine_service
        self.inventory_service = inventory_service
        
        self.title("Medicine Inventory Management")
        self.geometry("900x600")
        self.configure(padx=PAD_MEDIUM, pady=PAD_MEDIUM, bg=COLOR_BG)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        ttk.Label(
            self,
            text="📦 Inventory Management",
            style="Title.TLabel"
        ).pack(pady=(0, PAD_MEDIUM))
        
        # Notebook (Tabs)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        
        # Create tabs for each category
        categories = [
            ("Dilutions", "DILUTION"),
            ("Mother Tinctures", "Q"),
            ("Biochemic Salts", "BIOCHEMIC"),
            ("Globules", "GLOBULE"),
            ("Complexes", "COMPLEX"),
            ("Nosodes", "NOSODE")
        ]
        
        for tab_name, category in categories:
            tab = self.create_category_tab(notebook, category)
            notebook.add(tab, text=tab_name)
    
    def create_category_tab(self, notebook, category):
        """Create a tab for a specific medicine category."""
        tab = ttk.Frame(notebook, padding=PAD_MEDIUM)
        
        # Search
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill="x", pady=(0, PAD_MEDIUM))
        
        ttk.Label(search_frame, text="Search:", font=FONT_HEADER).pack(side="left", padx=5)
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(side="left")
        
        # Table
        columns = ("Medicine", "Potency", "Form", "Size", "Stock", "Min Level")
        col_config = {
            "Medicine": {"width": 150, "anchor": "w"},
            "Potency": {"width": 80, "anchor": "center"},
            "Form": {"width": 80, "anchor": "center"},
            "Size": {"width": 80, "anchor": "center"},
            "Stock": {"width": 80, "anchor": "center"},
            "Min Level": {"width": 100, "anchor": "center"}
        }
        
        tree = create_table(tab, columns, col_config)
        
        # Load data for this category
        self.load_category_data(tree, category)
        
        return tab
    
    def load_category_data(self, tree, category):
        """Load medicines for a specific category."""
        conn = self.med_db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                m.name,
                v.potency,
                v.form,
                v.bottle_size,
                COALESCE(s.quantity_available, 0),
                v.min_stock_level
            FROM medicine_master m
            JOIN medicine_variants v ON m.id = v.medicine_id
            LEFT JOIN inventory_stock s ON v.id = s.variant_id
            WHERE m.category = ? AND m.is_active = 1
            ORDER BY m.name, v.potency
        """, (category,))
        
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            tree.insert("", "end", values=row)


def show_medicine_store(app):
    """Entry point to show Medicine Store dashboard."""
    app.clear_content()
    MedicineStoreDashboard(app.content_frame, app).pack(fill="both", expand=True)
