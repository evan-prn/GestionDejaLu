Document Technique : GestionDejaLu
1. Introduction
GestionDejaLu est une application Python avec une interface graphique Tkinter permettant la gestion d'une librairie. Elle permet de rechercher des livres via l'API Google Books, de gérer les clients, de constituer un panier avec des quantités personnalisées, de valider des commandes, et d'envoyer des confirmations par email. Le projet utilise une base de données MySQL pour stocker les informations des clients et des commandes.
Objectifs :

Faciliter la recherche et l'achat de livres.
Gérer les informations des clients (ajout, modification, suppression).
Permettre la validation de commandes avec envoi de confirmations par email.

2. Architecture du système
L'application suit une architecture modulaire :

Interface graphique (gui.py) : Gérée avec Tkinter, elle fournit une interface utilisateur pour la recherche, la gestion des clients, et le panier.
API Google Books (api.py) : Interface avec l'API pour rechercher des livres par titre ou ISBN.
Gestion des clients (client.py) : Fonctions pour ajouter, rechercher, modifier, et supprimer des clients.
Base de données (database.py) : Connexion à MySQL pour stocker les clients et les commandes.
Modèles (models.py) : Gestion des commandes et génération de prix aléatoires.
Envoi d'emails (email_service.py) : Envoi de confirmations de commande par email.
Configuration (config.py) : Constantes pour les styles, limites de prix, et autres paramètres.

Diagramme d'architecture (Mermaid) :
graph TD
    A[Utilisateur] --> B[GUI Tkinter]
    B --> C[API Google Books]
    B --> D[Base de données MySQL]
    B --> E[Service Email]
    C --> F[Google Books API]
    D --> G[Clients]
    D --> H[Commandes]
    E --> I[SMTP Server]

3. Fonctionnalités principales

Recherche de livres : Recherche par titre ou ISBN via l'API Google Books, avec filtre par langue.
Gestion des clients : Ajout, modification, suppression, et recherche de clients (nom, prénom, âge, email, téléphone).
Panier : Ajout de livres avec quantités personnalisées, affichage du contenu, suppression d'articles.
Validation de commande : Association d'une commande à un client, enregistrement dans la base de données, envoi d'email de confirmation.
Journalisation : Logs pour le débogage et le suivi des erreurs.

4. Dépendances

Python : Version 3.11
Bibliothèques :
tkinter : Interface graphique
requests : Appels HTTP à l'API Google Books
mysql-connector-python : Connexion à MySQL
Autres (à confirmer via requirements.txt)


Services externes :
Google Books API
Serveur SMTP pour les emails



5. Structure du code

gui.py : Interface principale avec Tkinter, gestion des interactions utilisateur.
api.py : Communication avec l'API Google Books pour la recherche de livres.
client.py : Logique métier pour la gestion des clients.
livre.py : Définition de la classe Livre (titre, auteur, ISBN, prix, quantité).
models.py : Gestion des commandes et utilitaires (par exemple, generate_random_price).
database.py : Connexion et requêtes SQL.
email_service.py : Envoi d'emails de confirmation.
config.py : Constantes de configuration (styles, paramètres).

6. Base de données
Schéma présumé (à confirmer) :

Table clients :
id : INT, clé primaire, auto-incrémenté
nom : VARCHAR
prenom : VARCHAR
age : INT
email : VARCHAR
telephone : VARCHAR (nullable)


Table commandes (hypothétique) :
id : INT, clé primaire
client_id : INT, clé étrangère
date : DATETIME
livres : JSON ou table séparée pour les livres



7. Flux de travail

Recherche de livres :
L'utilisateur entre un titre ou un ISBN.
Appel à l'API Google Books via rechercher_livres_par_titre_ou_isbn.
Affichage des résultats avec option d'ajouter au panier.


Ajout au panier :
Sélection d'un livre avec quantité via un champ d'entrée.
Ajout au panier comme tuple (livre, quantite).


Gestion des clients :
Ajout, modification, ou suppression via une fenêtre dédiée.


Validation de commande :
Sélection d'un client, enregistrement de la commande, envoi d'email.



8. Détails techniques

Gestion des quantités : Implémentée via un champ Entry pour chaque livre, stockée comme tuple (livre, quantite) dans self.panier.
Validation des entrées : Vérification des ISBN (10 ou 13 chiffres), emails, et quantités positives.
Journalisation : Utilisation du module logging pour capturer les erreurs et débogages.
Problème connu : Erreur _tkinter.tkapp dans rechercher_livres due à une mauvaise liaison du callback.

9. Instructions d'installation et d'exécution

Cloner le dépôt : git clone <url_du_dépôt>
Installer les dépendances : pip install -r requirements.txt
Configurer la base de données MySQL :
Créer une base de données.
Mettre à jour les paramètres dans database.py.


Configurer le serveur SMTP dans email_service.py.
Exécuter : python gui.py

10. Limites et améliorations futures

Limites :
Erreur _tkinter.tkapp non résolue, probablement liée à une mauvaise gestion du callback.
Dépendance à l'API Google Books (sujet à des limites de quota).
Pas de gestion avancée des erreurs réseau.


Améliorations :
Résoudre l'erreur _tkinter.tkapp en sécurisant les callbacks.
Ajouter un cache pour les recherches API.
Implémenter une interface plus moderne (par exemple, avec PyQt ou Kivy).



11. Annexes

Exemple de recherche :livres = rechercher_livres_par_titre_ou_isbn(titre="Harry Potter")


Capture d'écran : (À fournir par l'utilisateur)
Schéma de la base de données : (À compléter avec le schéma exact)

