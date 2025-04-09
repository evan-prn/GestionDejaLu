import mysql.connector
from config import MYSQL_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    @staticmethod
    def get_connection():
        return mysql.connector.connect(**MYSQL_CONFIG)

def ajouter_client(nom, prenom, age, email, telephone):
    if not all([nom, prenom, age, email]):
        logger.warning("Champs obligatoires manquants pour ajouter un client.")
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

def rechercher_clients(nom=None, prenom=None, telephone=None):
    """Recherche des clients par nom, prénom ou téléphone."""
    try:
        with Database.get_connection() as conn:
            cursor = conn.cursor()
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
            cursor.execute(query, params)
            return cursor.fetchall()
    except mysql.connector.Error as e:
        logger.error(f"Erreur MySQL lors de la recherche de clients : {e}")
        return []

def get_clients():
    try:
        with Database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, prenom, nom, email FROM clients ORDER BY nom, prenom")
            return cursor.fetchall()
    except mysql.connector.Error as e:
        logger.error(f"Erreur MySQL lors de la récupération des clients : {e}")
        return []

def enregistrer_commande(client_id, livres):
    if not client_id or not livres:
        logger.warning("Client ID ou liste de livres manquante pour la commande.")
        return False
    try:
        with Database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM clients WHERE id = %s", (client_id,))
            if cursor.fetchone()[0] == 0:
                logger.warning(f"Client ID {client_id} inexistant.")
                return False
            for livre in livres:
                prix = round(float(livre.prix), 2)
                cursor.execute(
                    "INSERT INTO commandes (client_id, livre_isbn, titre_livre, prix) VALUES (%s, %s, %s, %s)",
                    (client_id, livre.isbn, livre.titre, prix)
                )
            conn.commit()
            logger.info(f"Commande enregistrée pour le client {client_id} avec {len(livres)} livres.")
            return True
    except mysql.connector.Error as e:
        logger.error(f"Erreur MySQL lors de l’enregistrement de la commande : {e}")
        return False

if __name__ == "__main__":
    try:
        conn = Database.get_connection()
        logger.info("Connexion à MySQL réussie !")
        conn.close()
    except mysql.connector.Error as e:
        logger.error(f"Échec de la connexion : {e}")


