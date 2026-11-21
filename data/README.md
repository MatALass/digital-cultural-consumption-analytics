# Données

## `raw/` : fichiers de l'Arcom, non modifiés

| Fichier | Contenu |
|---|---|
| `2024-barometre-consommation.xlsx` | Fichier individuel : 5 041 répondants, 1 518 colonnes, une ligne par répondant (colonne `ID`) |
| `2024-datamap.xlsx` | Dictionnaire des variables (feuilles VARIABLES et TEXTS : intitulés et codes) |

Source : Arcom, *Consommation des contenus culturels et sportifs numériques - Baromètre*, publié sur data.gouv.fr sous Licence Ouverte 2.0. Enquête réalisée par Ifop en avril-mai 2024. Crédit obligatoire : Arcom.

Le fichier ne contient ni nom, ni adresse, ni texte libre : uniquement un identifiant anonyme et des réponses codées.

## `processed/` : tables d'analyse

Produites par `dcca build` à partir de `raw/`. Elles sont versionnées pour que le dashboard démarre sans relire l'Excel (une dizaine de secondes). Le test `test_processed_tables_are_up_to_date` vérifie en CI qu'elles correspondent exactement au brut.

## `geo/regions.geojson`

Contours simplifiés des 13 régions métropolitaines, repris de [france-geojson](https://github.com/gregoiredavid/france-geojson) (données Admin Express, Licence Ouverte).
