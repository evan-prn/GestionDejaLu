#livre.py

import random

class Livre:
    """
    Représente un livre avec ses informations principales.

    Attributs:
        titre (str) : Le titre du livre.
        auteur (str) : L'auteur ou les auteurs du livre.
        couverture (str, optionnel) : URL de la couverture.
        isbn (str, optionnel) : ISBN du livre.
        date_publication (str, optionnel) : Date de publication.
        synopsis (str, optionnel) : Synopsis ou description.
        prix (float, optionnel) : Prix en euros (sans devise dans l’attribut).
        format_livre (str, optionnel) : Format (ex. 'papier', 'numérique').
        editeur (str, optionnel) : Nom de l’éditeur.
        langue (str, optionnel) : Code de langue (ex. 'fr').
    """

    def __init__(self, titre, auteur, couverture=None, isbn=None, date_publication=None, synopsis=None,
                 format_livre=None, editeur=None, langue=None, prix=None):
        self.titre = titre if titre else "Titre inconnu"
        self.auteur = auteur if auteur else "Auteur inconnu"
        self.couverture = couverture
        self.isbn = isbn
        self.date_publication = date_publication
        self.synopsis = synopsis
        self.format_livre = format_livre if format_livre else "Non spécifié"
        self.editeur = editeur if editeur else "Éditeur inconnu"
        self.langue = langue if langue else "Langue inconnue"
        self.prix = float(prix) if prix is not None else random.uniform(5, 30)

    def __str__(self):
        return f"{self.titre} de {self.auteur}"

    @property
    def prix_formate(self):
        return f"{self.prix:.2f} €"