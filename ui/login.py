import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
from database.database import DatabaseManager
from config.config import APP_TITLE, COLOR_BG

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Login - {APP_TITLE}")
        self.geometry("350x300")
        self.resizable(False, False)
        sv_ttk.set_theme("light")
        self.configure(bg=COLOR_BG)
        
        # Center the window
        self.center_window()
        
        self.db = DatabaseManager("clinic_data.db")
        self.logged_in = False
        self.logged_in_user = None
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
        title_label = ttk.Label(main_frame, text="ClinicManager Pro", font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Please log in to continue", font=("Segoe UI", 10))
        subtitle_label.pack(pady=(0, 20))

        # Username
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(username_frame, text="Username:").pack(side="left", pady=(0, 5))
        self.username_entry = ttk.Entry(username_frame, width=30)
        self.username_entry.pack(side="left", padx=(5, 0), pady=(0, 10))
        self.username_entry.focus()

        # Password
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill="x")
        
        ttk.Label(password_frame, text="Password:").pack(side="left", pady=(0, 5))
        self.password_entry = ttk.Entry(password_frame, show="*", width=30)
        self.password_entry.pack(side="left", padx=(5, 0), pady=(0, 20))
        
        # Login button
        login_btn = ttk.Button(main_frame, text="Login", command=self.login, width=20)
        login_btn.pack()
        
        # Bind Enter key to login
        self.bind('<Return>', lambda e: self.login())

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Warning", "Please enter both username and password.")
            return
        
        if self.db.verify_login(username, password):
            self.logged_in = True
            self.logged_in_user = username
            self.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            self.password_entry.delete(0, tk.END)
            self.username_entry.focus()