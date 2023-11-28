import requests
import json
import numpy as np
import matplotlib.pyplot as plt
import csv

url = "http://localhost:8000/rankings/2023"

# Envoi de la requête GET
response = requests.get(url)

# Vérifier le code de statut de la réponse
if response.status_code == 200:
    # Convertir la réponse JSON en une structure de données Python
    data = json.loads(response.text)

    # Dictionnaire pour stocker le classement total, le nombre d'occurrences, et d'autres mesures pour chaque manga
    classement_total = {}
    nombre_occurrences = {}
    classements = {}
    premieres_places = {}
    top3 = {}
    bottom3 = {}
    derniers_classements = {}

    # Parcourir chaque semaine de classement
    for semaine in data["rankings"]:
        # Parcourir chaque classement de la semaine
        for index, classement in enumerate(semaine["ranking"], start=1):  # commence à 1 pour refléter la position dans le tableau
            nom_manga = classement["name"]
            classement_manga = index  # utilisez l'index comme classement
            taille_classement = len(semaine["ranking"])

            # Mettre à jour le classement total, le nombre d'occurrences, et la liste des classements pour chaque manga
            if nom_manga in classement_total:
                classement_total[nom_manga] += classement_manga
                nombre_occurrences[nom_manga] += 1
            else:
                classement_total[nom_manga] = classement_manga
                nombre_occurrences[nom_manga] = 1
            if nom_manga not in classements:
                classements[nom_manga] = []
            classements[nom_manga].append((semaine["week"], classement_manga, taille_classement))  # Inversion de la semaine et du placement

            # Mettre à jour le nombre de première place, top 3 et bottom 3 pour chaque manga
            if classement_manga == 1:
                premieres_places[nom_manga] = premieres_places.get(nom_manga, 0) + 1
            if classement_manga <= 3:
                top3[nom_manga] = top3.get(nom_manga, 0) + 1
            if classement_manga > len(semaine["ranking"]) - 3:
                bottom3[nom_manga] = bottom3.get(nom_manga, 0) + 1

            # Mettre à jour les 5 derniers classements de chaque manga avec la semaine
            if nom_manga not in derniers_classements:
                derniers_classements[nom_manga] = []
            derniers_classements[nom_manga].append((semaine["week"], classement_manga, taille_classement))
            derniers_classements[nom_manga] = derniers_classements[nom_manga][-5:]

    # Calculer la moyenne, l'écart type, l'étendue et l'IQR des classements pour chaque manga
    moyennes = {manga: np.mean([c[1] for c in classements[manga]]) for manga in classements}
    ecarts_types = {manga: np.std([c[1] for c in classements[manga]]) for manga in classements}
    etendues = {manga: np.ptp([c[1] for c in classements[manga]]) for manga in classements}
    iqrs = {manga: np.percentile([c[1] for c in classements[manga]], 75) - np.percentile([c[1] for c in classements[manga]], 25) for manga in classements}

    # Ordonner les mangas par la moyenne de la plus haute à la plus basse
    mangas_ord = sorted(moyennes.keys(), key=lambda x: moyennes[x], reverse=True)

    # Afficher les moyennes et l'écart type sur le graphique
    fig, ax = plt.subplots()
    bar_width = 0.35
    index = np.arange(len(mangas_ord))
    bars1 = ax.bar(index, [moyennes[m] for m in mangas_ord], bar_width, label='Moyenne', color='green')
    bars2 = ax.bar(index + bar_width, [ecarts_types[m] for m in mangas_ord], bar_width, label='Écart type', color='blue')

    ax.set_xlabel('Mangas')
    ax.set_ylabel('Valeurs')
    ax.set_title('Moyennes et Écart type des classements par manga')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels([f"{m}\n({nombre_occurrences[m]})" for m in mangas_ord], rotation=45, ha='right')  # Inclinaison des titres
    ax.legend()

    # Afficher les valeurs sur le graphique
    for bar1, bar2 in zip(bars1, bars2):
        height1 = bar1.get_height()
        height2 = bar2.get_height()
        ax.text(bar1.get_x() + bar1.get_width() / 2, height1, round(height1, 2), ha='center', va='bottom')
        ax.text(bar2.get_x() + bar2.get_width() / 2, height2, round(height2, 2), ha='center', va='bottom')

    plt.show()

    # Enregistrez les statistiques dans un fichier CSV
    with open('statistiques_mangas.csv', 'w', newline='') as csvfile:
        fieldnames = ['Manga', 'Moyenne', 'Écart type', 'Étendue', 'IQR', 'Occurrences', 'Premières places', 'Top 3', 'Bottom 3', 'Derniers classements']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for manga in mangas_ord:
            writer.writerow({'Manga': manga, 'Moyenne': moyennes[manga], 'Écart type': ecarts_types[manga],
                             'Étendue': etendues[manga], 'IQR': iqrs[manga], 'Occurrences': nombre_occurrences[manga],
                             'Premières places': premieres_places.get(manga, 0), 'Top 3': top3.get(manga, 0),
                             'Bottom 3': bottom3.get(manga, 0), 'Derniers classements': derniers_classements[manga]})
            
    # Enregistrer un graphique pour chaque manga
    for manga in mangas_ord:
        # Extraire les classements et les semaines pour le manga
        classements_manga = [c[1] for c in classements[manga]]
        semaines_manga = [c[0] for c in classements[manga]]

        # Créer un graphique pour le manga
        fig, ax = plt.subplots()
        ax.plot(semaines_manga, classements_manga, marker='o', linestyle='-', label='Classement')
        
        # Ajouter un trait rouge pour la moyenne
        moyenne_manga = moyennes[manga]
        ax.axhline(y=moyenne_manga, color='red', linestyle='--', label='Moyenne')

        ax.set_title(f'Classements de "{manga}" par semaine')
        ax.set_xlabel('Semaine')
        ax.set_ylabel('Classement')
        ax.invert_yaxis()  # Inverser l'axe y pour représenter le classement correctement
        ax.legend()

        # Enregistrer le graphique dans un fichier PNG
        filename = f'{manga}_classements.png'
        plt.savefig(filename)
        plt.close()
else:
    print(f"La requête a échoué avec le code de statut {response.status_code}")