"""Chemins, codes du questionnaire et libellés courts utilisés partout.

Les codes viennent du dictionnaire de l'Arcom (data/raw/2024-datamap.xlsx).
Les libellés sont raccourcis pour les graphiques ; tests/test_codebook.py
vérifie qu'ils couvrent bien les codes du dictionnaire.
"""

from __future__ import annotations

from pathlib import Path

def _find_project_root() -> Path:
    """Retrouve la racine du dépôt, indépendamment de l'installation du package."""

    current = Path.cwd().resolve()

    for candidate in (current, *current.parents):
        if (
            (candidate / "pyproject.toml").is_file()
            and (candidate / "data").is_dir()
        ):
            return candidate

    raise RuntimeError(
        "Impossible de localiser la racine du projet "
        "depuis le répertoire courant."
    )


PROJECT_ROOT = _find_project_root()
DATA_DIR = PROJECT_ROOT / "data"
RAW_SURVEY_PATH = DATA_DIR / "raw" / "2024-barometre-consommation.xlsx"
DATAMAP_PATH = DATA_DIR / "raw" / "2024-datamap.xlsx"
PROCESSED_DIR = DATA_DIR / "processed"
GEOJSON_PATH = DATA_DIR / "geo" / "regions.geojson"

RESPONDENTS_FILE = "repondants.parquet"
CONTENTS_FILE = "contenus.parquet"
SUBSCRIPTIONS_FILE = "abonnements.parquet"
ILLICIT_MEANS_FILE = "moyens_illicites.parquet"
REASONS_FILE = "raisons_illicite.parquet"

# Plafond de lecture des montants saisis : 999 est un code de saisie (une seule
# occurrence, au-dessus de toutes les autres valeurs), pas une dépense réelle.
SPENDING_SENTINELS = {999.0}

# --- Sociodémographie -------------------------------------------------------

SEX_LABELS = {1: "Homme", 2: "Femme"}

AGE_GROUP_LABELS = {  # RAGE2, les tranches des quotas Ifop
    1: "15-24 ans",
    2: "25-34 ans",
    3: "35-49 ans",
    4: "50-64 ans",
    5: "65 ans et plus",
}
AGE_GROUP_ORDER = list(AGE_GROUP_LABELS.values())

REGION_LABELS = {  # REG13 ; noms identiques au GeoJSON pour la carte
    1: "Grand Est",
    2: "Nouvelle-Aquitaine",
    3: "Auvergne-Rhône-Alpes",
    4: "Bourgogne-Franche-Comté",
    5: "Bretagne",
    6: "Centre-Val de Loire",
    7: "Corse",
    8: "Île-de-France",
    9: "Occitanie",
    10: "Hauts-de-France",
    11: "Normandie",
    12: "Pays de la Loire",
    13: "Provence-Alpes-Côte d'Azur",
}

AGGLOMERATION_LABELS = {  # AGGLO, vérifié contre les tranches d'unité urbaine INSEE
    1: "Commune rurale",
    2: "2 000 à 20 000 hab.",
    3: "20 000 à 100 000 hab.",
    4: "Plus de 100 000 hab.",
    5: "Agglomération parisienne",
}
AGGLOMERATION_ORDER = list(AGGLOMERATION_LABELS.values())

SITUATION_LABELS = {  # SITI
    1: "En activité",
    2: "Chômeur",
    3: "Retraité",
    4: "Premier emploi recherché",
    5: "Élève ou étudiant",
    6: "Au foyer",
    7: "Autre inactif",
}

CSP_LABELS = {  # RECPPIA
    1: "Agriculteurs",
    2: "Artisans, commerçants",
    3: "Cadres",
    4: "Professions intermédiaires",
    5: "Employés",
    6: "Ouvriers",
    7: "Retraités (ex-CSP+)",
    8: "Retraités (ex-CSP-)",
    9: "Élèves, étudiants",
    10: "Autres inactifs",
}

HOUSEHOLD_STATUS_LABELS = {  # STATUT
    1: "Enfant chez ses parents",
    2: "En couple",
    3: "Célibataire",
}

CHILDREN_LABELS = {1: "1", 2: "2", 3: "3", 4: "4 et plus", 5: "Aucun"}

INTERNET_FREQUENCY_LABELS = {  # RS6
    1: "Plusieurs fois par jour",
    2: "1 fois par jour ou presque",
    3: "3 à 5 fois par semaine",
    4: "1 à 2 fois par semaine",
    5: "2 à 3 fois par mois",
    6: "1 fois par mois",
    7: "Moins souvent",
}

# --- Contenus (grilles Q1, Q2, Q5, Q6, QBU1) -------------------------------

# Code de ligne dans les grilles -> libellé court. Les codes 10 (« Autres »)
# et 11 (« Aucun ») ne sont pas des contenus : ils n'ont pas de ligne de grille.
CONTENT_LABELS = {
    1: "Musique, clips",
    2: "Films",
    3: "Séries",
    4: "Photos",
    5: "Jeux vidéo",
    6: "Livres numériques, audio",
    7: "Logiciels",
    8: "Presse",
    9: "Sport en direct",
    12: "Podcasts",
    13: "Spectacles vivants",
    14: "Documentaires",
}
CONTENT_OTHER_CODE = 10
CONTENT_NONE_CODE = 11

FREQUENCY_LABELS = {  # L_Q2, utilisée par Q2, Q6 et QBU11
    1: "Tous les jours ou presque",
    2: "1 à 5 fois par semaine",
    3: "1 à 3 fois par mois",
    4: "Moins souvent",
}
FREQUENCY_ORDER = list(FREQUENCY_LABELS.values())

