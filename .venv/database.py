"""Module pour la gestion des connexions à la base de données MySQL."""

import mysql.connector
from config import MYSQL_CONFIG
import logging

logger = logging.getLogger(__name__)

class Database:
    """Gère les connexions et requêtes à la base de données MySQL."""

    @staticmethod
    def get_connection():
        """Ouvre une connexion à la base de données MySQL.

        Returns:
            mysql.connector.connection.MySQLConnection: Connexion active.

        Raises:
            mysql.connector.Error: Si la connexion échoue.
        """
        try:
            return mysql.connector.connect(**MYSQL_CONFIG)
        except mysql.connector.Error as e:
            logger.error(f"Erreur de connexion à la base de données : {e}")
            raise