"""Module pour la gestion des clients dans la base de données."""

import mysql.connector
from database import Database
import logging
import re

logger = logging.getLogger(__name__)

def validate_email(email: str) -> bool:
    """Valide le format d'une adresse email.

    Args:
        email (str): Adresse email à valider.

    Returns:
        bool: True si l'email est valide, False sinon.
    """
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Valide le format d'un numéro de téléphone (optionnel).

    Args:
        phone (str): Numéro de téléphone à valider.

    Returns:
        bool: True si valide ou vide, False sinon.
    """
    if not phone:
        return True
    pattern = r"^\+?\d{10,15}$"
    return bool(re.match(pattern, phone))

def ajouter_client(nom: str, prenom: str, age: int, email: str, telephone: str = None) -> bool:
    """Ajoute un client à la base de données.

    Args:
        nom (str): Nom du client.
        prenom (str): Prénom du client.
        age (int): Âge du client.
        email (str): Email du client.
        telephone (str, optional): Numéro de téléphone.

    Returns:
        bool: True si l'ajout réussit, False sinon.
    """
    if not all([nom, prenom, age, email]):
        logger.warning("Champs obligatoires manquants pour ajouter un client.")
        return False
    if not validate_email(email):
        logger.warning(f"Email invalide : {email}")
        return False
    if not validate_phone(telephone):
        logger.warning(f"Téléphone invalide : {telephone}")
        return False
    if not isinstance(age, int) or age <= 0:
        logger.warning(f"Âge invalide : {age}")
        return False

    try:
        with Database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clients (nom, prenom, age, email, telephone) VALUES (%s, %s, %s, %s, %s)",
                (nom.strip(), prenom.strip(), age, email.strip(), telephone or None)
            )
            conn.commit()
            logger.info(f"Client {prenom} {nom} ajouté avec succès.")
            return True
    except mysql.connector.Error as e:
        logger.error(f"Erreur MySQL lors de l'ajout du client : {e}")
        return False

def rechercher_clients(nom: str = None, prenom: str = None, telephone: str = None) -> list:
    """Recherche des clients selon des critères.

    Args:
        nom (str, optional): Nom ou partie du nom.
        prenom (str, optional): Prénom ou partie du prénom.
        telephone (str, optional): Numéro de téléphone ou partie.

    Returns:
        list: Liste de tuples représentant les clients trouvés (id, nom, prenom, age, email, telephone).
    """
    query = "SELECT id, nom, prenom, age, email, telephone FROM clients WHERE 1=1"
    params = []
    if nom:
        query += " AND nom LIKE %s"
        params.append(f"%{nom.strip()}%")
    if prenom:
        query += " AND prenom LIKE %s"
        params.append(f"%{prenom.strip()}%")
    if telephone:
        query += " AND telephone LIKE %s"
        params.append(f"%{telephone.strip()}%")

    try:
        with Database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    except mysql.connector.Error as e:
        logger.error(f"Erreur MySQL lors de la recherche de clients : {e}")
        return []

def get_clients() -> list:
    """Récupère tous les clients.

    Returns:
        list: Liste de tuples représentant les clients (id, prenom, nom, email).
    """
    try:
        with Database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, prenom, nom, email FROM clients ORDER BY nom, prenom")
            return cursor.fetchall()
    except mysql.connector.Error as e:
        logger.error(f"Erreur MySQL lors de la récupération des clients : {e}")
        return []