import os
import time
import smtplib  # supprimez cette ligne si vous utilisez SendGrid
import requests
import google.generativeai as genai
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
BLOG_EMAIL = os.environ["BLOG_EMAIL"]
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")  # optionnel, selon votre choix
GMAIL_USER = os.environ["GMAIL_USER"]

NICHE = "plantes d'intérieur faciles"
PROMPT = f"""
Rédige un article de blog de 500 mots en français sur le thème '{NICHE}'.
L'article doit être informatif, bien structuré (titre, sous-titres, paragraphes),
sur un ton amical. Inclus une introduction et une conclusion.
Le titre doit être accrocheur. N'indique pas que c'est une IA qui écrit.
Retourne le résultat au format JSON avec les clés "titre" et "contenu".
Le contenu doit être en HTML simple (utilise <h2>, <p>, <ul>).
"""

def generer_article():
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    # Jusqu'à 3 tentatives avec attente croissante
    for i in range(3):
        try:
            response = model.generate_content(PROMPT)
            texte = response.text.strip()
            if texte.startswith("```json"):
                texte = texte[7:]
            if texte.endswith("```"):
                texte = texte[:-3]
            import json
            data = json.loads(texte)
            return data["titre"], data["contenu"]
        except Exception as e:
            print(f"Tentative {i+1} échouée : {e}")
            if i < 2:  # ne pas attendre après le dernier essai
                time.sleep(60)  # attendre 1 minute avant de réessayer
    raise Exception("Échec de génération après 3 tentatives")

def envoyer_article_sendgrid(titre, contenu_html):
    message = Mail(
        from_email=GMAIL_USER,
        to_emails=BLOG_EMAIL,
        subject=titre,
        html_content=contenu_html)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Article publié : {titre} (status {response.status_code})")
    except Exception as e:
        print(f"Erreur SendGrid : {e}")
        raise e

if __name__ == "__main__":
    try:
        titre, contenu = generer_article()
        envoyer_article_sendgrid(titre, contenu)
    except Exception as e:
        print(f"Échec final : {e}")
        exit(1)  # pour que GitHub Actions détecte l'échec
