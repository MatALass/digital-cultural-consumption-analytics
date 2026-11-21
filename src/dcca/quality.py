"""Contrôles qualité lancés à chaque `dcca build`.

Un contrôle en échec arrête la construction : les fichiers de data/processed
ne sont pas réécrits.
"""

from __future__ import annotations

import pandas as pd

from dcca import config as cfg
from dcca.segments import NON_CONSUMER, SEGMENT_ORDER


def _decoded_without_gaps(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [
        f"{col} : {int(df[col].isna().sum())} valeurs non décodées"
        for col in columns
        if df[col].isna().any()
    ]


def run_quality_checks(tables) -> list[str]:
    r = tables.respondents
    c = tables.contents
    s = tables.subscriptions
    failures: list[str] = []

    # Schéma et unicité
    if not r["id"].is_unique:
        failures.append("id en double dans la table des répondants")
    if c.duplicated(["id", "contenu"]).any():
        failures.append("couple (id, contenu) en double")
    if s.duplicated(["id", "abonnement"]).any():
        failures.append("couple (id, abonnement) en double")
    unknown = set(c["id"]) - set(r["id"])
    if unknown:
        failures.append(f"{len(unknown)} id de contenus absents des répondants")

    # Variables posées à tout le monde : aucune valeur manquante après décodage
    failures += _decoded_without_gaps(
        r,
        [
            "sous_echantillon",
            "sexe",
            "tranche_age",
            "region",
            "agglomeration",
            "csp",
            "statut_foyer",
            "frequence_internet",
            "vpn",
            "dns",
        ],
    )

    # Routage du questionnaire
    spent = r["depense_mensuelle"].notna()
    if (spent & (r["sous_echantillon"] != cfg.SUBSAMPLE_LABELS[2])).any():
        failures.append("dépense renseignée hors du sous-échantillon B")
    if (spent & ~r["consommateur"]).any():
        failures.append("dépense renseignée pour un non-consommateur")
    if (r["n_contenus"].gt(0) & ~r["consommateur"]).any():
        failures.append("contenus consommés par un non-consommateur")
    missing_frequency = c["frequence_code"].isna().sum()
    if missing_frequency:
        failures.append(f"{missing_frequency} contenus consommés sans fréquence")
    if (c["illicite"] != c["frequence_illicite_code"].notna()).any():
        failures.append("fréquence illicite incohérente avec la licéité (Q5/Q6)")

    # Valeurs plausibles
    if not r["age"].between(15, 100).all():
        failures.append("âge hors de [15, 100]")
    if (r["depense_mensuelle"] < 0).any():
        failures.append("dépense négative")
    if not r["score_intensite"].between(0, 100).all():
        failures.append("score d'intensité hors de [0, 100]")

    # Segmentation exhaustive et exclusive
    expected = set(SEGMENT_ORDER) | {NON_CONSUMER}
    if not set(r["segment"]).issubset(expected):
        failures.append("segment inconnu")
    if (r.loc[r["consommateur"], "segment"] == NON_CONSUMER).any():
        failures.append("consommateur classé non-consommateur")
    return failures
