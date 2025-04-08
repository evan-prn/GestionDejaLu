import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import io
import requests
from config import STYLES
from api import rechercher_livres_par_titre_ou_isbn
from models import ajouter_client, get_clients, enregistrer_commande
from livre import Livre
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Application(tk.Tk):
    def __init__(self):
        """Initialise l'application avec une fenêtre plein écran et les widgets principaux."""
        super().__init__()
        self.title("Bibliothèque Moderne - Google Books")
        self.attributes('-fullscreen', True)
        self.configure(bg=STYLES["bg"])
        self.panier = []
        self.client_id = None
        # Gestion de la fermeture via le bouton "X"
        self.protocol("WM_DELETE_WINDOW", self.quitter)
        self.creer_widgets()

    def creer_widgets(self):
        """Crée et configure les widgets principaux de l'interface graphique."""
        main_frame = tk.Frame(self, bg=STYLES["bg"], padx=10, pady=10, bd=1, relief="raised")
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        tk.Label(main_frame, text="Recherche de Livres - Google Books",
                 font=STYLES["font_title"], bg=STYLES["bg"], fg=STYLES["fg"]).pack(pady=(0, 10))

        tk.Button(main_frame, text="Gestion des Clients", font=STYLES["font_button"],
                  bg="#F1C40F", fg=STYLES["button_fg"], relief="flat", padx=10, pady=3,
                  command=self.gestion_clients).pack(pady=5)

        tk.Button(main_frame, text="Voir le Panier", font=STYLES["font_button"],
                  bg=STYLES["order_bg"], fg=STYLES["button_fg"], relief="flat", padx=10, pady=3,
                  command=self.voir_panier).pack(pady=5)

        # Bouton Quitter
        tk.Button(main_frame, text="Quitter", font=STYLES["font_button"],
                  bg="#E74C3C", fg=STYLES["button_fg"], relief="flat", padx=10, pady=3,
                  command=self.quitter).pack(pady=5)

        search_frame = tk.Frame(main_frame, bg=STYLES["menu_bg"], padx=10, pady=8, bd=1, relief="solid",
                                highlightbackground=STYLES["menu_border"], highlightthickness=1)
        search_frame.pack(fill="x", pady=5)

        tk.Label(search_frame, text="Titre:", bg=STYLES["menu_bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=0, column=0, padx=3, pady=2, sticky="e")
        self.titre_entry = tk.Entry(search_frame, width=25, bg=STYLES["entry_bg"], fg=STYLES["fg"])
        self.titre_entry.grid(row=0, column=1, padx=3, pady=2)

        tk.Label(search_frame, text="ISBN:", bg=STYLES["menu_bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=0, column=2, padx=3, pady=2, sticky="e")
        self.isbn_entry = tk.Entry(search_frame, width=15, bg=STYLES["entry_bg"], fg=STYLES["fg"])
        self.isbn_entry.grid(row=0, column=3, padx=3, pady=2)

        tk.Label(search_frame, text="Langue:", bg=STYLES["menu_bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=0, column=4, padx=3, pady=2, sticky="e")
        self.langue_var = tk.StringVar(value="Tous")
        tk.OptionMenu(search_frame, self.langue_var, "Tous", "fr", "en", "es").grid(row=0, column=5, padx=3, pady=2, sticky="w")

        tk.Label(search_frame, text="Type:", bg=STYLES["menu_bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=1, column=0, padx=3, pady=2, sticky="e")
        self.type_var = tk.StringVar(value="Tous")
        tk.OptionMenu(search_frame, self.type_var, "Tous", "book", "magazine").grid(row=1, column=1, padx=3, pady=2, sticky="w")

        tk.Label(search_frame, text="Sujet:", bg=STYLES["menu_bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=1, column=2, padx=3, pady=2, sticky="e")
        self.sujet_var = tk.StringVar(value="Tous")
        tk.OptionMenu(search_frame, self.sujet_var, "Tous", "fiction", "science", "history").grid(row=1, column=3, padx=3, pady=2, sticky="w")

        tk.Label(search_frame, text="Éditeur:", bg=STYLES["menu_bg"], fg=STYLES["fg"],
                 font=STYLES["font_label"]).grid(row=1, column=4, padx=3, pady=2, sticky="e")
        self.editeur_var = tk.StringVar(value="Tous")
        tk.OptionMenu(search_frame, self.editeur_var, "Tous", "Penguin", "Hachette", "Gallimard").grid(row=1, column=5, padx=3, pady=2, sticky="w")

        button_frame = tk.Frame(search_frame, bg=STYLES["menu_bg"])
        button_frame.grid(row=2, column=0, columnspan=6, pady=5)
        self.rechercher_btn = tk.Button(button_frame, text="Rechercher", font=STYLES["font_button"],
                                        bg=STYLES["button_bg"], fg=STYLES["button_fg"], relief="flat",
                                        padx=8, pady=2, command=self.rechercher_livres)
        self.rechercher_btn.pack(side="left", padx=3)
        tk.Button(button_frame, text="Effacer", font=STYLES["font_button"],
                  bg=STYLES["button_bg"], fg=STYLES["button_fg"], relief="flat",
                  padx=8, pady=2, command=self.effacer_recherche).pack(side="left", padx=3)

        canvas = tk.Canvas(main_frame, bg=STYLES["bg"])
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=STYLES["bg"])

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def quitter(self):
        """Ferme proprement l'application."""
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            self.destroy()
            logger.info("Application fermée par l'utilisateur.")

    def gestion_clients(self):
        client_window = tk.Toplevel(self)
        client_window.title("Gestion des Clients")
        client_window.geometry("600x400")
        client_window.configure(bg=STYLES["bg"])

        form_frame = tk.Frame(client_window, bg=STYLES["bg"])
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Nom:", bg=STYLES["bg"], fg=STYLES["fg"]).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        nom_entry = tk.Entry(form_frame)
        nom_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Prénom:", bg=STYLES["bg"], fg=STYLES["fg"]).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        prenom_entry = tk.Entry(form_frame)
        prenom_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Âge:", bg=STYLES["bg"], fg=STYLES["fg"]).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        age_entry = tk.Entry(form_frame)
        age_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Email:", bg=STYLES["bg"], fg=STYLES["fg"]).grid(row=3, column=0, padx=5, pady=5, sticky="e")
        email_entry = tk.Entry(form_frame)
        email_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Téléphone:", bg=STYLES["bg"], fg=STYLES["fg"]).grid(row=4, column=0, padx=5, pady=5, sticky="e")
        telephone_entry = tk.Entry(form_frame)
        telephone_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Button(form_frame, text="Ajouter", font=STYLES["font_button"],
                  bg=STYLES["button_bg"], fg=STYLES["button_fg"], relief="flat",
                  command=lambda: self.ajouter_client(nom_entry.get(), prenom_entry.get(), age_entry.get(),
                                                      email_entry.get(), telephone_entry.get(), client_window)).grid(row=5, column=1, pady=10)

    def ajouter_client(self, nom, prenom, age, email, telephone, window):
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
        titre = self.titre_entry.get().strip()
        isbn = self.isbn_entry.get().strip()
        langue = self.langue_var.get() if self.langue_var.get() != "Tous" else None
        type_livre = self.type_var.get() if self.type_var.get() != "Tous" else None
        sujet = self.sujet_var.get() if self.sujet_var.get() != "Tous" else None
        editeur = self.editeur_var.get() if self.editeur_var.get() != "Tous" else None

        if not titre and not isbn:
            messagebox.showwarning("Erreur", "Veuillez entrer un titre ou un ISBN.")
            return

        logger.info(f"Recherche : titre={titre}, isbn={isbn}, langue={langue}, type={type_livre}, sujet={sujet}, editeur={editeur}")
        self.rechercher_btn.config(state="disabled", text="Recherche en cours...")
        self.update()

        livres_trouves = rechercher_livres_par_titre_ou_isbn(titre=titre, isbn=isbn, langue=langue,
                                                             type_livre=type_livre, sujet=sujet, editeur=editeur)
        logger.info(f"Résultats trouvés : {len(livres_trouves)} livres")
        self.afficher_resultats(livres_trouves)

        self.rechercher_btn.config(state="normal", text="Rechercher")

    def effacer_recherche(self):
        self.titre_entry.delete(0, tk.END)
        self.isbn_entry.delete(0, tk.END)
        self.langue_var.set("Tous")
        self.type_var.set("Tous")
        self.sujet_var.set("Tous")
        self.editeur_var.set("Tous")
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def ajouter_au_panier(self, livre):
        self.panier.append(livre)
        messagebox.showinfo("Panier", f"{livre.titre} ajouté au panier !")

    def afficher_resultats(self, livres):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not livres:
            tk.Label(self.scrollable_frame, text="Aucun résultat trouvé", font=STYLES["font_label"],
                     bg=STYLES["bg"], fg=STYLES["fg"]).pack(pady=20)
            return

        for livre in livres:
            card_frame = tk.Frame(self.scrollable_frame, bg=STYLES["card_bg"], bd=1, relief="solid", padx=10, pady=10)
            card_frame.pack(fill="x", padx=10, pady=5)

            titre_label = tk.Label(card_frame, text=livre.titre, font=("Helvetica", 14, "bold"),
                                   bg=STYLES["card_bg"], fg=STYLES["fg"], wraplength=600, justify="left")
            titre_label.pack(anchor="w", pady=(0, 3))
            titre_label.bind("<Enter>", lambda e, l=titre_label: l.config(fg=STYLES["highlight"]))
            titre_label.bind("<Leave>", lambda e, l=titre_label: l.config(fg=STYLES["fg"]))

            tk.Label(card_frame, text=f"Auteur(s) : {livre.auteur}", font=STYLES["font_label"],
                     bg=STYLES["card_bg"], fg=STYLES["fg"]).pack(anchor="w")
            tk.Label(card_frame, text=f"ISBN : {livre.isbn}", font=STYLES["font_label"],
                     bg=STYLES["card_bg"], fg=STYLES["fg"]).pack(anchor="w")
            tk.Label(card_frame, text=f"Prix : {livre.prix_formate}", font=STYLES["font_label"],
                     bg=STYLES["card_bg"], fg=STYLES["fg"]).pack(anchor="w")
            tk.Label(card_frame, text=f"Éditeur : {livre.editeur} | Langue : {livre.langue}", font=STYLES["font_label"],
                     bg=STYLES["card_bg"], fg=STYLES["fg"]).pack(anchor="w")

            tk.Button(card_frame, text="Ajouter au panier", font=STYLES["font_button"],
                      bg=STYLES["button_bg"], fg=STYLES["button_fg"], relief="flat",
                      command=lambda l=livre: self.ajouter_au_panier(l)).pack(anchor="e", pady=5)

    def voir_panier(self):
        if not self.panier:
            messagebox.showinfo("Panier", "Le panier est vide.")
            return

        panier_window = tk.Toplevel(self)
        panier_window.title("Mon Panier")
        panier_window.geometry("800x600")
        panier_window.configure(bg=STYLES["bg"])

        panier_frame = tk.Frame(panier_window, bg=STYLES["bg"])
        panier_frame.pack(pady=10, fill="both", expand=True)

        tk.Label(panier_frame, text="Contenu du Panier", font=STYLES["font_title"],
                 bg=STYLES["bg"], fg=STYLES["fg"]).pack(pady=(0, 10))

        canvas = tk.Canvas(panier_frame, bg=STYLES["bg"])
        scrollbar = ttk.Scrollbar(panier_frame, orient="vertical", command=canvas.yview)
        scrollable_content = tk.Frame(canvas, bg=STYLES["bg"])

        scrollable_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, livre in enumerate(self.panier):
            item_frame = tk.Frame(scrollable_content, bg=STYLES["card_bg"], bd=1, relief="solid", padx=10, pady=10)
            item_frame.pack(fill="x", padx=5, pady=5)

            tk.Label(item_frame, text=f"{livre.titre} - {livre.auteur}", font=STYLES["font_label"],
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
        client_options = [f"{c[1]} {c[2]} ({c[3]})" for c in clients] if clients else ["Aucun client"]
        tk.OptionMenu(client_frame, self.client_var, *client_options).pack(side="left", padx=5)

        tk.Button(client_frame, text="Valider la commande", font=STYLES["font_button"],
                  bg=STYLES["order_bg"], fg=STYLES["button_fg"], relief="flat",
                  command=lambda: self.valider_commande(clients, panier_window)).pack(side="left", padx=5)

    def supprimer_du_panier(self, index, window):
        if 0 <= index < len(self.panier):
            livre = self.panier.pop(index)
            messagebox.showinfo("Panier", f"{livre.titre} supprimé du panier.")
            window.destroy()
            self.voir_panier()

    def valider_commande(self, clients, window):
        if not self.panier:
            messagebox.showwarning("Erreur", "Le panier est vide.")
            return
        if not clients:
            messagebox.showwarning("Erreur", "Aucun client disponible.")
            return

        client_selection = self.client_var.get()
        client_id = next((c[0] for c in clients if f"{c[1]} {c[2]} ({c[3]})" == client_selection), None)
        if not client_id:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un client valide.")
            return

        if enregistrer_commande(client_id, self.panier):
            messagebox.showinfo("Succès", f"Commande validée pour {client_selection} !")
            self.panier.clear()
            window.destroy()
        else:
            messagebox.showerror("Erreur", "Échec de l'enregistrement de la commande.")