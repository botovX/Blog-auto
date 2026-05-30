import os
import smtplib
from email.mime.text import MIMEText
import google.generativeai as genai

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
BLOG_EMAIL = os.environ["BLOG_EMAIL"]
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]

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
    response = model.generate_content(PROMPT)
    texte = response.text.strip()
    if texte.startswith("```json"):
        texte = texte[7:]
    if texte.endswith("```"):
        texte = texte[:-3]
    import json
    data = json.loads(texte)
    return data["titre"], data["contenu"]

def envoyer_article(titre, contenu):
    msg = MIMEText(contenu, "html", "utf-8")
    msg["Subject"] = titre
    msg["From"] = GMAIL_USER
    msg["To"] = BLOG_EMAIL
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, BLOG_EMAIL, msg.as_string())
    print(f"Article publié : {titre}")

if __name__ == "__main__":
    titre, contenu = generer_article()
    envoyer_article(titre, contenu)
