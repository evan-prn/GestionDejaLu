"""Module définissant la classe Livre pour représenter un livre."""

class Livre:
    """Représente un livre avec ses informations principales.

    Attributs:
        titre (str): Titre du livre.
        auteur (str): Auteur(s) du livre.
        couverture (str, optionnel): URL de la couverture.
        isbn (str, optionnel): ISBN du livre.
        date_publication (str, optionnel): Date de publication.
        synopsis (str, optionnel): Synopsis ou description.
        prix (float, optionnel): Prix en euros (None si non spécifié).
        format_livre (str, optionnel): Format (ex. 'papier', 'numérique').
        editeur (str, optionnel): Nom de l'éditeur.
        langue (str, optionnel): Code de langue (ex. 'fr').
    """

    def __init__(self, titre, auteur, couverture=None, isbn=None, date_publication=None, synopsis=None,
                 format_livre=None, editeur=None, langue=None, prix=None):
        """Initialise un livre avec les informations fournies.

        Args:
            titre (str): Titre du livre.
            auteur (str): Auteur(s) du livre.
            couverture (str, optional): URL de la couverture.
            isbn (str, optional): ISBN du livre.
            date_publication (str, optional): Date de publication.
            synopsis (str, optional): Synopsis.
            format_livre (str, optional): Format du livre.
            editeur (str, optional): Nom de l'éditeur.
            langue (str, optional): Code de langue.
            prix (float, optional): Prix en euros.
        """
        self.titre = titre if titre else "Titre inconnu"
        self.auteur = auteur if auteur else "Auteur inconnu"
        self.couverture = couverture
        self.isbn = isbn
        self.date_publication = date_publication
        self.synopsis = synopsis
        self.format_livre = format_livre if format_livre else "Non spécifié"
        self.editeur = editeur if editeur else "Éditeur inconnu"
        self.langue = langue if langue else "Langue inconnue"
        self.prix = float(prix) if prix is not None else None

    def __str__(self):
        """Retourne une représentation textuelle du livre."""
        return f"{self.titre} de {self.auteur}"

    @property
    def prix_formate(self):
        """Formate le prix avec la devise (€) ou indique 'Non spécifié' si None.

        Returns:
            str: Prix formaté (ex. '12.50 €') ou 'Non spécifié'.
        """
        return f"{self.prix:.2f} €" if self.prix is not None else "Non spécifié"