from tkinter import messagebox
import sqlite3
import datetime
import sys
import os

class MedicineDatabaseManager:
    def __init__(self, db_file="clinic_medicine.db"):
        # Ensure we use an absolute path relative to the script location
        # or a specific location. Here, assume relative to CWD or user provided.
        self.db_file = os.path.abspath(db_file)
        self.init_db()

    def get_connection(self):
        """Creates a database connection with foreign key support."""
        try:
            conn = sqlite3.connect(self.db_file)
            conn.execute("PRAGMA foreign_keys = 1")
            return conn
        except sqlite3.Error as e:
            messagebox.showerror("Medicine Database Error", f"Could not connect to medicine database: {e}")
            sys.exit(1)

    def init_db(self):
        """Initializes the medicine database schema if it doesn't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # ---------------------------------------------------------
        # 1. Medicine Master Table
        # Defines WHAT exists (e.g., Arnica, Belladonna)
        # ---------------------------------------------------------
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicine_master (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT CHECK(category IN ('Q', 'DILUTION', 'BIOCHEMIC', 'COMPLEX', 'NOSODE', 'GLOBULE', 'OTHER')) NOT NULL,
                manufacturer TEXT,
                is_active BOOLEAN DEFAULT 1,
                is_restricted BOOLEAN DEFAULT 0,
                notes TEXT
            )
        ''')

        # ---------------------------------------------------------
        # 2. Medicine Variants Table
        # Defines HOW it exists (e.g., Arnica 30C 30ml Liquid)
        # ---------------------------------------------------------
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicine_variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_id INTEGER NOT NULL,
                potency TEXT, -- 6C, 30C, 200C, 1M, Q, etc.
                form TEXT, -- liquid / tablet / globule / ointment
                bottle_size TEXT, -- 30ml, 100ml, 450gm
                unit_type TEXT, -- ml / tablets / pills / gm
                min_stock_level INTEGER DEFAULT 5,
                expiry_date DATE,
                FOREIGN KEY (medicine_id) REFERENCES medicine_master(id) ON DELETE CASCADE
            )
        ''')

        # ---------------------------------------------------------
        # 3. Inventory Stock Table
        # Defines CURRENT state (Quantity Available)
        # ---------------------------------------------------------
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                variant_id INTEGER UNIQUE NOT NULL,
                quantity_available INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (variant_id) REFERENCES medicine_variants(id) ON DELETE CASCADE
            )
        ''')

        # ---------------------------------------------------------
        # 4. Inventory Movements Table
        # Defines HISTORY (Audit Trail)
        # ---------------------------------------------------------
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                variant_id INTEGER NOT NULL,
                movement_type TEXT CHECK(movement_type IN ('IN', 'OUT', 'EXPIRED', 'ADJUST', 'RETURN')),
                quantity INTEGER NOT NULL,
                reference_type TEXT CHECK(reference_type IN ('PURCHASE', 'PRESCRIPTION', 'DISPOSAL', 'ADJUSTMENT')),
                reference_id TEXT, -- Can be prescription ID or Purchase Order ID
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (variant_id) REFERENCES medicine_variants(id) ON DELETE CASCADE
            )
        ''')

        # ---------------------------------------------------------
        # 5. Globule Stock Table
        # Consumables (Global stock, not tied to a specific medicine)
        # ---------------------------------------------------------
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS globule_stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                size INTEGER UNIQUE NOT NULL, -- 20, 30, 40 etc.
                quantity_available INTEGER DEFAULT 0, -- in grams/kg or bottles? Usually grams/bottles.
                min_level INTEGER DEFAULT 10
            )
        ''')

        conn.commit()
        conn.close()

    # --- CRUD Operations for Medicine Master ---

    def create_medicine(self, name, category, manufacturer="", is_restricted=False, notes=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO medicine_master (name, category, manufacturer, is_restricted, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, category, manufacturer, is_restricted, notes))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            # messagebox.showerror("Database Error", str(e)) # suppress specific error dialogs from low level
            print(f"Error creating medicine: {e}")
            return None
        finally:
            conn.close()

    def get_medicine_master(self, medicine_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medicine_master WHERE id = ?", (medicine_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def search_medicines(self, query):
        conn = self.get_connection()
        cursor = conn.cursor()
        search_term = f"%{query}%"
        cursor.execute('''
            SELECT * FROM medicine_master 
            WHERE name LIKE ? 
            ORDER BY name ASC
        ''', (search_term,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    # --- CRUD Operations for Variants ---

    def create_variant(self, medicine_id, potency, form, bottle_size, unit_type, min_stock_level=5, expiry_date=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO medicine_variants (medicine_id, potency, form, bottle_size, unit_type, min_stock_level, expiry_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (medicine_id, potency, form, bottle_size, unit_type, min_stock_level, expiry_date))
            variant_id = cursor.lastrowid
            
            # Initialize stock entry for this variant (0 quantity)
            cursor.execute('''
                INSERT OR IGNORE INTO inventory_stock (variant_id, quantity_available)
                VALUES (?, 0)
            ''', (variant_id,))
            
            conn.commit()
            return variant_id
        except sqlite3.Error as e:
            print(f"Error creating variant: {e}")
            return None
        finally:
            conn.close()
            
    def get_variants_for_medicine(self, medicine_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Join with stock to get current quantity
        cursor.execute("""
            SELECT v.*, s.quantity_available 
            FROM medicine_variants v
            LEFT JOIN inventory_stock s ON v.id = s.variant_id
            WHERE v.medicine_id = ?
        """, (medicine_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    # --- Inventory Operations ---

    def add_stock(self, variant_id, quantity, reference_type="PURCHASE", reference_id=None, notes=""):
        """Adds stock to a variant and logs movement."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Update current stock
            cursor.execute('''
                UPDATE inventory_stock 
                SET quantity_available = quantity_available + ?, last_updated = CURRENT_TIMESTAMP
                WHERE variant_id = ?
            ''', (quantity, variant_id))
            
            # Log movement
            cursor.execute('''
                INSERT INTO inventory_movements (variant_id, movement_type, quantity, reference_type, reference_id, notes)
                VALUES (?, 'IN', ?, ?, ?, ?)
            ''', (variant_id, quantity, reference_type, reference_id, notes))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding stock: {e}")
            return False
        finally:
            conn.close()

    def deduct_stock(self, variant_id, quantity, reference_type="PRESCRIPTION", reference_id=None, notes=""):
        """Deducts stock from a variant and logs movement. Returns False if insufficient stock."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check current stock first
            cursor.execute("SELECT quantity_available FROM inventory_stock WHERE variant_id = ?", (variant_id,))
            row = cursor.fetchone()
            if not row:
                return False # Variant not initialized
            
            current_qty = row[0]
            if current_qty < quantity:
                return False # Insufficient stock

            # Deduct stock
            cursor.execute('''
                UPDATE inventory_stock 
                SET quantity_available = quantity_available - ?, last_updated = CURRENT_TIMESTAMP
                WHERE variant_id = ?
            ''', (quantity, variant_id))
            
            # Log movement
            cursor.execute('''
                INSERT INTO inventory_movements (variant_id, movement_type, quantity, reference_type, reference_id, notes)
                VALUES (?, 'OUT', ?, ?, ?, ?)
            ''', (variant_id, quantity, reference_type, reference_id, notes))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deducting stock: {e}")
            return False
        finally:
            conn.close()

    def get_low_stock_medicines(self):
        """Returns variants where stock < min_stock_level."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                m.name, 
                v.potency, 
                v.form, 
                s.quantity_available, 
                v.min_stock_level 
            FROM medicine_variants v
            JOIN inventory_stock s ON v.id = s.variant_id
            JOIN medicine_master m ON v.medicine_id = m.id
            WHERE s.quantity_available <= v.min_stock_level
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    # --- Globule Operations ---
    
    def update_globule_stock(self, size, quantity_change): # positive for add, negative for deduct
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if exists
            cursor.execute("SELECT quantity_available FROM globule_stock WHERE size = ?", (size,))
            row = cursor.fetchone()
            
            if row:
                new_qty = row[0] + quantity_change
                if new_qty < 0:
                    return False # Cannot go negative
                cursor.execute("UPDATE globule_stock SET quantity_available = ? WHERE size = ?", (new_qty, size))
            else:
                 if quantity_change < 0:
                     return False # Cannot deduct from non-existent
                 cursor.execute("INSERT INTO globule_stock (size, quantity_available) VALUES (?, ?)", (size, quantity_change))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating globule stock: {e}")
            return False
        finally:
            conn.close()

    def get_globule_stock(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM globule_stock ORDER BY size ASC")
        rows = cursor.fetchall()
        conn.close()
        return rows
