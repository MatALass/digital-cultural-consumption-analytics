"""Score d'intensité de consommation culturelle en ligne.

Le score mesure deux choses qui ne se recouvrent pas :
- l'étendue : combien de contenus différents la personne consomme (sur 12) ;
- la régularité : à quelle fréquence elle consomme ces contenus, en moyenne.

Les deux comptent pour moitié. Je n'ai pas de variable cible pour estimer des
poids, donc je garde le choix le plus simple à expliquer, et je vérifie a
posteriori que le score suit bien la dépense et le nombre d'abonnements
(voir notebooks/02_analyse_et_segmentation).
"""

from __future__ import annotations

import pandas as pd

from dcca.config import CONTENT_LABELS

N_CONTENTS = len(CONTENT_LABELS)

# Fréquence Q2 -> points : tous les jours = 1, chaque semaine = 2/3,
# chaque mois = 1/3, moins souvent = 0.
FREQUENCY_POINTS = {1: 1.0, 2: 2 / 3, 3: 1 / 3, 4: 0.0}

BREADTH_WEIGHT = 0.5
REGULARITY_WEIGHT = 0.5


def intensity_score(contents: pd.DataFrame) -> pd.Series:
    """Score de 0 à 100 par répondant, à partir de la table longue des contenus.

    Les répondants absents de la table (aucun contenu) n'ont pas de ligne :
    l'appelant leur donne 0.
    """
    if contents.empty:
        return pd.Series(dtype=float, name="score_intensite")
    points = pd.to_numeric(contents["frequence_code"], errors="coerce").map(FREQUENCY_POINTS)
    grouped = points.groupby(contents["id"])
    breadth = grouped.size() / N_CONTENTS
    # Un contenu sans fréquence renseignée compte comme « moins souvent ».
    regularity = grouped.apply(lambda s: s.fillna(0.0).mean())
    score = 100 * (BREADTH_WEIGHT * breadth + REGULARITY_WEIGHT * regularity)
    return score.clip(0, 100).rename("score_intensite")
