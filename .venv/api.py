import requests
from livre import Livre
from urllib.parse import quote
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rechercher_livres_par_titre_ou_isbn(titre=None, isbn=None, langue=None, type_livre=None, sujet=None, editeur=None,
                                        sort_by="relevance", max_results=15):
    """
    Recherche des livres via l'API Google Books en fonction de divers critères.

    Args:
        titre (str, optional): Titre du livre à rechercher.
        isbn (str, optional): ISBN du livre (10 ou 13 chiffres).
        langue (str, optional): Code de langue (ex. 'fr', 'en').
        type_livre (str, optional): Type de publication ('book', 'magazine').
        sujet (str, optional): Sujet ou catégorie du livre.
        editeur (str, optional): Nom de l'éditeur.
        sort_by (str, optional): Critère de tri ('relevance' ou 'newest'). Par défaut 'relevance'.
        max_results (int, optional): Nombre maximum de résultats (1 à 40). Par défaut 15.

    Returns:
        list: Liste d'objets Livre. Vide si aucun résultat ou erreur.
    """
    if not titre and not isbn:
        logger.warning("Aucun titre ni ISBN fourni pour la recherche.")
        return []

    if isbn:
        isbn = isbn.replace("-", "").strip()
        if not (isbn.isdigit() and len(isbn) in (10, 13)):
            logger.warning(f"ISBN invalide : {isbn}")
            return []

    url = "https://www.googleapis.com/books/v1/volumes"
    query_parts = []
    if isbn:
        query_parts.append(f"isbn:{isbn}")
    elif titre:
        query_parts.append(f"intitle:{quote(titre.strip())}")

    if sujet and titre:
        query_parts.append(f"subject:{quote(sujet)}")
    if editeur and titre:
        query_parts.append(f"inpublisher:{quote(editeur)}")

    params = {
        "q": " ".join(query_parts),
        "maxResults": min(max(max_results, 1), 40),
        "orderBy": sort_by if sort_by in ("relevance", "newest") else "relevance"
    }
    if langue:
        params["langRestrict"] = langue.lower()
    if type_livre:
        params["printType"] = type_livre.lower()

    logger.info(f"Requête API : {params}")
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        livres = []
        if "items" not in data:
            logger.info("Aucun résultat retourné par l'API.")
            return livres

        for item in data["items"]:
            info = item["volumeInfo"]
            titre_livre = info.get("title", "Titre inconnu")
            auteur_livre = ", ".join(info.get("authors", ["Auteur inconnu"]))
            couverture = info.get("imageLinks", {}).get("thumbnail", None)
            isbn_result = next(
                (id["identifier"] for id in info.get("industryIdentifiers", []) if id["type"] == "ISBN_13"), None)
            date_publication = info.get("publishedDate")
            synopsis = info.get("description")
            format_livre = info.get("printType", "Non spécifié")
            editeur_livre = info.get("publisher", "Éditeur inconnu")
            langue_livre = info.get("language", "Langue inconnue")

            livres.append(Livre(
                titre_livre, auteur_livre, couverture, isbn_result, date_publication, synopsis,
                format_livre=format_livre, editeur=editeur_livre, langue=langue_livre
            ))
        return livres
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la requête API : {e}")
        return []