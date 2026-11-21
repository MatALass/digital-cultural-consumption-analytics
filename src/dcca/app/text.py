"""Mise en forme des nombres en français et phrases générées à partir des données.

Toutes les phrases d'interprétation du dashboard sont calculées sur les données
filtrées : aucun chiffre n'est écrit en dur.
"""

from __future__ import annotations

import math

import pandas as pd

NBSP = " "


def pct(value: float, decimals: int = 0) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "n.d."
    text = f"{100 * value:.{decimals}f}".replace(".", ",")
    return f"{text}{NBSP}%"


def eur(value: float, decimals: int = 0) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "n.d."
    text = f"{value:,.{decimals}f}".replace(",", NBSP).replace(".", ",")
    return f"{text}{NBSP}€"


def integer(value: float) -> str:
    return f"{int(value):,}".replace(",", NBSP)


def interval(low: float, high: float) -> str:
    return f"[{pct(low)} ; {pct(high)}]"


def one_in(value: float) -> str:
    """0,24 -> « 1 sur 4 », pour les titres qui parlent à tout le monde."""
    if not value or math.isnan(value) or value <= 0:
        return "aucun"
    n = round(1 / value)
    if n <= 1:
        return "presque tous"
    return f"1 sur {n}"


def compare_extremes(table: pd.DataFrame, by: str, value: str = "part", subject: str = "") -> str:
    """Phrase « le plus haut chez X (a %), le plus bas chez Y (b %) ».

    Ne regarde que les modalités dont la base est suffisante. Renvoie une
    phrase sur une seule modalité si le filtre n'en laisse qu'une.
    """
    usable = table[table.get("fiable", True)].dropna(subset=[value])
    if usable.empty:
        return "La base est trop petite pour comparer les groupes."
    if len(usable) == 1:
        row = usable.iloc[0]
        return f"{subject}{row[by]} : {pct(row[value])}."
    top = usable.loc[usable[value].idxmax()]
    low = usable.loc[usable[value].idxmin()]
    gap = top[value] - low[value]
    return (
        f"{subject}la part la plus haute est chez **{top[by]}** ({pct(top[value])}), "
        f"la plus basse chez **{low[by]}** ({pct(low[value])}), soit "
        f"{round(100 * gap)} points d'écart."
    )
