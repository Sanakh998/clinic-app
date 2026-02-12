import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
import os
from utils.resource_path import resource_path
from database.database import DatabaseManager
from ui.styles import setup_styles
from utils.placeholder_entry import PlaceholderEntry
from config.config import APP_TITLE, COLOR_BG, DB_NAME

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Login - {APP_TITLE}")
        # self.geometry("350x300")
        self.geometry("420x420")
        self.resizable(False, False)
        sv_ttk.set_theme("light")
        self.configure(bg=COLOR_BG)
        
        self.style = ttk.Style()
        setup_styles(self.style)
        
        # Set Window Icon
        icon_path = resource_path("assets/clinic.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"Error loading login window icon: {e}")

        # Center the window
        self.center_window()
        
        self.db = DatabaseManager(DB_NAME)
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

        # Center container
        container = ttk.Frame(self, style="TFrame")
        container.pack(expand=True)

        # Card
        card = ttk.Frame(container, style="Card.TFrame", padding=30)
        card.pack()

        # App Title (use style)
        ttk.Label(
            card,
            text="Clinic Manager Pro",
            style="Title.TLabel"
        ).pack(pady=(0, 5))

        ttk.Label(
            card,
            text="Please log in to continue",
            style="Muted.TLabel"
        ).pack(pady=(5, 20))

        # Username
        self.username_entry = PlaceholderEntry(
            card,
            placeholder="Enter username",
            width=40
        )
        self.username_entry.pack(pady=(0, 12), ipady=5)
        self.username_entry.focus()

        # Password
        self.password_entry = PlaceholderEntry(
            card,
            placeholder="Enter password",
            show="*",
            width=40
        )
        self.password_entry.pack(pady=(0, 20), ipady=5)

        # Login Button
        login_btn = ttk.Button(
            card,
            text="Login",
            command=self.login,
            style="Accent.TButton"
        )
        login_btn.pack(fill="x", ipady=5)

        # Enter key binding
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
            self.password_entry.focus()
