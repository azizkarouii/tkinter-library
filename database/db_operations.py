import sqlite3
import hashlib

def init_db():
    conn = sqlite3.connect('biblio.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS utilisateurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        adresse TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        date_naissance TEXT NOT NULL,
        cin TEXT UNIQUE NOT NULL CHECK(length(cin) = 8 AND cin GLOB '[0-9]*'),
        role TEXT NOT NULL CHECK(role IN ('admin', 'bibliothecaire', 'emprunteur'))
        )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS livres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        auteur TEXT NOT NULL,
        annee INTEGER NOT NULL,
        disponible TEXT NOT NULL CHECK(disponible IN ('oui', 'non'))
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emprunts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        livre_id INTEGER NOT NULL,
        emprunteur_id INTEGER NOT NULL,
        date_emprunt TEXT NOT NULL,
        date_retour TEXT NOT NULL,
        duree INTEGER NOT NULL,
        statut TEXT NOT NULL CHECK(statut IN ('en cours', 'terminé', 'en retard')),
        FOREIGN KEY (livre_id) REFERENCES livres(id),
        FOREIGN KEY (emprunteur_id) REFERENCES utilisateurs(id))
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM utilisateurs WHERE role='admin'")
    if cursor.fetchone()[0] == 0:
        hashed_password = hash_password("admin123")
        cursor.execute('''
            INSERT INTO utilisateurs 
            (nom, prenom, adresse, email, password, date_naissance, cin, role) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            ('Admin', 'System', 'Adresse admin', 'admin@bibliotheque.com', 
             hashed_password, '2000-01-01', '12345678', 'admin'))
    
    conn.commit()
    conn.close()

def connect_db():
    return sqlite3.connect('biblio.db')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()