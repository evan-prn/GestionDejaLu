#config.py

"""
Configuration pour l'application de gestion de bibliothèque.

Ce module contient les styles pour l'interface graphique et les paramètres de connexion
à la base de données MySQL. Les configurations sensibles (comme les identifiants MySQL)
devraient être externalisées dans des variables d'environnement en production.
"""

import os
from dotenv import load_dotenv

load_dotenv()

STYLES = {
    "bg": "#ECF0F1",
    "fg": "#1A2526",
    "button_bg": "#4A90E2",
    "button_fg": "#FFFFFF",
    "entry_bg": "#F7F7F7",
    "font_title": ("Helvetica", 20, "bold"),
    "font_label": ("Helvetica", 11),
    "font_button": ("Helvetica", 11, "bold"),
    "card_bg": "#FFFFFF",
    "card_border": "#E0E0E0",
    "highlight": "#4A90E2",
    "order_bg": "#2ECC71",
    "menu_bg": "#E8ECEF",
    "menu_border": "#D3D8DE"
}

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "gestion_dejalu"),
    "raise_on_warnings": True
}

# Vérification améliorée des identifiants
if not MYSQL_CONFIG["user"] or not MYSQL_CONFIG["password"]:
    import warnings
    warnings.warn(
        "Identifiants MySQL manquants ou incomplets. Vérifiez MYSQL_USER et MYSQL_PASSWORD dans .env.",
        UserWarning
    )