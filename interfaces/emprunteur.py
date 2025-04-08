import tkinter as tk
from tkinter import ttk
from database.db_operations import connect_db

class EmprunteurInterface:
    def __init__(self, user):
        self.user = user
        self.root = tk.Tk()
        self.root.title(f"Interface Emprunteur - {user[1]} {user[2]}")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f4f4f4")
        
        self.create_navbar()
        self.create_notebook()
        self.load_initial_data()
        self.root.mainloop()
    
    def create_navbar(self):
        navbar = tk.Frame(self.root, bg="#343a40", height=50)
        navbar.pack(fill="x", padx=10, pady=5)
        
        tk.Label(navbar, text=f"Emprunteur: {self.user[1]} {self.user[2]}", 
                fg="white", bg="#343a40", font=("Arial", 12)).pack(side="left", padx=10)
        
        tk.Button(navbar, text="Déconnexion", command=self.logout, 
                 bg="#dc3545", fg="white", font=("Arial", 10)).pack(side="right", padx=10)
    
    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
        
        # Onglet Mes Emprunts
        self.current_loans_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.current_loans_frame, text="Mes Emprunts en Cours")
        self.create_current_loans_tab()
        
        # Onglet Historique
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="Mon Historique")
        self.create_history_tab()
    
    def create_current_loans_tab(self):
        # Tableau des emprunts en cours
        table_frame = tk.Frame(self.current_loans_frame)
        table_frame.pack(pady=10, padx=10, expand=True, fill="both")
        
        columns = ("ID", "Livre", "Date Emprunt", "Date Retour")
        self.current_loans_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.current_loans_tree.heading(col, text=col)
            self.current_loans_tree.column(col, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.current_loans_tree.yview)
        self.current_loans_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.current_loans_tree.pack(expand=True, fill="both")
    
    def create_history_tab(self):
        # Tableau de l'historique
        table_frame = tk.Frame(self.history_frame)
        table_frame.pack(pady=10, padx=10, expand=True, fill="both")
        
        columns = ("ID", "Livre", "Date Emprunt", "Date Retour", "Statut")
        self.history_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.history_tree.pack(expand=True, fill="both")
    
    def load_initial_data(self):
        self.load_current_loans()
        self.load_history()
    
    def load_current_loans(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.id, l.titre, e.date_emprunt, e.date_retour
            FROM emprunts e
            JOIN livres l ON e.livre_id = l.id
            WHERE e.emprunteur_id=? AND e.statut='en cours'
            ORDER BY e.date_retour
        ''', (self.user[0],))
        rows = cursor.fetchall()
        conn.close()
        
        self.current_loans_tree.delete(*self.current_loans_tree.get_children())
        for row in rows:
            self.current_loans_tree.insert("", "end", values=row)
    
    def load_history(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.id, l.titre, e.date_emprunt, e.date_retour, e.statut
            FROM emprunts e
            JOIN livres l ON e.livre_id = l.id
            WHERE e.emprunteur_id=? AND e.statut!='en cours'
            ORDER BY e.date_retour DESC
        ''', (self.user[0],))
        rows = cursor.fetchall()
        conn.close()
        
        self.history_tree.delete(*self.history_tree.get_children())
        for row in rows:
            self.history_tree.insert("", "end", values=row)
    
    def logout(self):
        self.root.destroy()
        from interfaces.login import LoginWindow
        root = tk.Tk()
        login_app = LoginWindow(root)
        root.mainloop()