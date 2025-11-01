import requests
import os
import json
import sys

# --- 1️⃣ CONFIGURATION DES MOTS-CLÉS ---
KEYWORDS = [
    "pré-embauche",
    "pre-embauche",
    "possibilité d'embauche",
    "embauche à l'issue",
    "cdi à la clé",
    "vue d'embauche",
    "stage concluant",
    "opportunité d'embauche"
]

# --- 2️⃣ VARIABLES D'ENVIRONNEMENT ---
CLIENT_ID = os.environ.get("FT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("FT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    sys.exit("❌ Erreur : variables FT_CLIENT_ID ou FT_SECRET non définies.")

# --- 3️⃣ AUTHENTIFICATION FRANCE TRAVAIL ---
print("🔐 Tentative d'obtention du token d'accès...")

auth_url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"
auth_data = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "scope": "api_offresdemploi o2dsoffre"
}

auth_response = requests.post(auth_url, data=auth_data, timeout=30)

if auth_response.status_code != 200:
    print("❌ Échec de l'authentification à l'API France Travail.")
    print(f"Code HTTP : {auth_response.status_code}")
    print("Réponse complète :", auth_response.text)
    sys.exit(1)

ACCESS_TOKEN = auth_response.json().get("access_token")
print("✅ Token d'accès obtenu avec succès.")

# --- 4️⃣ RECHERCHE DES OFFRES ---
print("🔍 Recherche des offres de stage...")

search_url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "User-Agent": "StagePreEmbaucheBot/1.0"
}
params = {
    "typeContrat": "STY",
    "range": "0-149",
    "sort": 1
}

search_response = requests.get(search_url, headers=headers, params=params, timeout=30)

if search_response.status_code != 200:
    print("❌ Erreur lors de la récupération des offres.")
    print("Réponse :", search_response.text)
    sys.exit(1)

offres = search_response.json().get("resultats", [])
print(f"📦 {len(offres)} offres de stage récupérées.")

# --- 5️⃣ FILTRAGE ---
stages_filtres = []
for offre in offres:
    texte = f"{offre.get('intitule', '').lower()} {offre.get('description', '').lower()}"
    if any(keyword in texte for keyword in KEYWORDS):
        stages_filtres.append({
            "id": offre.get("id"),
            "titre": offre.get("intitule"),
            "entreprise": offre.get("entreprise", {}).get("nom", "Non précisé"),
            "lieu": offre.get("lieuTravail", {}).get("libelle", "Non précisé"),
            "url": offre.get("origineOffre", {}).get("urlOrigine", "#")
        })

print(f"✅ {len(stages_filtres)} offres correspondent au filtre pré-embauche.")

# --- 6️⃣ SAUVEGARDE ---
output_filename = "stages_filtres.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(stages_filtres, f, ensure_ascii=False, indent=2)

print(f"💾 Fichier '{output_filename}' généré avec succès.")
