"""Module pour l'interface graphique de l'application GestionDejaLu.

Ce module définit la classe Application qui gère l'interface utilisateur Tkinter,
incluant la recherche de livres, la gestion des clients, le panier et la validation
des commandes. Il intègre des styles visuels, une journalisation et des interactions
avec les autres modules (base de données, API, email).
"""

import tkinter as tk
from tkinter import messagebox, ttk
from config import STYLES, RANDOM_PRICE_MIN, RANDOM_PRICE_MAX  # Importation des configurations de style et prix
from api import rechercher_livres_par_titre_ou_isbn  # Recherche via Google Books API
from client import ajouter_client, rechercher_clients, get_clients  # Gestion des clients
from models import enregistrer_commande, generate_random_price  # Gestion des commandes
from livre import Livre  # Classe Livre pour représenter un livre
from email_service import send_order_confirmation_email  # Envoi d'emails
import logging
import mysql.connector  # Gestion des erreurs MySQL

# Initialisation du logger pour ce module
logger = logging.getLogger(__name__)

class Application(tk.Tk):
    """Classe principale pour l'interface graphique de GestionDejaLu.

    Hérite de tk.Tk pour créer une fenêtre principale avec des fonctionnalités
    de recherche de livres, gestion de clients, panier et validation de commandes.

    Attributes:
        panier (list): Liste des objets Livre ajoutés au panier.
        client_id (int or None): ID du client sélectionné (initialisé mais non utilisé ici).
    """

    def __init__(self):
        """Initialise l'application Tkinter avec les paramètres de base."""
        super().__init__()
        self.title("Gestion DejaLu")
        self.attributes('-fullscreen', True)
        self.configure(bg=STYLES["bg"])
        self.panier = []
        self.client_id = None
        self.protocol("WM_DELETE_WINDOW", self.quitter)
        self.creer_widgets()

    def creer_widgets(self):
        """Crée les widgets principaux de l'interface utilisateur."""
        self.creer_barre_navigation()

        main_frame = tk.Frame(self, bg=STYLES["bg"], padx=10, pady=10)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        tk.Label(main_frame, text="Gestion DejaLu",
                 font=STYLES["font_title"], bg=STYLES["bg"], fg=STYLES["fg"]).pack(pady=(0, 20))

        self.creer_cadre_recherche(main_frame)

        self.canvas = tk.Canvas(main_frame, bg=STYLES["bg"])
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=STYLES["bg"])
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def creer_barre_navigation(self):
        """Crée la barre de navigation avec les boutons principaux."""
        nav_frame = tk.Frame(self, bg=STYLES["menu_bg"], pady=10, padx=10, bd=1, relief="raised")
        nav_frame.pack(fill="x", side="top")

        tk.Button(nav_frame, text="Gestion des Clients", font=STYLES["font_button"],
                  bg="#F1C40F", fg=STYLES["button_fg"], relief="flat", padx=15, pady=5,
                  command=self.gestion_clients).pack(side="left", padx=10)
        tk.Button(nav_frame, text="Voir le Panier", font=STYLES["font_button"],
                  bg=STYLES["order_bg"], fg=STYLES["button_fg"], relief="flat", padx=15, pady=5,
                  command=self.voir_panier).pack(side="left", padx=10)
        tk.Button(nav_frame, text="Quitter", font=STYLES["font_button"],
                  bg="#E74C3C", fg=STYLES["button_fg"], relief="flat", padx=15, pady=5,
                  command=self.quitter).pack(side="right", padx=10)

    def creer_cadre_recherche(self, parent):
        """Crée le cadre de recherche pour les livres avec champs et boutons."""
        search_frame = tk.Frame(parent, bg=STYLES["menu_bg"], padx=10, pady=8, bd=1, relief="solid",
                                highlightbackground=STYLES["menu_border"], highlightthickness=1)
        search_frame.pack(fill="x", pady=5)

        tk.Label(search_frame, text="Titre:", bg=STYLES["menu_bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.titre_entry = tk.Entry(search_frame, width=25, bg=STYLES["entry_bg"], fg=STYLES["fg"])
        self.titre_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(search_frame, text="ISBN:", bg=STYLES["menu_bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=0, column=2, padx=5, pady=2, sticky="e")
        self.isbn_entry = tk.Entry(search_frame, width=15, bg=STYLES["entry_bg"], fg=STYLES["fg"])
        self.isbn_entry.grid(row=0, column=3, padx=5, pady=2)

        tk.Label(search_frame, text="Langue:", bg=STYLES["menu_bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=0, column=4, padx=5, pady=2, sticky="e")
        self.langue_var = tk.StringVar(value="Tous")
        tk.OptionMenu(search_frame, self.langue_var, "Tous", "fr", "en", "es").grid(row=0, column=5, padx=5, pady=2)

        button_frame = tk.Frame(search_frame, bg=STYLES["menu_bg"])
        button_frame.grid(row=2, column=0, columnspan=6, pady=10)
        self.rechercher_btn = tk.Button(button_frame, text="Rechercher", font=STYLES["font_button"],
                                        bg=STYLES["button_bg"], fg=STYLES["button_fg"], relief="flat",
                                        padx=10, pady=3, command=self.rechercher_livres)
        self.rechercher_btn.pack(side="left", padx=5)
        tk.Button(button_frame, text="Effacer", font=STYLES["font_button"],
                  bg=STYLES["button_bg"], fg=STYLES["button_fg"], relief="flat",
                  padx=10, pady=3, command=self.effacer_recherche).pack(side="left", padx=5)

    def quitter(self):
        """Ferme l'application après confirmation de l'utilisateur."""
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            self.destroy()
            logger.info("Application fermée par l'utilisateur.")

    def gestion_clients(self):
        """Ouvre une fenêtre modale pour la gestion des clients."""
        client_window = tk.Toplevel(self)
        client_window.title("Gestion des Clients")
        client_window.geometry("800x600")
        client_window.configure(bg=STYLES["bg"])
        client_window.transient(self)  # Rend la fenêtre modale
        client_window.grab_set()  # Bloque les interactions avec la fenêtre principale

        tk.Label(client_window, text="Gestion des Clients", font=STYLES["font_title"],
                 bg=STYLES["bg"], fg=STYLES["fg"]).pack(pady=10)

        self.creer_cadre_recherche_clients(client_window)
        self.creer_cadre_ajout_client(client_window)
        self.creer_cadre_resultats_clients(client_window)
        self.rechercher_clients_gui("", "", "", client_window)

    def creer_cadre_recherche_clients(self, parent):
        """Crée le cadre de recherche pour les clients."""
        search_frame = tk.Frame(parent, bg=STYLES["menu_bg"], padx=10, pady=10, bd=1, relief="solid")
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Nom:", bg=STYLES["menu_bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        nom_search = tk.Entry(search_frame, width=20, bg=STYLES["entry_bg"], fg=STYLES["fg"])
        nom_search.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(search_frame, text="Prénom:", bg=STYLES["menu_bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        prenom_search = tk.Entry(search_frame, width=20, bg=STYLES["entry_bg"], fg=STYLES["fg"])
        prenom_search.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(search_frame, text="Téléphone:", bg=STYLES["menu_bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        telephone_search = tk.Entry(search_frame, width=20, bg=STYLES["entry_bg"], fg=STYLES["fg"])
        telephone_search.grid(row=0, column=5, padx=5, pady=5)

        tk.Button(search_frame, text="Rechercher", font=STYLES["font_button"],
                  bg=STYLES["button_bg"], fg=STYLES["button_fg"], relief="flat",
                  command=lambda: self.rechercher_clients_gui(nom_search.get(), prenom_search.get(),
                                                              telephone_search.get(), parent)).grid(
                      row=0, column=6, padx=10, pady=5)

    def creer_cadre_ajout_client(self, parent):
        """Crée le cadre pour ajouter un nouveau client."""
        add_frame = tk.Frame(parent, bg=STYLES["bg"], padx=10, pady=10, bd=1, relief="solid")
        add_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(add_frame, text="Ajouter un Client", font=("Helvetica", 14, "bold"),
                 bg=STYLES["bg"], fg=STYLES["fg"]).grid(row=0, column=0, columnspan=4, pady=5)

        tk.Label(add_frame, text="Nom:", bg=STYLES["bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        nom_entry = tk.Entry(add_frame, bg=STYLES["entry_bg"], fg=STYLES["fg"])
        nom_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_frame, text="Prénom:", bg=STYLES["bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=1, column=2, padx=5, pady=5, sticky="e")
        prenom_entry = tk.Entry(add_frame, bg=STYLES["entry_bg"], fg=STYLES["fg"])
        prenom_entry.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(add_frame, text="Âge:", bg=STYLES["bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        age_entry = tk.Entry(add_frame, bg=STYLES["entry_bg"], fg=STYLES["fg"])
        age_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(add_frame, text="Email:", bg=STYLES["bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=2, column=2, padx=5, pady=5, sticky="e")
        email_entry = tk.Entry(add_frame, bg=STYLES["entry_bg"], fg=STYLES["fg"])
        email_entry.grid(row=2, column=3, padx=5, pady=5)

        tk.Label(add_frame, text="Téléphone:", bg=STYLES["bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=3, column=0, padx=5, pady=5, sticky="e")
        telephone_entry = tk.Entry(add_frame, bg=STYLES["entry_bg"], fg=STYLES["fg"])
        telephone_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(add_frame, text="Ajouter", font=STYLES["font_button"],
                  bg=STYLES["button_bg"], fg=STYLES["button_fg"], relief="flat",
                  command=lambda: self.ajouter_client(nom_entry.get(), prenom_entry.get(), age_entry.get(),
                                                     email_entry.get(), telephone_entry.get(), parent)).grid(
                      row=3, column=3, padx=10, pady=10)

    def creer_cadre_resultats_clients(self, parent):
        """Crée le cadre pour afficher les résultats de recherche des clients."""
        result_frame = tk.Frame(parent, bg=STYLES["bg"])
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.client_tree = ttk.Treeview(result_frame, columns=("ID", "Nom", "Prénom", "Âge", "Email", "Téléphone"),
                                        show="headings", height=10)
        self.client_tree.heading("ID", text="ID")
        self.client_tree.heading("Nom", text="Nom")
        self.client_tree.heading("Prénom", text="Prénom")
        self.client_tree.heading("Âge", text="Âge")
        self.client_tree.heading("Email", text="Email")
        self.client_tree.heading("Téléphone", text="Téléphone")
        self.client_tree.column("ID", width=50)
        self.client_tree.column("Nom", width=100)
        self.client_tree.column("Prénom", width=100)
        self.client_tree.column("Âge", width=50)
        self.client_tree.column("Email", width=200)
        self.client_tree.column("Téléphone", width=150)
        self.client_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.client_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.client_tree.configure(yscrollcommand=scrollbar.set)

        action_frame = tk.Frame(parent, bg=STYLES["bg"])
        action_frame.pack(pady=10)
        tk.Button(action_frame, text="Modifier", font=STYLES["font_button"],
                  bg="#F1C40F", fg=STYLES["button_fg"], relief="flat",
                  command=lambda: self.modifier_client(parent)).pack(side="left", padx=5)
        tk.Button(action_frame, text="Supprimer", font=STYLES["font_button"],
                  bg="#E74C3C", fg=STYLES["button_fg"], relief="flat",
                  command=lambda: self.supprimer_client(parent)).pack(side="left", padx=5)

    def rechercher_clients_gui(self, nom, prenom, telephone, window):
        """Recherche et affiche les clients dans le Treeview."""
        if not hasattr(self, 'client_tree'):
            logger.error("Treeview non initialisé avant la recherche.")
            messagebox.showerror("Erreur", "Erreur interne : Treeview non initialisé.")
            return
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)

        try:
            clients = rechercher_clients(nom=nom.strip(), prenom=prenom.strip(), telephone=telephone.strip())
            for client in clients:
                self.client_tree.insert("", "end", values=(client[0], client[1], client[2], client[3], client[4], client[5] or ""))
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des clients : {str(e)}")
            messagebox.showerror("Erreur", "Échec de la recherche des clients.")

    def ajouter_client(self, nom, prenom, age, email, telephone, window):
        """Ajoute un client via l'interface graphique."""
        from client import validate_email, validate_phone
        nom, prenom, email = nom.strip(), prenom.strip(), email.strip()
        telephone = telephone.strip() if telephone else None

        if not all([nom, prenom, age, email]):
            messagebox.showwarning("Erreur", "Tous les champs obligatoires (nom, prénom, âge, email) doivent être remplis.")
            return
        if not validate_email(email):
            messagebox.showerror("Erreur", "Format d'email invalide.")
            return
        if telephone and not validate_phone(telephone):
            messagebox.showerror("Erreur", "Format de téléphone invalide (ex. +33123456789 ou vide).")
            return
        try:
            age = int(age)
            if age <= 0:
                raise ValueError("L'âge doit être positif")
            if ajouter_client(nom, prenom, age, email, telephone):
                messagebox.showinfo("Succès", f"Client {prenom} {nom} ajouté avec succès !")
                self.rechercher_clients_gui("", "", "", window)
            else:
                messagebox.showerror("Erreur", "Échec de l'ajout du client. Vérifiez les données.")
        except ValueError as e:
            messagebox.showerror("Erreur", str(e) if "âge" in str(e) else "L'âge doit être un nombre.")
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du client : {str(e)}")
            messagebox.showerror("Erreur", "Une erreur inattendue est survenue.")

    def modifier_client(self, window):
        """Ouvre une fenêtre pour modifier un client sélectionné."""
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un client à modifier.")
            return

        client_id = self.client_tree.item(selected[0])["values"][0]
        edit_window = tk.Toplevel(self)
        edit_window.title("Modifier Client")
        edit_window.geometry("400x300")
        edit_window.configure(bg=STYLES["bg"])
        edit_window.transient(self)
        edit_window.grab_set()

        # Titre avec pack
        tk.Label(edit_window, text="Modifier Client", font=("Helvetica", 14, "bold"),
                 bg=STYLES["bg"], fg=STYLES["fg"]).pack(pady=10)

        # Frame pour les champs, géré par pack
        fields_frame = tk.Frame(edit_window, bg=STYLES["bg"])
        fields_frame.pack(pady=10, padx=10, fill="x")

        fields = ["Nom", "Prénom", "Âge", "Email", "Téléphone"]
        entries = {}
        for field in fields:
            # Chaque ligne dans un frame horizontal
            row_frame = tk.Frame(fields_frame, bg=STYLES["bg"])
            row_frame.pack(fill="x", pady=5)

            tk.Label(row_frame, text=f"{field}:", bg=STYLES["bg"], fg=STYLES["fg"],
                     font=STYLES["font_label"], width=10, anchor="e").pack(side="left", padx=5)
            entries[field] = tk.Entry(row_frame, bg=STYLES["entry_bg"], fg=STYLES["fg"])
            entries[field].pack(side="left", padx=5, fill="x", expand=True)

        # Remplissage des champs avec les valeurs actuelles
        current_values = self.client_tree.item(selected[0])["values"]
        entries["Nom"].insert(0, current_values[1])
        entries["Prénom"].insert(0, current_values[2])
        entries["Âge"].insert(0, current_values[3])
        entries["Email"].insert(0, current_values[4])
        entries["Téléphone"].insert(0, current_values[5] or "")

        # Bouton Sauvegarder avec pack
        tk.Button(edit_window, text="Sauvegarder", font=STYLES["font_button"],
                  bg=STYLES["button_bg"], fg=STYLES["button_fg"], relief="flat",
                  command=lambda: self.sauvegarder_modification(client_id, entries["Nom"].get(),
                                                                entries["Prénom"].get(),
                                                                entries["Âge"].get(), entries["Email"].get(),
                                                                entries["Téléphone"].get(), edit_window, window)).pack(
            pady=10)

    def sauvegarder_modification(self, client_id, nom, prenom, age, email, telephone, edit_window, client_window):
        """Sauvegarde les modifications apportées à un client."""
        from client import validate_email, validate_phone
        nom, prenom, email = nom.strip(), prenom.strip(), email.strip()
        telephone = telephone.strip() if telephone else None

        if not all([nom, prenom, age, email]):
            messagebox.showwarning("Erreur", "Tous les champs obligatoires doivent être remplis.")
            return
        if not validate_email(email):
            messagebox.showerror("Erreur", "Format d'email invalide.")
            return
        if telephone and not validate_phone(telephone):
            messagebox.showerror("Erreur", "Format de téléphone invalide (ex. +33123456789 ou vide).")
            return
        try:
            age = int(age)
            if age <= 0:
                raise ValueError("L'âge doit être positif")
            from database import Database
            with Database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE clients SET nom=%s, prenom=%s, age=%s, email=%s, telephone=%s WHERE id=%s",
                    (nom, prenom, age, email, telephone, client_id)
                )
                conn.commit()
            messagebox.showinfo("Succès", "Client modifié avec succès !")
            edit_window.destroy()
            self.rechercher_clients_gui("", "", "", client_window)
        except ValueError as e:
            messagebox.showerror("Erreur", str(e) if "âge" in str(e) else "L'âge doit être un nombre.")
        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL lors de la modification du client : {str(e)}")
            messagebox.showerror("Erreur", f"Erreur de base de données : {e}")

    def supprimer_client(self, window):
        """Supprime un client sélectionné après confirmation."""
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un client à supprimer.")
            return

        client_id = self.client_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce client ?"):
            try:
                from database import Database
                with Database.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM clients WHERE id=%s", (client_id,))
                    conn.commit()
                messagebox.showinfo("Succès", "Client supprimé avec succès !")
                self.rechercher_clients_gui("", "", "", window)
            except mysql.connector.Error as e:
                logger.error(f"Erreur MySQL lors de la suppression du client : {str(e)}")
                messagebox.showerror("Erreur", f"Erreur de base de données : {e}")

    def rechercher_livres(self):
        """Recherche des livres via l'API Google Books et affiche les résultats."""
        titre = self.titre_entry.get().strip()
        isbn = self.isbn_entry.get().strip()
        langue = self.langue_var.get() if self.langue_var.get() != "Tous" else None

        if not (titre or isbn):
            messagebox.showwarning("Erreur", "Veuillez entrer un titre ou un ISBN.")
            return
        if isbn and not (isbn.replace("-", "").isdigit() and len(isbn.replace("-", "")) in (10, 13)):
            messagebox.showwarning("Erreur", "L'ISBN doit être un numéro de 10 ou 13 chiffres.")
            return

        self.rechercher_btn.config(state="disabled", text="Recherche en cours...")
        self.update()
        try:
            livres_trouves = rechercher_livres_par_titre_ou_isbn(titre=titre, isbn=isbn, langue=langue)
            if not livres_trouves:
                messagebox.showinfo("Résultat", "Aucun livre trouvé.")
            self.afficher_resultats(livres_trouves)
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de livres : {str(e)}")
            messagebox.showerror("Erreur", "Échec de la recherche. Vérifiez votre connexion.")
        finally:
            self.rechercher_btn.config(state="normal", text="Rechercher")

    def effacer_recherche(self):
        """Efface les champs de recherche et les résultats affichés."""
        self.titre_entry.delete(0, tk.END)
        self.isbn_entry.delete(0, tk.END)
        self.langue_var.set("Tous")
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def ajouter_au_panier(self, livres):
        """Ajoute un ou plusieurs livres au panier avec un prix aléatoire si non défini."""
        livres_ajoutes = []
        logger.debug(f"Appel de ajouter_au_panier avec livres : {livres}")

        if not isinstance(livres, list):
            logger.debug(f"Ajout d'un seul livre : {livres.titre}")
            try:
                livre_copy = Livre(**vars(livres))
                if livre_copy.prix is None:
                    livre_copy.prix = generate_random_price()
                self.panier.append(livre_copy)
                livres_ajoutes.append(livre_copy.titre)
                logger.debug(f"Livre ajouté au panier : {livre_copy.titre}")
            except Exception as e:
                logger.error(f"Erreur lors de la copie du livre : {str(e)}")
                messagebox.showerror("Erreur", f"Échec de l'ajout au panier : {e}")
        else:
            logger.debug("Ajout multiple via sélection")
            for livre in livres:
                if self.livre_selection.get(livre, tk.BooleanVar(value=False)).get():
                    livre_copy = Livre(**vars(livre))
                    if livre_copy.prix is None:
                        livre_copy.prix = generate_random_price()
                    self.panier.append(livre_copy)
                    livres_ajoutes.append(livre_copy.titre)
                    self.livre_selection[livre].set(False)
                    logger.debug(f"Livre ajouté au panier (multiple) : {livre_copy.titre}")

        if livres_ajoutes:
            logger.info(f"Livres ajoutés : {livres_ajoutes}")
            messagebox.showinfo("Panier", f"{len(livres_ajoutes)} livre(s) ajouté(s) : {', '.join(livres_ajoutes)}")
            if isinstance(livres, list):
                self.afficher_resultats(livres)
        elif isinstance(livres, list):
            logger.warning("Aucun livre sélectionné pour l'ajout multiple")
            messagebox.showwarning("Panier", "Aucun livre sélectionné.")

    def afficher_resultats(self, livres):
        """Affiche les résultats de la recherche de livres dans le cadre défilant."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        if not livres:
            tk.Label(self.scrollable_frame, text="Aucun résultat trouvé", font=STYLES["font_label"],
                     bg=STYLES["bg"], fg=STYLES["fg"]).pack(pady=20)
            return

        selection_frame = tk.Frame(self.scrollable_frame, bg=STYLES["bg"])
        selection_frame.pack(fill="x", pady=5)
        tk.Button(selection_frame, text="Ajouter sélectionnés au panier", font=STYLES["font_button"],
                  bg=STYLES["button_bg"], fg=STYLES["button_fg"], relief="flat",
                  command=lambda: self.ajouter_au_panier(livres)).pack(side="right", padx=10)

        self.livre_selection = {}
        for livre in livres:
            prix_affichage = livre.prix if livre.prix is not None else generate_random_price()
            prix_formate = f"{prix_affichage:.2f} €" if livre.prix is None else livre.prix_formate
            card_frame = tk.Frame(self.scrollable_frame, bg=STYLES["card_bg"], bd=1, relief="solid", padx=10, pady=10)
            card_frame.pack(fill="x", padx=10, pady=5)

            self.livre_selection[livre] = tk.BooleanVar(value=False)
            tk.Checkbutton(card_frame, variable=self.livre_selection[livre], bg=STYLES["card_bg"]).pack(side="left")

            tk.Label(card_frame, text=livre.titre, font=("Helvetica", 14, "bold"),
                     bg=STYLES["card_bg"], fg=STYLES["fg"], wraplength=600, justify="left").pack(anchor="w", pady=(0, 3))
            tk.Label(card_frame, text=f"Auteur(s) : {livre.auteur or 'Inconnu'}", font=STYLES["font_label"],
                     bg=STYLES["card_bg"], fg=STYLES["fg"]).pack(anchor="w")
            tk.Label(card_frame, text=f"ISBN : {livre.isbn or 'Non spécifié'}", font=STYLES["font_label"],
                     bg=STYLES["card_bg"], fg=STYLES["fg"]).pack(anchor="w")
            tk.Label(card_frame, text=f"Prix : {prix_formate}", font=STYLES["font_label"],
                     bg=STYLES["card_bg"], fg=STYLES["fg"]).pack(anchor="w")
            tk.Button(card_frame, text="Ajouter au panier", font=STYLES["font_button"],
                      bg=STYLES["button_bg"], fg=STYLES["button_fg"], relief="flat",
                      command=lambda l=livre: self.ajouter_au_panier(l)).pack(anchor="e", pady=5)

    def voir_panier(self):
        """Ouvre une fenêtre pour afficher et gérer le contenu du panier."""
        if not self.panier:
            messagebox.showinfo("Panier", "Le panier est vide.")
            return
        panier_window = tk.Toplevel(self)
        panier_window.title("Mon Panier")
        panier_window.geometry("800x600")
        panier_window.configure(bg=STYLES["bg"])
        panier_window.transient(self)
        panier_window.grab_set()

        panier_frame = tk.Frame(panier_window, bg=STYLES["bg"])
        panier_frame.pack(pady=10, fill="both", expand=True)

        tk.Label(panier_frame, text="Contenu du Panier", font=STYLES["font_title"],
                 bg=STYLES["bg"], fg=STYLES["fg"]).pack(pady=(0, 10))

        canvas = tk.Canvas(panier_frame, bg=STYLES["bg"])
        scrollbar = ttk.Scrollbar(panier_frame, orient="vertical", command=canvas.yview)
        scrollable_content = tk.Frame(canvas, bg=STYLES["bg"])
        scrollable_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, livre in enumerate(self.panier):
            item_frame = tk.Frame(scrollable_content, bg=STYLES["card_bg"], bd=1, relief="solid", padx=10, pady=10)
            item_frame.pack(fill="x", padx=5, pady=5)
            tk.Label(item_frame, text=f"{livre.titre} - {livre.auteur or 'Inconnu'}", font=STYLES["font_label"],
                     bg=STYLES["card_bg"], fg=STYLES["fg"]).pack(anchor="w")
            tk.Label(item_frame, text=f"Prix : {livre.prix_formate}", font=STYLES["font_label"],
                     bg=STYLES["card_bg"], fg=STYLES["fg"]).pack(anchor="w")
            tk.Button(item_frame, text="Supprimer", font=STYLES["font_button"],
                      bg=STYLES["button_bg"], fg=STYLES["button_fg"], relief="flat",
                      command=lambda idx=i: self.supprimer_du_panier(idx, panier_window)).pack(anchor="e")

        client_frame = tk.Frame(panier_window, bg=STYLES["bg"])
        client_frame.pack(pady=10)
        tk.Label(client_frame, text="Sélectionner un client :", bg=STYLES["bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).pack(side="left", padx=5)
        self.client_var = tk.StringVar()
        clients = get_clients()
        if not clients:
            client_options = ["Aucun client"]
        else:
            client_options = [f"{c[1]} {c[2]} (ID: {c[0]})" for c in clients]  # Compatible avec 4 éléments
        tk.OptionMenu(client_frame, self.client_var, *client_options).pack(side="left", padx=5)
        tk.Button(client_frame, text="Valider la commande", font=STYLES["font_button"],
                  bg=STYLES["order_bg"], fg=STYLES["button_fg"], relief="flat",
                  command=lambda: self.valider_commande(clients, panier_window)).pack(side="left", padx=5)

    def supprimer_du_panier(self, index, window):
        """Supprime un livre du panier et rafraîchit la fenêtre."""
        if 0 <= index < len(self.panier):
            livre = self.panier.pop(index)
            messagebox.showinfo("Panier", f"{livre.titre} supprimé du panier.")
            window.destroy()
            self.voir_panier()

    def valider_commande(self, clients, window):
        """Valide la commande pour un client sélectionné et envoie une confirmation par email."""
        if not self.panier:
            messagebox.showwarning("Erreur", "Le panier est vide.")
            return
        if not clients:
            messagebox.showwarning("Erreur", "Aucun client disponible.")
            return

        client_selection = self.client_var.get()
        client = next((c for c in clients if f"{c[1]} {c[2]} (ID: {c[0]})" == client_selection), None)
        if not client:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un client valide.")
            return

        # Déballage pour 4 éléments : id, nom, prenom, email
        client_id, nom, prenom, email = client
        client_name = f"{prenom} {nom}"

        try:
            if enregistrer_commande(client_id, self.panier):
                email_sent = send_order_confirmation_email(email, client_name, self.panier)
                messagebox.showinfo("Succès",
                                    f"Commande validée pour {client_name} ! "
                                    f"{'Email envoyé à ' + email if email_sent else 'Échec de l’envoi de l’email.'}")
                self.panier.clear()
                window.destroy()
            else:
                messagebox.showerror("Erreur", "Échec de l'enregistrement de la commande.")
        except Exception as e:
            logger.error(f"Erreur lors de la validation de la commande : {str(e)}")
            messagebox.showerror("Erreur", f"Erreur lors de la validation : {e}")

if __name__ == "__main__":
    try:
        app = Application()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Erreur fatale au démarrage de l'application : {str(e)}")
        messagebox.showerror("Erreur critique", "L'application n'a pas pu démarrer correctement.")