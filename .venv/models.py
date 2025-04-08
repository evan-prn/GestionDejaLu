import random
import mysql.connector
from config import MYSQL_CONFIG


class Livre:
    """
    Représente un livre avec ses informations principales.

    Cette classe est utilisée pour créer des objets représentant des livres 
    avec des attributs tels que le titre, l'auteur, l'ISBN, la date de publication, 
    le synopsis, le prix, le format, l'éditeur et la langue.

    Attributs:
        titre (str) : Le titre du livre.
        auteur (str) : L'auteur du livre.
        couverture (str, optionnel) : L'URL de la couverture du livre.
        isbn (str, optionnel) : Le numéro ISBN du livre.
        date_publication (str, optionnel) : La date de publication du livre.
        synopsis (str, optionnel) : Un synopsis du livre.
        prix (str, optionnel) : Le prix du livre, formaté avec un montant en euros.
        format_livre (str, optionnel) : Le format du livre (ex : "papier", "numérique").
        editeur (str, optionnel) : L'éditeur du livre.
        langue (str, optionnel) : La langue du livre.

    Exemple:
        >>> livre = Livre("Python pour les nuls", "John Doe", prix="25.00 €")
        >>> print(livre)
        Python pour les nuls de John Doe
    """

    def __init__(self, titre, auteur, couverture=None, isbn=None, date_publication=None, synopsis=None, prix=None,
                 format_livre=None, editeur=None, langue=None):
        self.titre = titre
        self.auteur = auteur
        self.couverture = couverture
        self.isbn = isbn or "Non disponible"
        self.date_publication = date_publication or "Date inconnue"
        self.synopsis = synopsis or "Synopsis non disponible"
        self.prix = prix or f"{random.uniform(5, 30):.2f} €"
        self.format_livre = format_livre or "Non spécifié"
        self.editeur = editeur or "Éditeur inconnu"
        self.langue = langue or "Langue inconnue"

    def __str__(self):
        """
        Retourne une représentation sous forme de chaîne de caractères du livre.

        La chaîne renvoyée est sous la forme : "<titre> de <auteur>".

        Retourne:
            str : Représentation textuelle du livre.

        Exemple:
            >>> livre = Livre("Python pour les nuls", "John Doe")
            >>> str(livre)
            "Python pour les nuls de John Doe"
        """
        return f"{self.titre} de {self.auteur}"


def connecter_bdd():
    """
    Établit une connexion à la base de données MySQL.

    Utilise les informations de connexion spécifiées dans le fichier de configuration 
    MYSQL_CONFIG pour établir la connexion à la base de données.

    Retourne:
        mysql.connector.connection_cext.CMySQLConnection : Un objet de connexion MySQL.

    Exemple:
        >>> conn = connecter_bdd()
        >>> print(conn)
        <mysql.connector.connection_cext.CMySQLConnection object at 0x7f7c0b7f7fd0>
    """
    return mysql.connector.connect(**MYSQL_CONFIG)


def ajouter_client(nom, prenom, age, email, telephone):
    """
    Ajoute un client dans la base de données.

    Cette fonction insère un nouvel enregistrement dans la table "clients" de la base de données
    avec les informations du client fournies.

    Paramètres:
        nom (str) : Le nom du client.
        prenom (str) : Le prénom du client.
        age (int) : L'âge du client.
        email (str) : L'email du client.
        telephone (str) : Le numéro de téléphone du client.

    Retourne:
        bool : Retourne True si l'ajout a réussi, sinon False.

    Exemple:
        >>> ajouter_client("Doe", "John", 30, "john.doe@example.com", "123456789")
        True
    """
    try:
        conn = connecter_bdd()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clients (nom, prenom, age, email, telephone) VALUES (%s, %s, %s, %s, %s)",
                       (nom, prenom, age, email, telephone))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Erreur MySQL : {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()


def get_clients():
    """
    Récupère tous les clients dans la base de données.

    Cette fonction interroge la table "clients" et récupère les informations des clients 
    dans la base de données.

    Retourne:
        list : Une liste de tuples représentant les clients sous la forme (id, prénom, nom, email),
               ou une liste vide en cas d'erreur.

    Exemple:
        >>> get_clients()
        [(1, "John", "Doe", "john.doe@example.com"), (2, "Jane", "Smith", "jane.smith@example.com")]
    """
    try:
        conn = connecter_bdd()
        cursor = conn.cursor()
        cursor.execute("SELECT id, prenom, nom, email FROM clients")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Erreur MySQL : {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()


def enregistrer_commande(client_id, livres):
    """
    Enregistre une commande dans la base de données.

    Cette fonction enregistre les livres commandés par un client dans la table "commandes".
    Chaque livre est associé à un client et un prix.

    Paramètres:
        client_id (int) : L'ID du client effectuant la commande.
        livres (list) : Liste d'objets Livre représentant les livres commandés.

    Retourne:
        bool : Retourne True si l'enregistrement a réussi, sinon False.

    Exemple:
        >>> livres = [Livre("Python pour les nuls", "John Doe", prix="25.00 €")]
        >>> enregistrer_commande(1, livres)
        True
    """
    try:
        conn = connecter_bdd()
        cursor = conn.cursor()
        for livre in livres:
            cursor.execute("INSERT INTO commandes (client_id, livre_isbn, titre_livre, prix) VALUES (%s, %s, %s, %s)",
                           (client_id, livre.isbn, livre.titre, float(livre.prix.replace(" €", ""))))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Erreur MySQL : {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()
