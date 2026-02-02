from ui.login import LoginWindow
from ui.app import MainApp

if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()
    
    if login.logged_in:
        app = MainApp()
        app.mainloop()