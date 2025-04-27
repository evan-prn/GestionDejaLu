"""Module pour la gestion des commandes dans la base de données.

Ce module fournit des fonctions pour valider les ISBN, générer des prix aléatoires,
et enregistrer des commandes dans une base de données MySQL via la classe Database.
"""

from database import Database  # Classe pour gérer les connexions à la base de données
import logging
import random
from config import RANDOM_PRICE_MIN, RANDOM_PRICE_MAX  # Bornes pour les prix aléatoires
import mysql.connector  # Ajout explicite pour la gestion des erreurs MySQL

# Initialisation du logger pour ce module
logger = logging.getLogger(__name__)

def validate_isbn(isbn: str) -> bool:
    """Valide le format d'un ISBN (10 ou 13 chiffres).

    Supprime les tirets et espaces de l'ISBN, puis vérifie s'il contient uniquement
    des chiffres et si sa longueur est correcte (10 ou 13).

    Args:
        isbn (str): Numéro ISBN à valider.

    Returns:
        bool: True si l'ISBN est valide, False sinon (incluant le cas où isbn est None ou vide).
    """
    if not isbn:  # Vérifie si l'ISBN est None ou vide
        return False
    isbn_clean = isbn.replace("-", "").replace(" ", "")  # Nettoyage des caractères non numériques
    return isbn_clean.isdigit() and len(isbn_clean) in (10, 13)

def generate_random_price() -> float:
    """Génère un prix aléatoire pour un livre dans une plage définie.

    Utilise les constantes RANDOM_PRICE_MIN et RANDOM_PRICE_MAX importées depuis config.

    Returns:
        float: Prix aléatoire arrondi à 2 décimales, compris entre RANDOM_PRICE_MIN et RANDOM_PRICE_MAX.
    """
    return round(random.uniform(RANDOM_PRICE_MIN, RANDOM_PRICE_MAX), 2)

def enregistrer_commande(client_id: int, livres: list) -> bool:
    """Enregistre une commande pour un client dans la base de données.

    Vérifie l'existence du client, valide les ISBN des livres, génère des prix si nécessaire,
    et insère les informations dans la table 'commandes'.

    Args:
        client_id (int): Identifiant unique du client.
        livres (list): Liste d'objets Livre à inclure dans la commande.

    Returns:
        bool: True si la commande est enregistrée avec succès, False en cas d'échec.

    Raises:
        ValueError: Si la conversion du prix en float échoue.
        mysql.connector.Error: Si une erreur MySQL survient lors de l'accès à la base de données.
    """
    if not client_id or not livres:
        logger.warning("Client ID ou liste de livres manquante pour la commande.")
        return False

    try:
        with Database.get_connection() as conn:  # Connexion à la base de données avec gestion automatique
            cursor = conn.cursor()
            # Vérification de l'existence du client dans la table 'clients'
            cursor.execute("SELECT COUNT(*) FROM clients WHERE id = %s", (client_id,))
            if cursor.fetchone()[0] == 0:
                logger.warning(f"Client ID {client_id} inexistant dans la base de données.")
                return False

            # Traitement de chaque livre dans la liste
            for livre in livres:
                if not validate_isbn(livre.isbn):
                    logger.warning(f"ISBN invalide pour le livre : {livre.titre}")
                    continue  # Passe au livre suivant sans interrompre la boucle
                # Utilisation d'un prix aléatoire si aucun prix n'est spécifié
                prix = generate_random_price() if livre.prix is None else round(float(livre.prix), 2)
                cursor.execute(
                    "INSERT INTO commandes (client_id, livre_isbn, titre_livre, prix) "
                    "VALUES (%s, %s, %s, %s)",
                    (client_id, livre.isbn, livre.titre, prix)
                )
            conn.commit()  # Validation des insertions dans la base de données
            logger.info(f"Commande enregistrée pour le client {client_id} avec {len(livres)} livres.")
            return True

    except ValueError as e:
        logger.error(f"Erreur de conversion du prix en float : {str(e)}")
        return False
    except mysql.connector.Error as e:
        logger.error(f"Erreur MySQL lors de l'enregistrement de la commande : {str(e)}")
        return False