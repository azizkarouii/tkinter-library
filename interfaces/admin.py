import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from database.db_operations import connect_db, hash_password
from utils.validators import validate_email, validate_cin, validate_date

class AdminInterface:
    def __init__(self, user):
        self.user = user
        self.root = tk.Tk()
        self.root.title(f"Interface Admin - {user[1]} {user[2]}")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f4f4f4")
        
        self.create_navbar()
        self.create_notebook()
        self.load_initial_data()
        self.root.mainloop()
    
    def create_navbar(self):
        navbar = tk.Frame(self.root, bg="#343a40", height=50)
        navbar.pack(fill="x", padx=10, pady=5)
        
        tk.Label(navbar, text=f"Admin: {self.user[1]} {self.user[2]}", 
                fg="white", bg="#343a40", font=("Arial", 12)).pack(side="left", padx=10)
        
        tk.Button(navbar, text="Déconnexion", command=self.logout, 
                 bg="#dc3545", fg="white", font=("Arial", 10)).pack(side="right", padx=10)
    
    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
        
        # Onglet Gestion des Utilisateurs
        self.user_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.user_frame, text="Gestion des Utilisateurs")
        self.create_user_tab()
        
        # Onglet Visualisation des Livres
        self.book_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.book_frame, text="Visualisation des Livres")
        self.create_book_view_tab()
        
        # Onglet Visualisation des Emprunts
        self.loan_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.loan_frame, text="Visualisation des Emprunts")
        self.create_loan_view_tab()
    
    def create_user_tab(self):
        # Frame de saisie
        input_frame = tk.Frame(self.user_frame, bg="#f4f4f4")
        input_frame.pack(pady=10, padx=10, fill="x")
        
        # Champs utilisateur
        fields = [
            ("Nom", 0, 0), ("Prénom", 0, 2), ("Adresse", 1, 0),
            ("Email", 2, 0), ("Mot de passe", 2, 2), ("Date Naissance (AAAA-MM-JJ)", 3, 0),
            ("CIN", 3, 2), ("Rôle", 4, 0)
        ]
        
        self.user_entries = {}
        
        for text, row, col in fields:
            tk.Label(input_frame, text=text+":", bg="#f4f4f4", font=("Arial", 10)).grid(row=row, column=col, padx=5, pady=5, sticky="e")
            if text == "Rôle":
                self.role_var = tk.StringVar(value="emprunteur")
                ttk.OptionMenu(input_frame, self.role_var, "emprunteur", "emprunteur", "bibliothecaire").grid(row=row, column=col+1, padx=5, pady=5, sticky="w")
            else:
                entry = tk.Entry(input_frame, font=("Arial", 10))
                entry.grid(row=row, column=col+1, padx=5, pady=5, sticky="w")
                self.user_entries[text.lower().split()[0]] = entry
        
        # Boutons
        btn_frame = tk.Frame(input_frame, bg="#f4f4f4")
        btn_frame.grid(row=5, column=0, columnspan=4, pady=10)
        
        tk.Button(btn_frame, text="Ajouter Utilisateur", command=self.add_user, 
                 bg="#28a745", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Supprimer Utilisateur", command=self.delete_user, 
                 bg="#dc3545", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        # Tableau des utilisateurs
        table_frame = tk.Frame(self.user_frame)
        table_frame.pack(pady=10, padx=10, expand=True, fill="both")
        
        columns = ("ID", "Nom", "Prénom", "Email", "CIN", "Rôle")
        self.user_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.user_tree.pack(expand=True, fill="both")
        
        self.user_tree.bind("<<TreeviewSelect>>", self.on_user_select)
    
    def create_book_view_tab(self):
        # Tableau des livres
        table_frame = tk.Frame(self.book_frame)
        table_frame.pack(pady=10, padx=10, expand=True, fill="both")
        
        columns = ("ID", "Titre", "Auteur", "Année", "Disponible")
        self.book_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.book_tree.pack(expand=True, fill="both")
    
    def create_loan_view_tab(self):
        # Tableau des emprunts
        table_frame = tk.Frame(self.loan_frame)
        table_frame.pack(pady=10, padx=10, expand=True, fill="both")
        
        columns = ("ID", "Livre", "Emprunteur", "Date Emprunt", "Date Retour", "Statut")
        self.loan_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.loan_tree.heading(col, text=col)
            self.loan_tree.column(col, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.loan_tree.yview)
        self.loan_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.loan_tree.pack(expand=True, fill="both")
    
    def load_initial_data(self):
        self.load_users()
        self.load_books()
        self.load_loans()
    
    def load_users(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, prenom, email, cin, role FROM utilisateurs")
        rows = cursor.fetchall()
        conn.close()
        
        self.user_tree.delete(*self.user_tree.get_children())
        for row in rows:
            self.user_tree.insert("", "end", values=row)
    
    def load_books(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, titre, auteur, annee, disponible FROM livres")
        rows = cursor.fetchall()
        conn.close()
        
        self.book_tree.delete(*self.book_tree.get_children())
        for row in rows:
            self.book_tree.insert("", "end", values=row)
    
    def load_loans(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.id, l.titre, u.nom || ' ' || u.prenom, e.date_emprunt, e.date_retour, e.statut
            FROM emprunts e
            JOIN livres l ON e.livre_id = l.id
            JOIN utilisateurs u ON e.emprunteur_id = u.id
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        self.loan_tree.delete(*self.loan_tree.get_children())
        for row in rows:
            self.loan_tree.insert("", "end", values=row)
    
    def add_user(self):
        nom = self.user_entries['nom'].get().strip()
        prenom = self.user_entries['prénom'].get().strip()
        adresse = self.user_entries['adresse'].get().strip()
        email = self.user_entries['email'].get().strip()
        password = self.user_entries['mot'].get().strip()
        date_naissance = self.user_entries['date'].get().strip()
        cin = self.user_entries['cin'].get().strip().upper()
        role = self.role_var.get()
        
        # Validation des champs
        if not all([nom, prenom, adresse, email, password, date_naissance, cin]):
            messagebox.showwarning("Erreur", "Tous les champs sont obligatoires")
            return
        
        if not validate_email(email):
            messagebox.showwarning("Erreur", "Email invalide")
            return
        
        if not validate_cin(cin):
            messagebox.showwarning("Erreur", "CIN invalide (doit contenir exactement 8 chiffres)")
            return
        
        if not validate_date(date_naissance):
            messagebox.showwarning("Erreur", "Date de naissance invalide (format: AAAA-MM-JJ)")
            return
        
        conn = connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO utilisateurs 
                (nom, prenom, adresse, email, password, date_naissance, cin, role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nom, prenom, adresse, email, hash_password(password), date_naissance, cin, role))
            
            conn.commit()
            self.load_users()
            self.clear_user_entries()
            messagebox.showinfo("Succès", "Utilisateur ajouté avec succès")
        except sqlite3.IntegrityError as e:
            if "email" in str(e):
                messagebox.showerror("Erreur", "Cet email est déjà utilisé")
            elif "cin" in str(e):
                messagebox.showerror("Erreur", "Ce CIN est déjà utilisé")
            else:
                messagebox.showerror("Erreur", f"Erreur de base de données: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")
        finally:
            conn.close()
    
    def delete_user(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un utilisateur")
            return
        
        user_id = self.user_tree.item(selected, 'values')[0]
        
        if user_id == str(self.user[0]):
            messagebox.showerror("Erreur", "Vous ne pouvez pas supprimer votre propre compte")
            return
        
        conn = connect_db()
        cursor = conn.cursor()
        
        try:
            # Vérifier si l'utilisateur a des emprunts en cours
            cursor.execute("SELECT COUNT(*) FROM emprunts WHERE emprunteur_id=? AND statut='en cours'", (user_id,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Erreur", "Cet utilisateur a des emprunts en cours et ne peut pas être supprimé")
                return
            
            cursor.execute("DELETE FROM utilisateurs WHERE id=?", (user_id,))
            conn.commit()
            self.load_users()
            self.clear_user_entries()
            messagebox.showinfo("Succès", "Utilisateur supprimé avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")
        finally:
            conn.close()
    
    def on_user_select(self, event):
        selected = self.user_tree.selection()
        if not selected:
            return
        
        values = self.user_tree.item(selected, 'values')
        self.clear_user_entries()
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nom, prenom, adresse, email, date_naissance, cin, role FROM utilisateurs WHERE id=?", (values[0],))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            self.user_entries['nom'].insert(0, user_data[0])
            self.user_entries['prénom'].insert(0, user_data[1])
            self.user_entries['adresse'].insert(0, user_data[2])
            self.user_entries['email'].insert(0, user_data[3])
            self.user_entries['date'].insert(0, user_data[4])
            self.user_entries['cin'].insert(0, user_data[5])
            self.role_var.set(user_data[6])
    
    def clear_user_entries(self):
        for entry in self.user_entries.values():
            entry.delete(0, tk.END)
        self.role_var.set("emprunteur")
    
    def logout(self):
        self.root.destroy()
        from interfaces.login import LoginWindow
        root = tk.Tk()
        login_app = LoginWindow(root)
        root.mainloop()