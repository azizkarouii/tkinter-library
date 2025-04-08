import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from database.db_operations import hash_password, connect_db
from utils.validators import validate_email

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Connexion - Gestion de Bibliothèque")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.root.configure(bg="#f8f9fa")
        
        self.setup_ui()
    
    def setup_ui(self):
        try:
            img = Image.open("login_bg.jpg") if os.path.exists("login_bg.jpg") else None
            if img:
                img = img.resize((400, 100), Image.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(img)
                tk.Label(self.root, image=self.bg_image, bg="#f8f9fa").pack(pady=10)
            else:
                tk.Label(self.root, text="Gestion de Bibliothèque", font=("Arial", 16, "bold"), bg="#f8f9fa").pack(pady=20)
        except Exception as e:
            print(f"Erreur image: {e}")
            tk.Label(self.root, text="Gestion de Bibliothèque", font=("Arial", 16, "bold"), bg="#f8f9fa").pack(pady=20)
        
        login_frame = tk.Frame(self.root, bg="#f8f9fa")
        login_frame.pack(pady=20)
        
        tk.Label(login_frame, text="Email:", font=("Arial", 12), bg="#f8f9fa").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = tk.Entry(login_frame, font=("Arial", 12), width=25)
        self.email_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(login_frame, text="Mot de passe:", font=("Arial", 12), bg="#f8f9fa").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = tk.Entry(login_frame, show="*", font=("Arial", 12), width=25)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(self.root, text="Se connecter", command=self.authenticate, 
                 bg="#007BFF", fg="white", font=("Arial", 12), width=15).pack(pady=10)
        
        self.email_entry.focus_set()
    
    def authenticate(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showwarning("Erreur", "Veuillez remplir tous les champs")
            return
        
        if not validate_email(email):
            messagebox.showwarning("Erreur", "Email invalide")
            return
        
        conn = connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM utilisateurs WHERE email=?", (email,))
            user = cursor.fetchone()
            
            if user and user[5] == hash_password(password):
                self.root.destroy()
                self.open_interface_based_on_role(user)
            else:
                messagebox.showerror("Erreur", "Email ou mot de passe incorrect")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue: {str(e)}")
        finally:
            conn.close()
    
    def open_interface_based_on_role(self, user):
        if user[8] == 'admin':
            from interfaces.admin import AdminInterface
            AdminInterface(user)
        elif user[8] == 'bibliothecaire':
            from interfaces.bibliothecaire import BibliothecaireInterface
            BibliothecaireInterface(user)
        else:
            from interfaces.emprunteur import EmprunteurInterface
            EmprunteurInterface(user)