import requests
from models import Livre


def rechercher_livres_par_titre_ou_isbn(titre=None, isbn=None, langue=None, type_livre=None, sujet=None, editeur=None,
                                        sort_by="relevance"):
    """
    Recherche des livres via l'API Google Books en fonction du titre, ISBN, et autres critères.

    Cette fonction envoie une requête à l'API Google Books pour rechercher des livres 
    par titre, ISBN, langue, type de livre, sujet, et éditeur, et retourne une liste d'objets 
    'Livre' contenant les informations extraites.

    Paramètres:
        titre (str, optionnel) : Le titre du livre à rechercher. Si ce paramètre est fourni, 
                                 il sera utilisé pour la requête.
        isbn (str, optionnel) : L'ISBN du livre à rechercher. Si ce paramètre est fourni, 
                                il sera utilisé pour la requête.
        langue (str, optionnel) : La langue des livres à rechercher. Par défaut, tous les livres sont recherchés.
                                  Les valeurs possibles incluent les codes de langue (ex : 'fr' pour le français).
                                  Si la valeur est "all", ce filtre est ignoré.
        type_livre (str, optionnel) : Le type de livre à rechercher, par exemple "book", "magazine", etc.
                                      Si la valeur est "all", ce filtre est ignoré.
        sujet (str, optionnel) : Le sujet du livre. Si fourni, ce filtre est ajouté à la requête.
                                 Si la valeur est "all", ce filtre est ignoré.
        editeur (str, optionnel) : L'éditeur du livre. Si fourni, ce filtre est ajouté à la requête.
                                  Si la valeur est "all", ce filtre est ignoré.
        sort_by (str, optionnel) : Le critère de tri des résultats. Par défaut, "relevance" (pertinence),
                                   mais peut être défini à "newest" pour trier par date de publication.

    Retourne:
        list : Une liste d'objets 'Livre' qui contiennent les informations des livres trouvés par l'API.
              Si aucun livre n'est trouvé ou qu'il y a une erreur lors de la requête API, une liste vide est retournée.

    Exceptions:
        requests.exceptions.RequestException : En cas d'erreur lors de la requête API, une exception sera levée et un message 
                                                d'erreur sera affiché.

    Exemple:
        >>> rechercher_livres_par_titre_ou_isbn(titre="Python Programming")
        [Livre("Learning Python", "Mark Lutz", "http://example.com/cover.jpg", "9781449355739", "2013-06-01", "Description du livre", "Book", "O'Reilly Media", "en")]

    >>> rechercher_livres_par_titre_ou_isbn(isbn="9781449355739")
        [Livre("Learning Python", "Mark Lutz", "http://example.com/cover.jpg", "9781449355739", "2013-06-01", "Description du livre", "Book", "O'Reilly Media", "en")]
    """

    url = "https://www.googleapis.com/books/v1/volumes"
    query = ""
    if isbn:
        query = f"isbn:{isbn}"
    elif titre:
        query = f"intitle:{titre}"
    else:
        return []

    params = {
        "q": query,
        "maxResults": 15 if titre else 1,
        "orderBy": sort_by
    }
    if langue and langue != "all":
        params["langRestrict"] = langue
    if type_livre and type_livre != "all":
        params["printType"] = type_livre
    if sujet and sujet != "all" and titre:
        params["q"] += f" subject:{sujet}"
    if editeur and editeur != "all" and titre:
        params["q"] += f" inpublisher:{editeur}"

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        livres = []
        if "items" in data:
            for item in data["items"]:
                info = item["volumeInfo"]
                titre_livre = info.get("title", "Titre inconnu")
                auteur_livre = ", ".join(info.get("authors", ["Auteur inconnu"]))
                couverture = info.get("imageLinks", {}).get("thumbnail")
                isbn_result = next(
                    (id["identifier"] for id in info.get("industryIdentifiers", []) if id["type"] == "ISBN_13"), None)
                date_publication = info.get("publishedDate")
                synopsis = info.get("description")
                format_livre = info.get("printType", "Non spécifié")
                editeur_livre = info.get("publisher", "Éditeur inconnu")
                langue_livre = info.get("language", "Langue inconnue")
                livres.append(Livre(titre_livre, auteur_livre, couverture, isbn_result, date_publication, synopsis,
                                    format_livre=format_livre, editeur=editeur_livre, langue=langue_livre))
            return livres
        return []
    except requests.exceptions.RequestException as e:
        print(f"Erreur API : {str(e)}")
        return []
