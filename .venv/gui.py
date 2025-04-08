import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import io
from config import STYLES
from api import rechercher_livres_par_titre_ou_isbn
from models import ajouter_client, get_clients, enregistrer_commande

class Application(tk.Tk):
    """
    La classe principale représentant l'interface utilisateur pour la bibliothèque moderne.
    Elle hérite de la classe Tk de tkinter et gère la recherche de livres, la gestion des clients et le panier d'achat.

    Attributs:
    - panier (list): Liste des livres ajoutés au panier.
    - client_id (int or None): ID du client actuellement sélectionné.
    """
    def __init__(self):
        """
        Constructeur de la classe Application.
        Initialise l'application, configure la fenêtre principale et crée les widgets de l'interface.

        Retour:
        - None
        """
        super().__init__()
        self.title("Bibliothèque Moderne - Google Books")
        self.attributes('-fullscreen', True)
        self.configure(bg=STYLES["bg"])

        self.panier = []
        self.client_id = None
        self.creer_widgets()

    def creer_widgets(self):
        """
        Crée et configure les widgets de l'interface graphique pour la recherche de livres et la gestion des clients.

        Retour:
        - None
        """
        main_frame = tk.Frame(self, bg=STYLES["bg"], padx=20, pady=20, bd=2, relief="raised")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(main_frame, text="Recherche de Livres - Google Books",
                 font=STYLES["font_title"], bg=STYLES["bg"], fg=STYLES["fg"]).pack(pady=(0, 20))

        # Gestion des clients button
        tk.Button(main_frame, text="Gestion des Clients", font=STYLES["font_button"],
                  bg="#F1C40F", fg=STYLES["button_fg"], relief="flat", padx=15, pady=5,
                  command=self.gestion_clients).pack(pady=5)

        # Frame pour la recherche
        search_frame = tk.Frame(main_frame, bg=STYLES["menu_bg"], padx=15, pady=15, bd=2, relief="groove",
                                highlightbackground=STYLES["menu_border"], highlightthickness=2)
        search_frame.pack(fill="x", pady=10)

        # Champs de recherche : Titre, ISBN, Langue, etc.
        # Chaque champ de recherche est configuré ici (comme pour 'Titre', 'ISBN', 'Langue', etc.)

    def gestion_clients(self):
        """
        Ouvre une nouvelle fenêtre permettant la gestion des clients (ajout et sélection).

        Retour:
        - None
        """
        client_window = tk.Toplevel(self)
        client_window.title("Gestion des Clients")
        client_window.geometry("600x400")
        client_window.configure(bg=STYLES["bg"])

        # Formulaire pour ajouter un client
        form_frame = tk.Frame(client_window, bg=STYLES["bg"])
        form_frame.pack(pady=10)

        # Champs du formulaire d'ajout de client
        # Chaque champ est un Label + Entry pour saisir les informations du client

        tk.Button(form_frame, text="Ajouter", font=STYLES["font_button"],
                  bg=STYLES["button_bg"], fg=STYLES["button_fg"], relief="flat",
                  command=lambda: self.ajouter_client(nom_entry.get(), prenom_entry.get(), age_entry.get(),
                                                    email_entry.get(), telephone_entry.get(), client_window)).grid(row=5, column=1, pady=10)

    def ajouter_client(self, nom, prenom, age, email, telephone, window):
        """
        Ajoute un client à la base de données après validation des informations.

        Paramètres:
        - nom (str): Nom du client.
        - prenom (str): Prénom du client.
        - age (str): Âge du client sous forme de chaîne de caractères.
        - email (str): Adresse email du client.
        - telephone (str): Numéro de téléphone du client.
        - window (tk.Toplevel): Fenêtre à fermer après l'ajout du client.

        Retour:
        - None

        Levée d'exception:
        - Affiche un message d'erreur si les champs obligatoires sont vides ou si l'âge n'est pas un nombre valide.
        """
        if not all([nom, prenom, age, email]):
            messagebox.showwarning("Erreur", "Tous les champs obligatoires (nom, prénom, âge, email) doivent être remplis.")
            return
        try:
            age = int(age)
            if ajouter_client(nom, prenom, age, email, telephone):
                messagebox.showinfo("Succès", f"Client {prenom} {nom} ajouté avec succès !")
                window.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "L'âge doit être un nombre.")

    def rechercher_livres(self):
        """
        Effectue une recherche de livres sur Google Books en fonction des critères définis par l'utilisateur (Titre, ISBN, Langue, etc.).

        Retour:
        - None

        Levée d'exception:
        - Affiche un message d'avertissement si aucun titre ni ISBN n'est fourni.
        """
        titre = self.titre_entry.get().strip()
        isbn = self.isbn_entry.get().strip()
        langue = self.langue_var.get()
        type_livre = self.type_var.get()
        sujet = self.sujet_var.get()
        editeur = self.editeur_var.get()

        if not titre and not isbn:
            messagebox.showwarning("Erreur", "Veuillez entrer un titre ou un ISBN.")
            return

        self.rechercher_btn.config(state="disabled", text="Recherche en cours...")
        self.update()

        livres_trouves = rechercher_livres_par_titre_ou_isbn(titre, isbn, langue, type_livre, sujet, editeur)
        self.afficher_resultats(livres_trouves)

        self.rechercher_btn.config(state="normal", text="Rechercher")

    def effacer_recherche(self):
        """
        Efface tous les champs de recherche et réinitialise l'affichage des résultats.

        Retour:
        - None
        """
        self.titre_entry.delete(0, tk.END)
        self.isbn_entry.delete(0, tk.END)
        self.langue_var.set("all")
        self.type_var.set("all")
        self.sujet_var.set("all")
        self.editeur_var.set("all")
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def afficher_resultats(self, livres):
        """
        Affiche les résultats de la recherche de livres dans l'interface.

        Paramètres:
        - livres (list): Liste des livres trouvés.

        Retour:
        - None
        """
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not livres:
            tk.Label(self.scrollable_frame, text="Aucun résultat trouvé", font=STYLES["font_label"],
                     bg=STYLES["bg"], fg=STYLES["fg"]).pack(pady=20)
            return

        # Affichage des informations pour chaque livre
        for livre in livres:
            card_frame = tk.Frame(self.scrollable_frame, bg=STYLES["card_bg"], bd=1,
                                  relief="solid", padx=15, pady=15)
            card_frame.pack(fill="x", padx=10, pady=5)

            titre_label = tk.Label(card_frame, text=livre.titre, font=("Helvetica", 16, "bold"),
                                   bg=STYLES["card_bg"], fg=STYLES["fg"], wraplength=600, justify="left")
            titre_label.pack(anchor="w", pady=(0, 5))
            titre_label.bind("<Enter>", lambda e, l=titre_label: l.config(fg=STYLES["highlight"]))
            titre_label.bind("<Leave>", lambda e, l=titre_label: l.config(fg=STYLES["fg"]))

            # Ajout des autres informations : Auteur, ISBN, Prix, Format, etc.

