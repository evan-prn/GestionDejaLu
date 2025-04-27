#!/usr/bin/env python3
"""Point d'entrée principal pour l'application GestionDejaLu.

Ce module initialise le système de journalisation et lance l'interface graphique
de l'application. Il sert de point central pour démarrer le programme.
"""

import logging
from gui import Application  # Importation de la classe Application depuis le module gui

# Configuration du système de journalisation
logging.basicConfig(
    level=logging.INFO,  # Niveau de journalisation par défaut (INFO et supérieur)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # Format des messages
)
logger = logging.getLogger(__name__)  # Logger spécifique à ce module

def main():
    """Initialise et exécute l'application graphique GestionDejaLu.

    Cette fonction crée une instance de la classe Application, qui gère l'interface
    utilisateur, et lance la boucle principale Tkinter pour traiter les événements.
    Les exceptions globales sont capturées et journalisées pour faciliter le débogage.

    Raises:
        Exception: Si une erreur survient lors de l'initialisation ou de l'exécution
            de l'application, elle est relancée après journalisation.
    """
    try:
        # Création de l'instance de l'application graphique
        app = Application()
        # Lancement de la boucle principale pour les interactions utilisateur
        app.mainloop()
    except Exception as e:
        # Journalisation de l'erreur avec des détails
        logger.error(f"Erreur lors du lancement de l'application : {str(e)}")
        raise  # Relance l'exception pour permettre une gestion externe si nécessaire

if __name__ == "__main__":
    # Point d'entrée du script : exécute main() si le fichier est lancé directement
    main()