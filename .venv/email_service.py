"""Module pour l'envoi d'emails dans l'application GestionDejaLu."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_CONFIG
import logging

logger = logging.getLogger(__name__)

def send_order_confirmation_email(client_email: str, client_name: str, livres: list) -> bool:
    """Envoie un email de confirmation de commande au client.

    Args:
        client_email (str): Adresse email du client.
        client_name (str): Nom complet du client (prénom nom).
        livres (list): Liste d'objets Livre dans la commande.

    Returns:
        bool: True si l'email est envoyé avec succès, False sinon.
    """
    try:
        # Vérifier les paramètres SMTP
        if not SMTP_CONFIG["user"] or not SMTP_CONFIG["password"]:
            logger.error("Paramètres SMTP manquants : utilisateur ou mot de passe non défini.")
            return False

        # Créer le message
        msg = MIMEMultipart()
        msg["From"] = f"{SMTP_CONFIG['sender_name']} <{SMTP_CONFIG['sender_email']}>"
        msg["To"] = client_email
        msg["Subject"] = "Confirmation de votre commande - GestionDejaLu"

        # Contenu de l'email
        total_price = sum(livre.prix or 0 for livre in livres)
        body = f"""Bonjour {client_name},

Merci pour votre commande chez GestionDejaLu ! Voici les détails de votre commande :

Items commandés :
"""
        for livre in livres:
            body += f"- {livre.titre} par {livre.auteur} (ISBN: {livre.isbn or 'N/A'}) - {livre.prix_formate}\n"
        body += f"""
Montant total : {total_price:.2f} €

Nous vous contacterons bientôt pour la livraison. Si vous avez des questions, contactez-nous à {SMTP_CONFIG['sender_email']}.

Cordialement,
L'équipe GestionDejaLu
"""
        msg.attach(MIMEText(body, "plain"))

        # Connexion au serveur SMTP
        with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as server:
            server.starttls()  # Activer TLS
            server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
            server.send_message(msg)

        logger.info(f"Email de confirmation envoyé à {client_email}.")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Erreur d'authentification SMTP pour {client_email} : {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"Erreur SMTP lors de l'envoi de l'email à {client_email} : {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'envoi de l'email à {client_email} : {e}")
        return False