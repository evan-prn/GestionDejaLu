"""Module définissant la classe Livre pour représenter un livre dans l'application."""

class Livre:
    """Représente un livre avec ses informations principales.

    Cette classe encapsule les données d'un livre telles que le titre, l'auteur, le prix,
    et d'autres métadonnées optionnelles. Elle fournit également des méthodes pour
    manipuler et afficher ces informations.

    Attributes:
        titre (str): Titre du livre, "Titre inconnu" si non spécifié.
        auteur (str): Nom de l'auteur ou des auteurs, "Auteur inconnu" si non spécifié.
        couverture (str, optional): URL ou chemin de la couverture du livre, None si absent.
        isbn (str, optional): Numéro ISBN du livre, None si absent.
        date_publication (str, optional): Date de publication (format libre), None si absente.
        synopsis (str, optional): Résumé ou description du livre, None si absent.
        prix (float, optional): Prix du livre en euros, None si non spécifié.
        format_livre (str, optional): Format du livre (ex. 'papier', 'numérique'), "Non spécifié" si absent.
        editeur (str, optional): Nom de l'éditeur, "Éditeur inconnu" si non spécifié.
        langue (str, optional): Code ou nom de la langue (ex. 'fr'), "Langue inconnue" si non spécifié.
    """

    def __init__(self, titre, auteur, couverture=None, isbn=None, date_publication=None, synopsis=None,
                 format_livre=None, editeur=None, langue=None, prix=None):
        """Initialise une instance de Livre avec les informations fournies.

        Les paramètres obligatoires sont le titre et l'auteur. Les autres attributs sont
        optionnels et reçoivent des valeurs par défaut si non fournis.

        Args:
            titre (str): Titre du livre.
            auteur (str): Nom de l'auteur ou des auteurs.
            couverture (str, optional): URL ou chemin de la couverture. Defaults to None.
            isbn (str, optional): Numéro ISBN du livre. Defaults to None.
            date_publication (str, optional): Date de publication. Defaults to None.
            synopsis (str, optional): Résumé ou description. Defaults to None.
            format_livre (str, optional): Format du livre. Defaults to None.
            editeur (str, optional): Nom de l'éditeur. Defaults to None.
            langue (str, optional): Code ou nom de la langue. Defaults to None.
            prix (float, optional): Prix en euros. Defaults to None.
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
        """Retourne une représentation sous forme de chaîne du livre.

        Returns:
            str: Chaîne au format "titre de auteur" (ex. "Le Petit Prince de Antoine de Saint-Exupéry").
        """
        return f"{self.titre} de {self.auteur}"

    @property
    def prix_formate(self):
        """Retourne le prix formaté avec la devise ou un message si non défini.

        Returns:
            str: Prix avec deux décimales et symbole euro (ex. "12.50 €") ou "Non spécifié" si None.
        """
        return f"{self.prix:.2f} €" if self.prix is not None else "Non spécifié"