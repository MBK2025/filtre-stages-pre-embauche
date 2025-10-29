import requests
import os
import json

# --- 1. CONFIGURATION ---

# Vos mots-clés pour le filtre "pré-embauche"
# Nous les mettons en minuscule pour faciliter la recherche
KEYWORDS = [
    "pré-embauche",
    "pre-embauche",
    "possibilité d'embauche",
    "embauche à l'issue",
    "cdi à la clé",
    "vue d'embauche",
    "stage concluant", # Souvent suivi de "en vue d'embauche"
    "opportunité d'embauche"
]

# Récupérer les clés depuis les Secrets GitHub
CLIENT_ID = os.environ.get('FT_CLIENT_ID')
CLIENT_SECRET = os.environ.get('FT_SECRET')

if not CLIENT_ID or not CLIENT_SECRET:
    raise Exception("Erreur: FT_CLIENT_ID ou FT_SECRET non défini.")

# --- 2. OBTENIR LE TOKEN D'ACCÈS ---

print("Tentative d'obtention du token d'accès...")
auth_url = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire"
auth_data = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "scope": "api_offresdemploi_v2" # <-- MODIFICATION IMPORTANTE ICI
}
auth_response = requests.post(auth_url, data=auth_data)

if auth_response.status_code != 200:
    # --- DÉBOGAGE AMÉLIORÉ ---
    print(f"ÉCHEC DE L'AUTHENTIFICATION.")
    print(f"Code de statut reçu: {auth_response.status_code}")
    print(f"Réponse détaillée du serveur: {auth_response.text}") # Ceci va nous dire le VRAI problème
    # --- FIN DÉBOGAGE ---
    raise Exception("Erreur d'authentification à l'API France Travail. Voir détails ci-dessus.")

ACCESS_TOKEN = auth_response.json()["access_token"]
print("Token d'accès obtenu.")

# --- 3. RECHERCHER LES OFFRES DE STAGE ---

print("Recherche des offres de stage...")
search_url = "https://api.emploi-store.fr/partenaire/offresdemploi/v2/offres/search"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}
params = {
    "typeContrat": "STY",  # STY = Stage
    "range": "0-149",      # Demande les 150 dernières offres
    "sort": 1              # 1 = trier par date de publication (plus récent)
}

search_response = requests.get(search_url, headers=headers, params=params)

if search_response.status_code != 200:
    print(f"Erreur lors de la recherche d'offres. Statut: {search_response.status_code}")
    print(f"Réponse: {search_response.text}")
    raise Exception(f"Erreur lors de la recherche d'offres.")

offres_brutes = search_response.json().get("resultats", [])
print(f"{len(offres_brutes)} offres de stage trouvées.")

# --- 4. FILTRER LES OFFRES ---

stages_filtres = []

for offre in offres_brutes:
    # Combiner le titre et la description pour la recherche de mots-clés
    titre = offre.get("intitule", "").lower()
    description = offre.get("description", "").lower()
    texte_complet = titre + " " + description
    
    # Vérifier si un de nos mots-clés est présent
    if any(keyword in texte_complet for keyword in KEYWORDS):
        # Si oui, on garde cette offre
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

# Nom du fichier que notre interface lira
output_filename = "stages_filtres.json" 

with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(stages_filtres, f, indent=2, ensure_ascii=False)

print(f"Fichier '{output_filename}' sauvegardé avec succès.")