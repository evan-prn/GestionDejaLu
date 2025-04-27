"""
Configuration pour l'application de gestion de bibliothèque.

Ce module définit les styles de l'interface graphique, les paramètres de connexion à la base
de données MySQL, ainsi que les configurations SMTP pour l'envoi d'emails. Les valeurs
sensibles (identifiants, mots de passe) sont chargées depuis des variables d'environnement
via un fichier .env pour des raisons de sécurité, avec des valeurs par défaut pour le
développement.
"""

import os
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

# Styles pour l'interface graphique
STYLES = {
    "bg": "#ECF0F1",              # Couleur de fond principale
    "fg": "#1A2526",              # Couleur du texte principal
    "button_bg": "#4A90E2",       # Couleur de fond des boutons
    "button_fg": "#FFFFFF",       # Couleur du texte des boutons
    "entry_bg": "#F7F7F7",        # Couleur de fond des champs de saisie
    "font_title": ("Helvetica", 20, "bold"),  # Police pour les titres
    "font_label": ("Helvetica", 11),          # Police pour les étiquettes
    "font_button": ("Helvetica", 11, "bold"), # Police pour les boutons
    "card_bg": "#FFFFFF",         # Couleur de fond des cartes
    "card_border": "#E0E0E0",     # Couleur des bordures des cartes
    "highlight": "#4A90E2",       # Couleur des surbrillances
    "order_bg": "#2ECC71",        # Couleur de fond pour les commandes
    "menu_bg": "#E8ECEF",         # Couleur de fond des menus
    "menu_border": "#D3D8DE"      # Couleur des bordures des menus
}

# Configuration SMTP pour l'envoi d'emails
SMTP_CONFIG = {
    "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),  # Serveur SMTP, par défaut Gmail
    "port": int(os.getenv("SMTP_PORT", 587)),          # Port SMTP, converti en entier
    "user": os.getenv("SMTP_USER", "pernot.evan03@gmail.com"),  # Utilisateur SMTP
    "password": os.getenv("SMTP_PASSWORD", "qrhj aemm dyzx hdrl"),  # Mot de passe ou clé d'application
    "sender_name": os.getenv("SMTP_SENDER_NAME", "GestionDejaLu"),  # Nom de l'expéditeur
    "sender_email": os.getenv("SMTP_SENDER_EMAIL", "pernot.evan03@gmail.com"),  # Email de l'expéditeur
}

# Plage pour les prix aléatoires des livres
RANDOM_PRICE_MIN = float(os.getenv("RANDOM_PRICE_MIN", 5.0))  # Prix minimum en euros
RANDOM_PRICE_MAX = float(os.getenv("RANDOM_PRICE_MAX", 50.0))  # Prix maximum en euros

# Configuration de la base de données MySQL
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),          # Hôte de la base de données
    "user": os.getenv("MYSQL_USER", "root"),               # Nom d'utilisateur MySQL
    "password": os.getenv("MYSQL_PASSWORD", ""),           # Mot de passe MySQL (vide par défaut)
    "database": os.getenv("MYSQL_DATABASE", "gestion_dejalu"),  # Nom de la base de données
    "raise_on_warnings": True                              # Lever des exceptions sur les avertissements
}

# Vérification des identifiants MySQL
if not MYSQL_CONFIG["user"] or not MYSQL_CONFIG["password"]:
    import warnings
    warnings.warn(
        "Identifiants MySQL manquants ou incomplets. "
        "Vérifiez les variables MYSQL_USER et MYSQL_PASSWORD dans le fichier .env.",
        UserWarning
    )