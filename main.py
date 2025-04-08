import tkinter as tk
from database.db_operations import init_db
from interfaces.login import LoginWindow

if __name__ == "__main__":
    init_db()
    
    root = tk.Tk()
    login_app = LoginWindow(root)
    root.mainloop()