"""
Module principal de l'application graphique.

Ce module crée et lance l'application graphique en initialisant
une instance de la classe `Application` et en démarrant la boucle
principale de l'interface graphique.

Exemple d'utilisation:
    python mon_script.py
"""

from gui import Application


def main():
    """
    Point d'entrée de l'application.

    Crée une instance de la classe `Application` et lance la
    boucle principale de l'interface graphique pour gérer
    les événements utilisateur.

    Cette fonction est exécutée uniquement si le module est
    exécuté directement (pas importé).

    """
    # Création d'une instance de l'application
    app = Application()

    # Démarrage de la boucle principale de l'application
    app.mainloop()


# Exécution de la fonction main si ce module est exécuté directement
if __name__ == "__main__":
    main()
