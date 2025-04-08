#!/usr/bin/env python3
"""Script principal pour lancer une application graphique."""

from gui import Application
import logging

# Configuration basique du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Initialise et exécute l'application graphique.

    Crée une instance de la classe Application et démarre sa boucle principale
    pour gérer les interactions utilisateur.
    """
    try:
        # Instanciation de l'application
        app = Application()
        # Lancement de la boucle d'événements
        app.mainloop()
    except Exception as e:
        logger.error(f"Erreur lors du lancement de l'application : {e}")
        raise

if __name__ == "__main__":
    main()