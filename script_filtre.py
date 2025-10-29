import requests
import os
import json

# --- 1. CONFIGURATION ---

# Vos mots-clés pour le filtre "pré-embauche"
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

# Récupérer les clés depuis les Secrets GitHub
CLIENT_ID = os.environ.get('FT_CLIENT_ID')
CLIENT_SECRET = os.environ.get('FT_SECRET')

if not CLIENT_ID or not CLIENT_SECRET:
    raise Exception("Erreur: FT_CLIENT_ID ou FT_SECRET non défini.")

# --- 2. OBTENIR LE TOKEN D'ACCÈS ---

print("Tentative d'obtention du token d'accès...")
# CORRECTION FINALE : LE BON SERVEUR D'AUTH (api.francetravail.io)
auth_url = "https://api.francetravail.io/connexion/oauth2/access_token?realm=/partenaire"
auth_data = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "scope": "o2dsoffre api_offresdemploi" # LES BONS SCOPES (de votre capture d'écran)
}
auth_response = requests.post(auth_url, data=auth_data, timeout=30)

if auth_response.status_code != 200:
    print(f"ÉCHEC DE L'AUTHENTIFICATION.")
    print(f"Code de statut reçu: {auth_response.status_code}")
    print(f"Réponse détaillée du serveur: {auth_response.text}")
    raise Exception("Erreur d'authentification à l'API France Travail. Voir détails ci-dessus.")

ACCESS_TOKEN = auth_response.json()["access_token"]
print("Token d'accès obtenu.") # <-- C'EST CE QUE NOUS VOULONS VOIR !

# --- 3. RECHERCHER LES OFFRES DE STAGE ---

print("Recherche des offres de stage...")
# LA BONNE URL DE RECHERCHE (v2)
search_url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}
params = {
    "typeContrat": "STY",  # STY = Stage
    "range": "0-149",
    "sort": 1
}

search_response = requests.get(search_url, headers=headers, params=params, timeout=30)

if search_response.status_code != 200:
    print(f"Erreur lors de la recherche d'offres. Statut: {search_response.status_code}")
    print(f"Réponse: {search_response.text}")
    raise Exception(f"Erreur lors de la recherche d'offres.")

offres_brutes = search_response.json().get("resultats", [])
print(f"{len(offres_brutes)} offres de stage trouvées.")

# --- 4. FILTRER LES OFFRES ---

stages_filtres = []

for offre in offres_brutes:
    titre = offre.get("intitule", "").lower()
    description = offre.get("description", "").lower()
    texte_complet = titre + " " + description
    
    if any(keyword in texte_complet for keyword in KEYWORDS):
        stage_propre = {
            "id": offre.get("id"),
            "titre": offre.get("intitule"),
            "entreprise": offre.get("entreprise", {}).get("nom", "Non précisé"),
            "lieu": offre.get("lieuTravail", {}).get("libelle", "Non précisé"),
            "url": offre.get("origineOffre", {}).get("urlOrigine", "#")
        }
        stages_filtres.append(stage_propre)

print(f"{len(stages_filtres)} offres de stage filtrées (pré-embauche).")

# --- 5. SAUVEGARDER DANS LE FICHIER JSON ---

output_filename = "stages_filtres.json" 

with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(stages_filtres, f, indent=2, ensure_ascii=False)

print(f"Fichier '{output_filename}' sauvegardé avec succès.")