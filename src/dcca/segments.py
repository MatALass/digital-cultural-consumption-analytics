"""Segmentation des consommateurs par règles.

Deux questions suffisent à placer chaque consommateur :
1. Consomme-t-il au moins un contenu de façon illégale, même rarement (Q5) ?
2. Paie-t-il au moins un abonnement culturel dans son foyer (RS12BIS) ?
Pour ceux qui ne paient pas, je distingue en plus ceux qui utilisent le compte
d'une personne extérieure au foyer, car ce sont des clients potentiels que
l'offre touche déjà.

J'ai préféré des règles à un clustering : chaque segment se lit en une phrase
et répond à une question métier (qui paie, qui pourrait payer, qui pirate
alors qu'il paie déjà). Les deux questions sont posées à tout l'échantillon,
donc la segmentation couvre les deux sous-échantillons.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

NON_CONSUMER = "Non-consommateurs"
SEGMENTS = {
    "Abonnés légaux": "Paie au moins un abonnement, ne consomme rien illégalement.",
    "Hybrides": "Paie au moins un abonnement et consomme aussi illégalement.",
    "Abonnés par procuration": (
        "Pas d'abonnement payé dans le foyer, utilise le compte d'une personne"
        " extérieure, rien d'illégal."
    ),
    "Gratuit légal": "Ni abonnement ni compte extérieur, rien d'illégal.",
    "Illicites sans abonnement": (
        "Consomme illégalement et ne paie aucun abonnement dans son foyer."
    ),
}
SEGMENT_ORDER = list(SEGMENTS)


@dataclass(frozen=True)
class SegmentRules:
    """Colonnes utilisées par les règles, pour tester d'autres définitions."""

    illicit: str = "illicite"
    subscriber: str = "abonne_payant"
    shared_account: str = "compte_exterieur"


DEFAULT_RULES = SegmentRules()

# Variantes utilisées pour l'analyse de sensibilité.
RULE_VARIANTS = {
    "Définition retenue": DEFAULT_RULES,
    "Illicite = au moins autant d'illégal que de légal": SegmentRules(illicit="illicite_marque"),
    "Abonné = y compris « autre abonnement »": SegmentRules(subscriber="abonne_tous_types"),
}


def assign_segments(df: pd.DataFrame, rules: SegmentRules = DEFAULT_RULES) -> pd.Series:
    consumer = df["consommateur"].astype(bool)
    illicit = df[rules.illicit].astype(bool)
    subscriber = df[rules.subscriber].astype(bool)
    shared = df[rules.shared_account].astype(bool)

    conditions = [
        ~consumer,
        illicit & subscriber,
        illicit & ~subscriber,
        ~illicit & subscriber,
        ~illicit & ~subscriber & shared,
    ]
    choices = [
        NON_CONSUMER,
        "Hybrides",
        "Illicites sans abonnement",
        "Abonnés légaux",
        "Abonnés par procuration",
    ]
    return pd.Series(
        np.select(conditions, choices, default="Gratuit légal"),
        index=df.index,
        name="segment",
    )


def segment_shares_by_variant(df: pd.DataFrame) -> pd.DataFrame:
    """Part de chaque segment parmi les consommateurs, pour chaque variante."""
    consumers = df[df["consommateur"].astype(bool)]
    rows = {}
    for name, rules in RULE_VARIANTS.items():
        shares = assign_segments(consumers, rules).value_counts(normalize=True)
        rows[name] = shares.reindex(SEGMENT_ORDER).fillna(0.0)
    return pd.DataFrame(rows).T
