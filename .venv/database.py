"""Module pour la gestion des connexions à la base de données MySQL."""

import mysql.connector
from config import MYSQL_CONFIG  # Configuration importée depuis un fichier séparé
import logging

# Initialisation du logger pour ce module
logger = logging.getLogger(__name__)

class Database:
    """Classe pour gérer les connexions et interactions avec la base de données MySQL.

    Cette classe fournit des méthodes statiques pour établir et gérer les connexions
    à une base de données MySQL en utilisant les paramètres définis dans MYSQL_CONFIG.
    """

    @staticmethod
    def get_connection():
        """Établit une connexion à la base de données MySQL.

        Utilise les paramètres de configuration définis dans MYSQL_CONFIG pour
        créer une nouvelle connexion à la base de données.

        Returns:
            mysql.connector.connection.MySQLConnection: Objet représentant une connexion active
                à la base de données MySQL.

        Raises:
            mysql.connector.Error: En cas d'échec de la connexion (par exemple, identifiants
                incorrects, serveur inaccessible, etc.).
        """
        try:
            # Tentative de connexion avec les paramètres de MYSQL_CONFIG
            connection = mysql.connector.connect(**MYSQL_CONFIG)
            return connection
        except mysql.connector.Error as e:
            # Journalisation de l'erreur avec des détails pour le débogage
            logger.error(f"Échec de la connexion à la base de données : {str(e)}")
            raise  # Relance l'exception pour une gestion par l'appelant