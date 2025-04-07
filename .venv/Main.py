import tkinter as tk
from tkinter import messagebox, ttk
import requests
from PIL import Image, ImageTk
import io
from datetime import datetime

class Livre:
    def __init__(self, titre, auteur, couverture=None, isbn=None, date_publication=None, synopsis=None):
        self.titre = titre
        self.auteur = auteur
        self.couverture = couverture
        self.isbn = isbn or "Non disponible"
        self.date_publication = date_publication or "Date inconnue"
        self.synopsis = synopsis or "Synopsis non disponible"

    def __str__(self):
        return f"{self.titre} de {self.auteur}"

def rechercher_livres_par_titre_ou_isbn(titre=None, isbn=None, langue=None, type_livre=None, sujet=None, editeur=None, sort_by="relevance"):
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
                isbn_result = next((id["identifier"] for id in info.get("industryIdentifiers", []) if id["type"] == "ISBN_13"), None)
                date_publication = info.get("publishedDate")
                synopsis = info.get("description")
                livres.append(Livre(titre_livre, auteur_livre, couverture, isbn_result, date_publication, synopsis))
            return livres
        else:
            messagebox.showinfo("Résultat", "Aucun livre trouvé.")
            return []
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erreur", f"Erreur API : {str(e)}")
        return []

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bibliothèque Moderne - Google Books")
        self.attributes('-fullscreen', True)
        self.configure(bg="#2C3E50")

        self.style = {
            "bg": "#ECF0F1",
            "fg": "#2C3E50",
            "button_bg": "#3498DB",
            "button_fg": "#FFFFFF",
            "entry_bg": "#FFFFFF",
            "font_title": ("Helvetica", 20, "bold"),
            "font_label": ("Helvetica", 12),
            "font_button": ("Helvetica", 12, "bold"),
            "card_bg": "#FFFFFF",
            "card_border": "#E0E0E0",
            "highlight": "#3498DB",
            "order_bg": "#2ECC71",
            "menu_bg": "#34495E",  # Bleu nuit pour la barre de menu
            "menu_border": "#2C3E50"
        }

        self.panier = []
        self.creer_widgets()

    def creer_widgets(self):
        main_frame = tk.Frame(self, bg=self.style["bg"], padx=20, pady=20, bd=2, relief="raised")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(main_frame, text="Recherche de Livres - Google Books",
                 font=self.style["font_title"], bg=self.style["bg"], fg=self.style["fg"]).pack(pady=(0, 20))

        # Barre de menu améliorée
        search_frame = tk.Frame(main_frame, bg=self.style["menu_bg"], padx=15, pady=15, bd=2, relief="groove",
                                highlightbackground=self.style["menu_border"], highlightthickness=2)
        search_frame.pack(fill="x", pady=10)

        # Ligne 1 : Titre et ISBN
        ligne1_frame = tk.Frame(search_frame, bg=self.style["menu_bg"])
        ligne1_frame.pack(fill="x", pady=5)

        tk.Label(ligne1_frame, text="Titre :", font=self.style["font_label"], bg=self.style["menu_bg"],
                 fg=self.style["button_fg"]).pack(side="left", padx=5)
        self.titre_entry = tk.Entry(ligne1_frame, font=self.style["font_label"], bg=self.style["entry_bg"],
                                    relief="flat", bd=2, width=30)
        self.titre_entry.pack(side="left", padx=5)

        tk.Label(ligne1_frame, text="ISBN :", font=self.style["font_label"], bg=self.style["menu_bg"],
                 fg=self.style["button_fg"]).pack(side="left", padx=5)
        self.isbn_entry = tk.Entry(ligne1_frame, font=self.style["font_label"], bg=self.style["entry_bg"],
                                   relief="flat", bd=2, width=20)
        self.isbn_entry.pack(side="left", padx=5)
        self.isbn_entry.bind("<Return>", self.recherche_auto_isbn)  # Déclenche la recherche sur "Entrée"

        # Ligne 2 : Langue et Type
        ligne2_frame = tk.Frame(search_frame, bg=self.style["menu_bg"])
        ligne2_frame.pack(fill="x", pady=5)

        tk.Label(ligne2_frame, text="Langue :", font=self.style["font_label"], bg=self.style["menu_bg"],
                 fg=self.style["button_fg"]).pack(side="left", padx=5)
        self.langue_var = tk.StringVar(value="all")
        langue_menu = ttk.Combobox(ligne2_frame, textvariable=self.langue_var, state="readonly", width=10,
                                   values=["all", "fr", "en", "es", "de"])
        langue_menu.pack(side="left", padx=5)

        tk.Label(ligne2_frame, text="Type :", font=self.style["font_label"], bg=self.style["menu_bg"],
                 fg=self.style["button_fg"]).pack(side="left", padx=5)
        self.type_var = tk.StringVar(value="all")
        type_menu = ttk.Combobox(ligne2_frame, textvariable=self.type_var, state="readonly", width=10,
                                 values=["all", "books", "magazines"])
        type_menu.pack(side="left", padx=5)

        # Ligne 3 : Sujet et Éditeur
        ligne3_frame = tk.Frame(search_frame, bg=self.style["menu_bg"])
        ligne3_frame.pack(fill="x", pady=5)

        tk.Label(ligne3_frame, text="Sujet :", font=self.style["font_label"], bg=self.style["menu_bg"],
                 fg=self.style["button_fg"]).pack(side="left", padx=5)
        self.sujet_var = tk.StringVar(value="all")
        sujet_menu = ttk.Combobox(ligne3_frame, textvariable=self.sujet_var, state="readonly", width=20,
                                  values=["all", "Fiction", "Non-fiction", "Fantasy", "Science-fiction", "Mystery",
                                          "Romance", "Thriller", "Biography", "History", "Science", "Cooking",
                                          "Children", "Young Adult", "Poetry"])
        sujet_menu.pack(side="left", padx=5)

        tk.Label(ligne3_frame, text="Éditeur :", font=self.style["font_label"], bg=self.style["menu_bg"],
                 fg=self.style["button_fg"]).pack(side="left", padx=5)
        self.editeur_var = tk.StringVar(value="all")
        editeur_menu = ttk.Combobox(ligne3_frame, textvariable=self.editeur_var, state="readonly", width=20,
                                    values=["all", "Penguin", "Hachette", "Scholastic", "Random House", "HarperCollins",
                                            "Simon & Schuster", "Macmillan", "Gallimard", "Flammarion", "Oxford University Press",
                                            "Cambridge University Press", "Pearson", "Wiley", "Bloomsbury"])
        editeur_menu.pack(side="left", padx=5)

        # Ligne 4 : Boutons
        ligne4_frame = tk.Frame(search_frame, bg=self.style["menu_bg"])
        ligne4_frame.pack(fill="x", pady=5)

        self.rechercher_btn = tk.Button(ligne4_frame, text="Rechercher", font=self.style["font_button"],
                                        bg=self.style["button_bg"], fg=self.style["button_fg"],
                                        relief="flat", padx=15, pady=5, command=self.rechercher_livres)
        self.rechercher_btn.pack(side="left", padx=10)

        self.clear_btn = tk.Button(ligne4_frame, text="Effacer", font=self.style["font_button"],
                                   bg="#E74C3C", fg=self.style["button_fg"], relief="flat", padx=15, pady=5,
                                   command=self.effacer_recherche)
        self.clear_btn.pack(side="left", padx=5)

        self.panier_btn = tk.Button(ligne4_frame, text="Voir Panier (0)", font=self.style["font_button"],
                                    bg="#F1C40F", fg=self.style["button_fg"], relief="flat", padx=15, pady=5,
                                    command=self.voir_panier)
        self.panier_btn.pack(side="right", padx=5)

        self.results_frame = tk.Frame(main_frame, bg=self.style["bg"])
        self.results_frame.pack(pady=20, fill="both", expand=True)

        canvas = tk.Canvas(self.results_frame, bg=self.style["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=self.style["bg"])

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

    def rechercher_livres(self):
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

    def recherche_auto_isbn(self, event):
        isbn = self.isbn_entry.get().strip()
        if isbn:  # Si un ISBN est saisi
            self.rechercher_btn.config(state="disabled", text="Recherche en cours...")
            self.update()
            livres_trouves = rechercher_livres_par_titre_ou_isbn(isbn=isbn)
            self.afficher_resultats(livres_trouves)
            self.rechercher_btn.config(state="normal", text="Rechercher")

    def effacer_recherche(self):
        self.titre_entry.delete(0, tk.END)
        self.isbn_entry.delete(0, tk.END)
        self.langue_var.set("all")
        self.type_var.set("all")
        self.sujet_var.set("all")
        self.editeur_var.set("all")
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def commander_livre(self, livre):
        confirmation = messagebox.askyesno("Confirmation", f"Commander '{livre.titre}' par {livre.auteur} ?\nISBN: {livre.isbn}")
        if confirmation:
            self.panier.append(livre)
            self.panier_btn.config(text=f"Voir Panier ({len(self.panier)})")
            messagebox.showinfo("Succès", f"'{livre.titre}' a été ajouté au panier !")

    def voir_panier(self):
        if not self.panier:
            messagebox.showinfo("Panier", "Votre panier est vide.")
            return

        panier_window = tk.Toplevel(self)
        panier_window.title("Votre Panier")
        panier_window.geometry("600x400")
        panier_window.configure(bg=self.style["bg"])

        tk.Label(panier_window, text="Votre Panier", font=self.style["font_title"],
                 bg=self.style["bg"], fg=self.style["fg"]).pack(pady=10)

        canvas = tk.Canvas(panier_window, bg=self.style["bg"])
        scrollbar = ttk.Scrollbar(panier_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.style["bg"])

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for livre in self.panier:
            item_frame = tk.Frame(scrollable_frame, bg=self.style["card_bg"], bd=1, relief="solid", padx=10, pady=10)
            item_frame.pack(fill="x", padx=5, pady=5)

            tk.Label(item_frame, text=f"{livre.titre}", font=("Helvetica", 14, "bold"),
                     bg=self.style["card_bg"], fg=self.style["fg"]).pack(anchor="w")
            tk.Label(item_frame, text=f"Auteur(s) : {livre.auteur}", font=self.style["font_label"],
                     bg=self.style["card_bg"], fg=self.style["fg"]).pack(anchor="w")
            tk.Label(item_frame, text=f"ISBN : {livre.isbn}", font=self.style["font_label"],
                     bg=self.style["card_bg"], fg=self.style["fg"]).pack(anchor="w")

        tk.Button(panier_window, text="Vider le panier", font=self.style["font_button"],
                  bg="#E74C3C", fg=self.style["button_fg"], relief="flat", padx=10, pady=5,
                  command=lambda: self.vider_panier(panier_window)).pack(pady=10)

    def vider_panier(self, window):
        self.panier.clear()
        self.panier_btn.config(text="Voir Panier (0)")
        window.destroy()
        messagebox.showinfo("Panier", "Le panier a été vidé.")

    def afficher_resultats(self, livres):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not livres:
            tk.Label(self.scrollable_frame, text="Aucun résultat trouvé", font=self.style["font_label"],
                     bg=self.style["bg"], fg=self.style["fg"]).pack(pady=20)
            return

        for livre in livres:
            card_frame = tk.Frame(self.scrollable_frame, bg=self.style["card_bg"], bd=1,
                                  relief="solid", padx=15, pady=15)
            card_frame.pack(fill="x", padx=10, pady=5)

            titre_label = tk.Label(card_frame, text=livre.titre, font=("Helvetica", 16, "bold"),
                                   bg=self.style["card_bg"], fg=self.style["fg"], wraplength=600, justify="left")
            titre_label.pack(anchor="w", pady=(0, 5))
            titre_label.bind("<Enter>", lambda e, l=titre_label: l.config(fg=self.style["highlight"]))
            titre_label.bind("<Leave>", lambda e, l=titre_label: l.config(fg=self.style["fg"]))

            tk.Label(card_frame, text=f"Auteur(s) : {livre.auteur}", font=self.style["font_label"],
                     bg=self.style["card_bg"], fg=self.style["fg"]).pack(anchor="w", pady=2)
            tk.Label(card_frame, text=f"ISBN : {livre.isbn}", font=self.style["font_label"],
                     bg=self.style["card_bg"], fg=self.style["fg"]).pack(anchor="w", pady=2)
            tk.Label(card_frame, text=f"Date : {livre.date_publication}", font=self.style["font_label"],
                     bg=self.style["card_bg"], fg=self.style["fg"]).pack(anchor="w", pady=2)
            tk.Label(card_frame, text=f"Synopsis : {livre.synopsis[:150]}{'...' if len(livre.synopsis) > 150 else ''}",
                     font=self.style["font_label"], bg=self.style["card_bg"], fg=self.style["fg"],
                     wraplength=600, justify="left").pack(anchor="w", pady=2)

            tk.Button(card_frame, text="Commander", font=self.style["font_button"],
                      bg=self.style["order_bg"], fg=self.style["button_fg"], relief="flat", padx=10, pady=5,
                      command=lambda l=livre: self.commander_livre(l)).pack(anchor="w", pady=5)

            if livre.couverture:
                try:
                    response = requests.get(livre.couverture, timeout=5)
                    response.raise_for_status()
                    image = Image.open(io.BytesIO(response.content))
                    image = image.resize((120, 180), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    img_label = tk.Label(card_frame, image=photo, bg=self.style["card_bg"])
                    img_label.image = photo
                    img_label.pack(side="right", padx=10)
                except Exception as e:
                    tk.Label(card_frame, text="Image indisponible", font=self.style["font_label"],
                             bg=self.style["card_bg"], fg=self.style["fg"]).pack(side="right", padx=10)
            else:
                tk.Label(card_frame, text="Image indisponible", font=self.style["font_label"],
                         bg=self.style["card_bg"], fg=self.style["fg"]).pack(side="right", padx=10)

if __name__ == "__main__":
    app = Application()
    app.mainloop()