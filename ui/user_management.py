import tkinter as tk
from tkinter import ttk, messagebox
from database.database import DatabaseManager
from config.config import APP_TITLE, COLOR_BG, DB_NAME

class UserManagementWindow(tk.Toplevel):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.title(f"User Management - {APP_TITLE}")
        self.geometry("450x400")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)
        
        self.current_user = current_user
        self.db = DatabaseManager(DB_NAME)
        
        self.center_window()
        self.create_widgets()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill="both")
        
        # Title
        title_label = ttk.Label(main_frame, text="User Management", font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill="both")
        
        # Change Password Tab
        change_pass_frame = ttk.Frame(notebook, padding=10)
        notebook.add(change_pass_frame, text="Change Password")
        self.create_change_password_tab(change_pass_frame)
        
        # Add User Tab
        add_user_frame = ttk.Frame(notebook, padding=10)
        notebook.add(add_user_frame, text="Add New User")
        self.create_add_user_tab(add_user_frame)

    def create_change_password_tab(self, parent):
        # Current Password
        ttk.Label(parent, text="Current Password:").grid(row=0, column=0, sticky="w", pady=5)
        self.current_pass_entry = ttk.Entry(parent, show="*", width=30)
        self.current_pass_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # New Password
        ttk.Label(parent, text="New Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.new_pass_entry = ttk.Entry(parent, show="*", width=30)
        self.new_pass_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Confirm New Password
        ttk.Label(parent, text="Confirm Password:").grid(row=2, column=0, sticky="w", pady=5)
        self.confirm_pass_entry = ttk.Entry(parent, show="*", width=30)
        self.confirm_pass_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Change Button
        change_btn = ttk.Button(parent, text="Change Password", command=self.change_password)
        change_btn.grid(row=3, column=0, columnspan=2, pady=20)

    def create_add_user_tab(self, parent):
        # Username
        ttk.Label(parent, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.new_username_entry = ttk.Entry(parent, width=30)
        self.new_username_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(parent, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.new_user_pass_entry = ttk.Entry(parent, show="*", width=30)
        self.new_user_pass_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Confirm Password
        ttk.Label(parent, text="Confirm Password:").grid(row=2, column=0, sticky="w", pady=5)
        self.confirm_new_pass_entry = ttk.Entry(parent, show="*", width=30)
        self.confirm_new_pass_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Role (for future use)
        ttk.Label(parent, text="Role:").grid(row=3, column=0, sticky="w", pady=5)
        self.role_var = tk.StringVar(value="admin")
        role_combo = ttk.Combobox(parent, textvariable=self.role_var, values=["admin"], state="readonly", width=27)
        role_combo.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Add Button
        add_btn = ttk.Button(parent, text="Add User", command=self.add_user)
        add_btn.grid(row=4, column=0, columnspan=2, pady=20)

    def change_password(self):
        current_pass = self.current_pass_entry.get()
        new_pass = self.new_pass_entry.get()
        confirm_pass = self.confirm_pass_entry.get()
        
        if not current_pass or not new_pass or not confirm_pass:
            messagebox.showwarning("Warning", "All fields are required.")
            return
        
        if new_pass != confirm_pass:
            messagebox.showerror("Error", "New passwords do not match.")
            return
        
        if len(new_pass) < 4:
            messagebox.showwarning("Warning", "Password must be at least 4 characters long.")
            return
        
        if self.db.change_password(self.current_user, current_pass, new_pass):
            messagebox.showinfo("Success", "Password changed successfully!")
            self.clear_change_password_fields()
        else:
            messagebox.showerror("Error", "Failed to change password. Check your current password.")

    def add_user(self):
        username = self.new_username_entry.get().strip()
        password = self.new_user_pass_entry.get()
        confirm_pass = self.confirm_new_pass_entry.get()
        role = self.role_var.get()
        
        if not username or not password or not confirm_pass:
            messagebox.showwarning("Warning", "All fields are required.")
            return
        
        if password != confirm_pass:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        
        if len(password) < 4:
            messagebox.showwarning("Warning", "Password must be at least 4 characters long.")
            return
        
        if self.db.add_user(username, password, role):
            messagebox.showinfo("Success", f"User '{username}' added successfully!")
            self.clear_add_user_fields()
        else:
            messagebox.showerror("Error", "Failed to add user. Username may already exist.")

    def clear_change_password_fields(self):
        self.current_pass_entry.delete(0, tk.END)
        self.new_pass_entry.delete(0, tk.END)
        self.confirm_pass_entry.delete(0, tk.END)

    def clear_add_user_fields(self):
        self.new_username_entry.delete(0, tk.END)
        self.new_user_pass_entry.delete(0, tk.END)
        self.confirm_new_pass_entry.delete(0, tk.END)