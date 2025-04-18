"""Module pour la gestion des commandes dans la base de données."""

from database import Database
import logging

logger = logging.getLogger(__name__)

def validate_isbn(isbn: str) -> bool:
    """Valide le format d'un ISBN (10 ou 13 chiffres).

    Args:
        isbn (str): ISBN à valider.

    Returns:
        bool: True si l'ISBN est valide, False sinon.
    """
    if not isbn:
        return False
    isbn_clean = isbn.replace("-", "").replace(" ", "")
    return isbn_clean.isdigit() and len(isbn_clean) in (10, 13)

def enregistrer_commande(client_id: int, livres: list) -> bool:
    """Enregistre une commande pour un client.

    Args:
        client_id (int): ID du client.
        livres (list): Liste d'objets Livre.

    Returns:
        bool: True si la commande est enregistrée, False sinon.
    """
    if not client_id or not livres:
        logger.warning("Client ID ou liste de livres manquante pour la commande.")
        return False

    try:
        with Database.get_connection() as conn:
            cursor = conn.cursor()
            # Vérifier si le client existe
            cursor.execute("SELECT COUNT(*) FROM clients WHERE id = %s", (client_id,))
            if cursor.fetchone()[0] == 0:
                logger.warning(f"Client ID {client_id} inexistant.")
                return False

            # Insérer chaque livre comme une commande
            for livre in livres:
                if not validate_isbn(livre.isbn):
                    logger.warning(f"ISBN invalide pour le livre : {livre.titre}")
                    continue
                prix = 0.0 if livre.prix is None else round(float(livre.prix), 2)
                cursor.execute(
                    "INSERT INTO commandes (client_id, livre_isbn, titre_livre, prix) "
                    "VALUES (%s, %s, %s, %s)",
                    (client_id, livre.isbn, livre.titre, prix)
                )
            conn.commit()
            logger.info(f"Commande enregistrée pour le client {client_id} avec {len(livres)} livres.")
            return True
    except ValueError as e:
        logger.error(f"Erreur de conversion du prix : {e}")
        return False
    except mysql.connector.Error as e:
        logger.error(f"Erreur MySQL lors de l'enregistrement de la commande : {e}")
        return False