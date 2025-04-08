import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database.db_operations import connect_db, hash_password
import sqlite3
from utils.validators import validate_email, validate_cin, validate_date

class BibliothecaireInterface:
    def __init__(self, user):
        self.user = user
        self.root = tk.Tk()
        self.root.title(f"Interface Bibliothécaire - {user[1]} {user[2]}")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f4f4f4")
        
        self.create_navbar()
        self.create_notebook()
        self.load_initial_data()
        self.root.mainloop()
    
    def create_navbar(self):
        navbar = tk.Frame(self.root, bg="#343a40", height=50)
        navbar.pack(fill="x", padx=10, pady=5)
        
        tk.Label(navbar, text=f"Bibliothécaire: {self.user[1]} {self.user[2]}", 
                fg="white", bg="#343a40", font=("Arial", 12)).pack(side="left", padx=10)
        
        tk.Button(navbar, text="Déconnexion", command=self.logout, 
                 bg="#dc3545", fg="white", font=("Arial", 10)).pack(side="right", padx=10)
    
    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
        
        # Onglet Gestion des Emprunteurs
        self.borrower_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.borrower_frame, text="Gestion des Emprunteurs")
        self.create_borrower_tab()
        
        # Onglet Gestion des Livres
        self.book_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.book_frame, text="Gestion des Livres")
        self.create_book_tab()
        
        # Onglet Gestion des Emprunts
        self.loan_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.loan_frame, text="Gestion des Emprunts")
        self.create_loan_tab()
    
    def create_borrower_tab(self):
        # Frame de saisie
        input_frame = tk.Frame(self.borrower_frame, bg="#f4f4f4")
        input_frame.pack(pady=10, padx=10, fill="x")
        
        # Champs emprunteur
        fields = [
            ("Nom", 0, 0), ("Prénom", 0, 2), ("Adresse", 1, 0),
            ("Email", 2, 0), ("Mot de passe", 2, 2), ("Date Naissance (AAAA-MM-JJ)", 3, 0),
            ("CIN", 3, 2)
        ]
        
        self.borrower_entries = {}
        
        for text, row, col in fields:
            tk.Label(input_frame, text=text+":", bg="#f4f4f4", font=("Arial", 10)).grid(row=row, column=col, padx=5, pady=5, sticky="e")
            entry = tk.Entry(input_frame, font=("Arial", 10))
            entry.grid(row=row, column=col+1, padx=5, pady=5, sticky="w")
            self.borrower_entries[text.lower().split()[0]] = entry
        
        # Boutons
        btn_frame = tk.Frame(input_frame, bg="#f4f4f4")
        btn_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        tk.Button(btn_frame, text="Ajouter Emprunteur", command=self.add_borrower, 
                 bg="#28a745", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        # Tableau des emprunteurs
        table_frame = tk.Frame(self.borrower_frame)
        table_frame.pack(pady=10, padx=10, expand=True, fill="both")
        
        columns = ("ID", "Nom", "Prénom", "Email", "CIN")
        self.borrower_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.borrower_tree.heading(col, text=col)
            self.borrower_tree.column(col, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.borrower_tree.yview)
        self.borrower_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.borrower_tree.pack(expand=True, fill="both")
        
        self.borrower_tree.bind("<<TreeviewSelect>>", self.on_borrower_select)
    
    def create_book_tab(self):
        # Frame de saisie
        input_frame = tk.Frame(self.book_frame, bg="#f4f4f4")
        input_frame.pack(pady=10, padx=10, fill="x")
        
        # Champs livre
        fields = [("Titre", 0, 0), ("Auteur", 0, 2), ("Année", 1, 0)]
        
        self.book_entries = {}
        
        for text, row, col in fields:
            tk.Label(input_frame, text=text+":", bg="#f4f4f4", font=("Arial", 10)).grid(row=row, column=col, padx=5, pady=5, sticky="e")
            entry = tk.Entry(input_frame, font=("Arial", 10))
            entry.grid(row=row, column=col+1, padx=5, pady=5, sticky="w")
            self.book_entries[text.lower()] = entry
        
        # Disponible
        tk.Label(input_frame, text="Disponible:", bg="#f4f4f4", font=("Arial", 10)).grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.disponible_var = tk.StringVar(value="oui")
        ttk.OptionMenu(input_frame, self.disponible_var, "oui", "oui", "non").grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # Boutons
        btn_frame = tk.Frame(input_frame, bg="#f4f4f4")
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        tk.Button(btn_frame, text="Ajouter Livre", command=self.add_book, 
                 bg="#28a745", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Modifier Livre", command=self.update_book, 
                 bg="#17a2b8", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Supprimer Livre", command=self.delete_book, 
                 bg="#dc3545", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
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
        
        self.book_tree.bind("<<TreeviewSelect>>", self.on_book_select)
    
    def create_loan_tab(self):
        # Frame de création d'emprunt
        create_frame = tk.Frame(self.loan_frame, bg="#f4f4f4")
        create_frame.pack(pady=10, padx=10, fill="x")
        
        # Sélection du livre
        tk.Label(create_frame, text="Livre:", bg="#f4f4f4", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.livre_combo = ttk.Combobox(create_frame, font=("Arial", 10), state="readonly")
        self.livre_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Sélection de l'emprunteur
        tk.Label(create_frame, text="Emprunteur:", bg="#f4f4f4", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.emprunteur_combo = ttk.Combobox(create_frame, font=("Arial", 10), state="readonly")
        self.emprunteur_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Durée
        tk.Label(create_frame, text="Durée (jours):", bg="#f4f4f4", font=("Arial", 10)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.duree_entry = tk.Entry(create_frame, font=("Arial", 10))
        self.duree_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Bouton
        tk.Button(create_frame, text="Enregistrer Emprunt", command=self.create_loan, 
                 bg="#28a745", fg="white", font=("Arial", 10)).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Frame de gestion des emprunts
        manage_frame = tk.Frame(self.loan_frame)
        manage_frame.pack(pady=10, padx=10, expand=True, fill="both")
        
        # Boutons de gestion
        btn_frame = tk.Frame(manage_frame, bg="#f4f4f4")
        btn_frame.pack(fill="x", pady=5)
        
        tk.Button(btn_frame, text="Marquer comme retourné", command=self.mark_returned, 
                 bg="#17a2b8", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Actualiser", command=self.load_loans, 
                 bg="#6c757d", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        
        # Tableau des emprunts
        columns = ("ID", "Livre", "Emprunteur", "Date Emprunt", "Date Retour", "Statut")
        self.loan_tree = ttk.Treeview(manage_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.loan_tree.heading(col, text=col)
            self.loan_tree.column(col, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(manage_frame, orient="vertical", command=self.loan_tree.yview)
        self.loan_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.loan_tree.pack(expand=True, fill="both")
    
    def load_initial_data(self):
        self.load_borrowers()
        self.load_books()
        self.load_loans()
        self.update_comboboxes()
    
    def load_borrowers(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, prenom, email, cin FROM utilisateurs WHERE role='emprunteur'")
        rows = cursor.fetchall()
        conn.close()
        
        self.borrower_tree.delete(*self.borrower_tree.get_children())
        for row in rows:
            self.borrower_tree.insert("", "end", values=row)
    
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
            ORDER BY e.date_retour
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        self.loan_tree.delete(*self.loan_tree.get_children())
        for row in rows:
            self.loan_tree.insert("", "end", values=row)
    
    def update_comboboxes(self):
        # Mettre à jour la combobox des livres disponibles
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, titre FROM livres WHERE disponible='oui'")
        livres = cursor.fetchall()
        self.livre_combo['values'] = [f"{livre[0]} - {livre[1]}" for livre in livres]
        
        # Mettre à jour la combobox des emprunteurs
        cursor.execute("SELECT id, nom, prenom FROM utilisateurs WHERE role='emprunteur'")
        emprunteurs = cursor.fetchall()
        self.emprunteur_combo['values'] = [f"{emp[0]} - {emp[1]} {emp[2]}" for emp in emprunteurs]
        conn.close()
    
    def add_borrower(self):
        nom = self.borrower_entries['nom'].get().strip()
        prenom = self.borrower_entries['prénom'].get().strip()
        adresse = self.borrower_entries['adresse'].get().strip()
        email = self.borrower_entries['email'].get().strip()
        password = self.borrower_entries['mot'].get().strip()
        date_naissance = self.borrower_entries['date'].get().strip()
        cin = self.borrower_entries['cin'].get().strip().upper()
        
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
                VALUES (?, ?, ?, ?, ?, ?, ?, 'emprunteur')
            ''', (nom, prenom, adresse, email, hash_password(password), date_naissance, cin))
            
            conn.commit()
            self.load_borrowers()
            self.clear_borrower_entries()
            self.update_comboboxes()
            messagebox.showinfo("Succès", "Emprunteur ajouté avec succès")
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
    
    def on_borrower_select(self, event):
        selected = self.borrower_tree.selection()
        if not selected:
            return
        
        values = self.borrower_tree.item(selected, 'values')
        self.clear_borrower_entries()
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nom, prenom, adresse, email, date_naissance, cin FROM utilisateurs WHERE id=?", (values[0],))
        borrower_data = cursor.fetchone()
        conn.close()
        
        if borrower_data:
            self.borrower_entries['nom'].insert(0, borrower_data[0])
            self.borrower_entries['prénom'].insert(0, borrower_data[1])
            self.borrower_entries['adresse'].insert(0, borrower_data[2])
            self.borrower_entries['email'].insert(0, borrower_data[3])
            self.borrower_entries['date'].insert(0, borrower_data[4])
            self.borrower_entries['cin'].insert(0, borrower_data[5])
    
    def clear_borrower_entries(self):
        for entry in self.borrower_entries.values():
            entry.delete(0, tk.END)
    
    def add_book(self):
        titre = self.book_entries['titre'].get().strip()
        auteur = self.book_entries['auteur'].get().strip()
        annee = self.book_entries['année'].get().strip()
        disponible = self.disponible_var.get()
        
        if not titre or not auteur or not annee:
            messagebox.showwarning("Erreur", "Titre, auteur et année sont obligatoires")
            return
        
        try:
            annee = int(annee)
            if annee < 0 or annee > datetime.now().year:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Erreur", "Année invalide")
            return
        
        conn = connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO livres (titre, auteur, annee, disponible)
                VALUES (?, ?, ?, ?)
            ''', (titre, auteur, annee, disponible))
            
            conn.commit()
            self.load_books()
            self.clear_book_entries()
            self.update_comboboxes()
            messagebox.showinfo("Succès", "Livre ajouté avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")
        finally:
            conn.close()
    
    def update_book(self):
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un livre")
            return
        
        book_id = self.book_tree.item(selected, 'values')[0]
        titre = self.book_entries['titre'].get().strip()
        auteur = self.book_entries['auteur'].get().strip()
        annee = self.book_entries['année'].get().strip()
        disponible = self.disponible_var.get()
        
        if not titre or not auteur or not annee:
            messagebox.showwarning("Erreur", "Titre, auteur et année sont obligatoires")
            return
        
        try:
            annee = int(annee)
            if annee < 0 or annee > datetime.now().year:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Erreur", "Année invalide")
            return
        
        conn = connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE livres 
                SET titre=?, auteur=?, annee=?, disponible=?
                WHERE id=?
            ''', (titre, auteur, annee, disponible, book_id))
            
            conn.commit()
            self.load_books()
            self.clear_book_entries()
            self.update_comboboxes()
            messagebox.showinfo("Succès", "Livre modifié avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")
        finally:
            conn.close()
    
    def delete_book(self):
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un livre")
            return
        
        book_id = self.book_tree.item(selected, 'values')[0]
        
        conn = connect_db()
        cursor = conn.cursor()
        
        try:
            # Vérifier si le livre est emprunté
            cursor.execute("SELECT COUNT(*) FROM emprunts WHERE livre_id=? AND statut='en cours'", (book_id,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Erreur", "Ce livre est actuellement emprunté et ne peut pas être supprimé")
                return
            
            cursor.execute("DELETE FROM livres WHERE id=?", (book_id,))
            conn.commit()
            self.load_books()
            self.clear_book_entries()
            self.update_comboboxes()
            messagebox.showinfo("Succès", "Livre supprimé avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")
        finally:
            conn.close()
    
    def on_book_select(self, event):
        selected = self.book_tree.selection()
        if not selected:
            return
        
        values = self.book_tree.item(selected, 'values')
        self.clear_book_entries()
        
        self.book_entries['titre'].insert(0, values[1])
        self.book_entries['auteur'].insert(0, values[2])
        self.book_entries['année'].insert(0, values[3])
        self.disponible_var.set(values[4])
    
    def clear_book_entries(self):
        for entry in self.book_entries.values():
            entry.delete(0, tk.END)
        self.disponible_var.set("oui")
    
    def create_loan(self):
        livre_selection = self.livre_combo.get()
        emprunteur_selection = self.emprunteur_combo.get()
        duree = self.duree_entry.get().strip()
        
        if not livre_selection or not emprunteur_selection or not duree:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un livre, un emprunteur et spécifier une durée")
            return
        
        try:
            livre_id = int(livre_selection.split(" - ")[0])
            emprunteur_id = int(emprunteur_selection.split(" - ")[0])
            duree = int(duree)
            
            if duree <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Erreur", "Durée invalide (doit être un nombre positif)")
            return
        
        date_emprunt = datetime.now().strftime("%Y-%m-%d")
        date_retour = (datetime.now() + timedelta(days=duree)).strftime("%Y-%m-%d")
        
        conn = connect_db()
        cursor = conn.cursor()
        
        try:
            # Créer l'emprunt
            cursor.execute('''
                INSERT INTO emprunts 
                (livre_id, emprunteur_id, date_emprunt, date_retour, duree, statut)
                VALUES (?, ?, ?, ?, ?, 'en cours')
            ''', (livre_id, emprunteur_id, date_emprunt, date_retour, duree))
            
            # Marquer le livre comme non disponible
            cursor.execute("UPDATE livres SET disponible='non' WHERE id=?", (livre_id,))
            
            conn.commit()
            self.load_loans()
            self.update_comboboxes()
            self.duree_entry.delete(0, tk.END)
            messagebox.showinfo("Succès", "Emprunt enregistré avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")
        finally:
            conn.close()
    
    def mark_returned(self):
        selected = self.loan_tree.selection()
        if not selected:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un emprunt")
            return
        
        loan_id = self.loan_tree.item(selected, 'values')[0]
        statut = self.loan_tree.item(selected, 'values')[5]
        
        if statut != "en cours":
            messagebox.showwarning("Erreur", "Seuls les emprunts en cours peuvent être marqués comme retournés")
            return
        
        conn = connect_db()
        cursor = conn.cursor()
        
        try:
            # Récupérer l'ID du livre
            cursor.execute("SELECT livre_id FROM emprunts WHERE id=?", (loan_id,))
            livre_id = cursor.fetchone()[0]
            
            # Marquer l'emprunt comme terminé
            cursor.execute("UPDATE emprunts SET statut='terminé' WHERE id=?", (loan_id,))
            
            # Marquer le livre comme disponible
            cursor.execute("UPDATE livres SET disponible='oui' WHERE id=?", (livre_id,))
            
            conn.commit()
            self.load_loans()
            self.update_comboboxes()
            messagebox.showinfo("Succès", "Emprunt marqué comme retourné")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")
        finally:
            conn.close()
    
    def logout(self):
        self.root.destroy()
        from interfaces.login import LoginWindow
        root = tk.Tk()
        login_app = LoginWindow(root)
        root.mainloop()