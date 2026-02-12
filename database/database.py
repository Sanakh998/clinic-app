from tkinter import messagebox
import sqlite3
import datetime
import csv
import sys
import hashlib

# ==========================================
# DATABASE MANAGER
# ==========================================
class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file
        self.init_db()

    def get_connection(self):
        """Creates a database connection with foreign key support."""
        try:
            conn = sqlite3.connect(self.db_file)
            conn.execute("PRAGMA foreign_keys = 1")
            return conn
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not connect to database: {e}")
            sys.exit(1)

    def init_db(self):
        """Initializes the database schema if it doesn't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default user if not exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            default_hash = hashlib.sha256("admin".encode()).hexdigest()
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", default_hash))
        # Patients Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                age INTEGER,
                gender TEXT,
                address TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Visits Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                complaints TEXT,
                medicine TEXT,
                fees INTEGER,
                remarks TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id) ON DELETE CASCADE
            )
        ''')
        
        # Medicines Table (Inventory)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                times_used INTEGER DEFAULT 0,
                last_used DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ============================================
    # USER AUTHENTICATION
    # ============================================

    def verify_login(self, username, password):
        """Verify user login credentials."""
        conn = self.get_connection()
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        return user is not None

    def change_password(self, username, old_password, new_password):
        """Change user password after verifying old password."""
        if not self.verify_login(username, old_password):
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        new_hash = hashlib.sha256(new_password.encode()).hexdigest()
        try:
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, username))
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()

    def add_user(self, username, password, role='admin'):
        """Add a new user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, password_hash, role))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Username already exists
            return False
        except sqlite3.Error:
            return False
        finally:
            conn.close()
            
    # =====================================
    # PATIENT OPERATIONS
    # =====================================

    def add_patient(self, name, phone, age, gender, address, notes):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO patients (name, phone, age, gender, address, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, phone, age, gender, address, notes))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
            return None
        finally:
            conn.close()

    def update_patient(self, p_id, name, phone, age, gender, address, notes):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE patients 
                SET name=?, phone=?, age=?, gender=?, address=?, notes=?
                WHERE patient_id=?
            ''', (name, phone, age, gender, address, notes, p_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
            return False
        finally:
            conn.close()

    def delete_patient(self, p_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM patients WHERE patient_id = ?', (p_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
            return False
        finally:
            conn.close()

    def get_recent_patients(self, limit=15):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients ORDER BY created_at DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_recent_activity(self, limit=15):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                v.visit_date,
                p.name,
                p.gender,
                p.age,
                v.complaints,
                p.patient_id
            FROM visits v
            JOIN patients p ON v.patient_id = p.patient_id
            ORDER BY v.visit_date DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_all_patients(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients ORDER BY patient_id DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_new_patients_today(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        today = datetime.date.today().strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT COUNT(*)
            FROM patients
            WHERE DATE(created_at) = ?
        """, (today,))

        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_total_patients_count(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM patients")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def search_patients(self, query):
        conn = self.get_connection()
        cursor = conn.cursor()
        search_term = f"%{query}%"
        cursor.execute('''
            SELECT * FROM patients 
            WHERE name LIKE ? OR phone LIKE ? 
            ORDER BY name ASC
        ''', (search_term, search_term))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_patient_by_id(self, p_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients WHERE patient_id = ?', (p_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    # ============================================
    # MEDICINE OPERATIONS
    # ============================================

    def add_medicine(self, name, description=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO medicines (name, description)
                VALUES (?, ?)
            """, (name, description))
            conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
            return False
        finally:
            conn.close()

    def update_medicine(self, m_id, name, description):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE medicines
                SET name = ?, description = ?
                WHERE medicine_id = ?
            """, (name, description, m_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
            return False
        finally:
            conn.close()

    def delete_medicine(self, m_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM medicines WHERE medicine_id = ?",
                (m_id,)
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
            return False
        finally:
            conn.close()

    def get_all_medicines(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT medicine_id, name, description, times_used, last_used
            FROM medicines
            ORDER BY times_used DESC, name ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def search_medicines(self, query):
        conn = self.get_connection()
        cursor = conn.cursor()
        search_term = f"%{query}%"
        cursor.execute("""
            SELECT medicine_id, name, description, times_used, last_used
            FROM medicines
            WHERE name LIKE ?
            ORDER BY times_used DESC
        """, (search_term,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def create_or_increment_medicine(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT medicine_id FROM medicines WHERE name = ?",
                (name,)
            )
            result = cursor.fetchone()

            if result:
                medicine_id = result[0]
                cursor.execute("""
                    UPDATE medicines
                    SET times_used = times_used + 1,
                        last_used = CURRENT_TIMESTAMP
                    WHERE medicine_id = ?
                """, (medicine_id,))
            else:
                cursor.execute("""
                    INSERT INTO medicines (name, times_used, last_used)
                    VALUES (?, 1, CURRENT_TIMESTAMP)
                """, (name,))

            conn.commit()
            return True

        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
            return False

        finally:
            conn.close()


    # ============================================
    # VISIT OPERATIONS
    # ============================================

    def add_visit(self, patient_id, complaints, medicine, fees, remarks, date_str):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO visits (patient_id, complaints, medicine, fees, remarks, visit_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (patient_id, complaints, medicine, fees, remarks, date_str))
            conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
            return False
        finally:
            conn.close()

    def update_visit(self, visit_id, complaints, medicine, fees, remarks, date_str):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE visits 
                SET complaints=?, medicine=?, fees=?, remarks=?, visit_date=?
                WHERE visit_id=?
            ''', (complaints, medicine, fees, remarks, date_str, visit_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
            return False
        finally:
            conn.close()

    def get_visits(self, patient_id, limit=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        sql = '''
            SELECT * FROM visits 
            WHERE patient_id = ? 
            ORDER BY visit_date DESC
        '''
        if limit:
            sql += f" LIMIT {limit}"
            
        cursor.execute(sql, (patient_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_all_visits_with_patient(self):
        """
        Returns all visits with patient name.
        Order: latest visit first
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                v.visit_id,
                v.patient_id,
                v.visit_date,
                v.complaints,
                v.medicine,
                v.fees,
                v.remarks,
                p.name
            FROM visits v
            JOIN patients p ON v.patient_id = p.patient_id
            ORDER BY v.visit_date DESC
        """)

        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_visits_by_date_range(self, start_date, end_date):
        """
        start_date, end_date: 'YYYY-MM-DD'
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                v.visit_id,
                v.patient_id,
                v.visit_date,
                v.complaints,
                v.medicine,
                v.fees,
                v.remarks,
                p.name
            FROM visits v
            JOIN patients p ON v.patient_id = p.patient_id
            WHERE DATE(v.visit_date) BETWEEN ? AND ?
            ORDER BY v.visit_date DESC
        """, (start_date, end_date))

        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_today_visits(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        today = datetime.date.today().strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT 
                visits.visit_id,
                visits.patient_id,
                visits.visit_date,
                visits.complaints,
                visits.medicine,
                visits.fees,
                visits.remarks,
                patients.name
            FROM visits
            JOIN patients ON visits.patient_id = patients.patient_id
            WHERE DATE(visits.visit_date) = ?
            ORDER BY visits.visit_date DESC
        """, (today,))

        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def delete_visit(self, visit_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM visits WHERE visit_id = ?', (visit_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
            return False
        finally:
            conn.close()
    
    def get_visits_count_map(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT patient_id, COUNT(*) 
            FROM visits 
            GROUP BY patient_id
        """)
        rows = cursor.fetchall()
        conn.close()
        return {pid: cnt for pid, cnt in rows}

    # ============================================
    # STATISTICS & REPORTS
    # ============================================

    def get_today_earnings(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        today = datetime.date.today().strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT SUM(fees)
            FROM visits
            WHERE DATE(visit_date) = ?
        """, (today,))

        total = cursor.fetchone()[0]
        conn.close()
        return total or 0
    
    def get_month_earnings(self, year, month):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT SUM(fees)
            FROM visits
            WHERE strftime('%Y', visit_date) = ?
            AND strftime('%m', visit_date) = ?
        """, (str(year), f"{month:02d}"))

        total = cursor.fetchone()[0]
        conn.close()
        return total or 0

    def get_earnings_by_date_range(self, start_date, end_date):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT SUM(fees)
            FROM visits
            WHERE DATE(visit_date) BETWEEN ? AND ?
        """, (start_date, end_date))

        total = cursor.fetchone()[0]
        conn.close()
        return total or 0

    def get_visits_by_date_range(self, start_date, end_date):
        """
        start_date, end_date: 'YYYY-MM-DD'
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                v.visit_id,
                v.patient_id,
                v.visit_date,
                v.complaints,
                v.medicine,
                v.fees,
                v.remarks,
                p.name
            FROM visits v
            JOIN patients p ON v.patient_id = p.patient_id
            WHERE DATE(v.visit_date) BETWEEN ? AND ?
            ORDER BY v.visit_date DESC
        """, (start_date, end_date))

        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_total_earnings(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(fees) FROM visits")
        total = cursor.fetchone()[0]

        conn.close()
        return total or 0

    # ===========================================
    # DATA EXPORT
    # ===========================================

    def export_patients_csv(self, filepath):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM patients")
            rows = cursor.fetchall()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Phone', 'Age', 'Gender', 'Address', 'Notes', 'Created At'])
                writer.writerows(rows)
            return True
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
            return False
        finally:
            conn.close()