LEGALITY_LABELS = {  # Q5
    1: "Uniquement légal",
    2: "Surtout légal",
    3: "Autant légal qu'illégal",
    4: "Surtout illégal",
    5: "Uniquement illégal",
}
LEGALITY_ORDER = list(LEGALITY_LABELS.values())

PAYMENT_LABELS = {  # QBU1
    1: "Uniquement gratuit",
    2: "Surtout gratuit",
    3: "Autant gratuit que payant",
    4: "Surtout payant",
    5: "Uniquement payant",
}
PAYMENT_ORDER = list(PAYMENT_LABELS.values())

EVOLUTION_LABELS = {  # Q7
    1: "Plus de légal qu'avant",
    2: "Autant de légal qu'avant",
    3: "Moins de légal qu'avant",
    4: "Pas du tout de légal",
}

# --- Abonnements (RS12BIS, RS16BIS, RS17A) ----------------------------------

# Les lignes de RS12BIS n'ont pas de libellé dans le dictionnaire. Elles
# reprennent celles de RS16BIS_COLUMNS : les filtres AFRS16BISi<k> et
# AFRS17Ai<k> ont exactement les effectifs des colonnes c2 et c1 de la ligne k
# (vérifié dans tests/test_build.py).
SUBSCRIPTION_LABELS = {
    1: "Chaînes TV payantes",
    2: "Vidéo à la demande (SVOD)",
    3: "Musique en streaming",
    4: "Autre abonnement",
    5: "Jeux vidéo",
    6: "Presse en ligne",
    7: "Logiciels",
    8: "Livres numériques, audio",
    9: "Photos en ligne",
}
SUBSCRIPTION_STATUS_LABELS = {
    1: "Abonné dans le foyer",
    2: "Compte d'une personne extérieure",
    3: "Pas d'accès",
}
SUBSCRIPTION_STATUS_ORDER = list(SUBSCRIPTION_STATUS_LABELS.values())
# « Autre abonnement » est trop flou pour dire si la personne paie un contenu
# culturel : il est exclu de l'indicateur « abonné payant ».
PAID_SUBSCRIPTION_CODES = [1, 2, 3, 5, 6, 7, 8, 9]

SHARED_CODE_ORIGIN_LABELS = {  # RS16BIS
    1: "Famille",
    2: "Amis",
    3: "Codes trouvés sur Internet",
    4: "Autres personnes",
}
SHARED_CODE_ORIGIN_COLUMNS = {
    1: "codes_famille",
    2: "codes_amis",
    3: "codes_internet",
    4: "codes_autres",
}

# --- Pratiques de contournement --------------------------------------------

VPN_LABELS = {  # RS7BIS
    1: "Oui, régulièrement",
    2: "Oui, occasionnellement",
    3: "Plus maintenant",
    4: "Jamais",
}
DNS_LABELS = {  # RS8
    1: "Régulièrement",
    2: "De temps en temps",
    3: "Jamais",
    4: "Ne sait pas ce que c'est",
}
CRACKED_APP_LABELS = {  # QBU11C, choix multiples
    1: "Appli crackée TV payante",
    2: "Appli crackée SVOD",
    3: "Appli crackée musique",
    4: "N'utilise pas d'appli crackée",
    5: "Ne sait pas de quoi il s'agit",
}
ILLICIT_SENIORITY_LABELS = {  # QBU8
    1: "Moins d'un an",
    2: "1 à 3 ans",
    3: "3 à 5 ans",
    4: "Plus de 5 ans",
    5: "Ne sait pas",
}

# Moyens illicites (QBU10x). Chaque contenu a sa propre liste de moyens ; je
# garde les films et les séries, qui partagent la même liste (L_QBU10B) et
# concentrent le plus de consommateurs illicites.
ILLICIT_MEANS_QUESTIONS = {
    "QBU10b": 2,
    "QBU10c": 3,
}
ILLICIT_MEANS_LABELS = {
    1: "Sites de streaming",
    2: "Réseaux sociaux",
    3: "Pair-à-pair, torrent",
    4: "Téléchargement direct",
    5: "Convertisseurs (type YouTube to MP3)",
    6: "IPTV illicite",
    7: "Services de cloud",
    8: "Clés USB, disques de proches",
    9: "Usenet, newsgroups",
    10: "Autres moyens",
}

ILLICIT_REASON_LABELS = {  # QBU6
    1: "Prix à l'unité trop élevé",
    2: "Abonnements trop chers",
    3: "Sites légaux peu pratiques",
    4: "Offre légale trop limitée",
    5: "Œuvre introuvable en légal",
    6: "Nouveautés pas assez rapides",
    7: "Verrous numériques (DRM)",
    8: "Ne connaît pas de site légal",
    9: "Habitude du gratuit",
    10: "Peur de donner sa carte bancaire",
    11: "Pourquoi payer ce qui est gratuit ?",
    12: "Pas de moyen de paiement",
    13: "Sites légaux difficiles à trouver",
    14: "Contenu sans intérêt à garder",
    15: "Pas d'essai avant achat",
    16: "Autre raison",
    17: "Aucune de ces raisons",
}

# --- Sous-échantillons ------------------------------------------------------

# CELLULE 1 (1 500 personnes) et CELLULE 2 (3 541) ont reçu deux versions du
# questionnaire. Les questions sur le gratuit/payant, la dépense et les
# pratiques illicites détaillées ne sont posées qu'à la cellule 2.
SUBSAMPLE_LABELS = {1: "A", 2: "B"}
