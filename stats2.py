import requests
import json
import numpy as np
import matplotlib.pyplot as plt
import csv

def get_rankings(year):
    url = f"https://wsj.fly.dev/rankings/{year}"
    response = requests.get(url)

    if response.status_code == 200:
        data = json.loads(response.text)
        return data["rankings"]
    else:
        print(f"La requête pour l'année {year} a échoué avec le code de statut {response.status_code}")
        return []

# Récupérer les classements pour 2024
rankings_2024 = get_rankings(2024)
all_rankings = rankings_2024

# Obtenir la dernière semaine de classement
derniere_semaine = all_rankings[-1] if all_rankings else None

if derniere_semaine:
    # Extraire les mangas de la dernière semaine de classement et inverser l'ordre
    classement_derniere_semaine = [manga["name"] for manga in reversed(derniere_semaine.get("ranking", []))]

    # Extraire les pages couleurs de la dernière semaine
    pages_couleurs_derniere_semaine = [manga["rank"]["name"] for manga in derniere_semaine.get("color_pages", [])]

    # Écriture du résumé dans un fichier texte
    with open('classement_resume.txt', 'w') as fichier:
        fichier.write("Pages couleurs:\n")
        fichier.write('\n'.join(f"- {manga}" for manga in pages_couleurs_derniere_semaine) + "\n\n")
        fichier.write("Classement :\n")
        
        total_mangas = len(classement_derniere_semaine)
        for index, manga in enumerate(classement_derniere_semaine):
            position = total_mangas - index  # Calcul de la position inverse
            fichier.write(f"{position} {manga}\n")

    print("Le fichier classement_resume.txt a été généré avec succès.")
else:
    print("Aucune donnée de classement disponible pour générer un résumé.")
