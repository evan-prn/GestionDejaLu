#!/usr/bin/env python3
"""Point d'entrée principal pour l'application GestionDejaLu."""

import logging
from gui import Application

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    """Initialise et exécute l'application graphique.

    Crée une instance de la classe Application et lance la boucle principale
    pour gérer les interactions utilisateur. Gère les erreurs globales.
    """
    try:
        app = Application()
        app.mainloop()
    except Exception as e:
        logger.error(f"Erreur lors du lancement de l'application : {e}")
        raise

if __name__ == "__main__":
    main()