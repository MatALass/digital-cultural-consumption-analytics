"""Chargement des tables et application des filtres de la sidebar."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import pandas as pd
import streamlit as st

from dcca import config as cfg
from dcca.build import Tables, load_tables
from dcca.codebook import Codebook, load_codebook

ALL = "Toutes"
ALL_M = "Tous"

FILTERS = {
    # colonne : (libellé, valeur « tout », ordre des modalités)
    "region": ("Région", ALL, sorted(cfg.REGION_LABELS.values())),
    "sexe": ("Sexe", ALL_M, list(cfg.SEX_LABELS.values())),
    "tranche_age": ("Tranche d'âge", ALL, cfg.AGE_GROUP_ORDER),
    "agglomeration": ("Taille de commune", ALL, cfg.AGGLOMERATION_ORDER),
}


class MissingDataError(RuntimeError):
    pass


@st.cache_data(show_spinner="Chargement des données...")
def get_tables() -> Tables:
    try:
        return load_tables()
    except FileNotFoundError as exc:
        raise MissingDataError(str(exc)) from exc


@st.cache_data(show_spinner=False)
def get_codebook() -> Codebook:
    return load_codebook()


@st.cache_data(show_spinner=False)
def get_geojson() -> dict:
    with open(cfg.GEOJSON_PATH, encoding="utf-8") as fh:
        return json.load(fh)


@dataclass(frozen=True)
class View:
    """Les tables restreintes aux répondants retenus par les filtres."""

    respondents: pd.DataFrame
    contents: pd.DataFrame
    subscriptions: pd.DataFrame
    illicit_means: pd.DataFrame
    reasons: pd.DataFrame
    total: int
    filters: dict[str, str] = field(default_factory=dict)

    @property
    def consumers(self) -> pd.DataFrame:
        return self.respondents[self.respondents["consommateur"]]

    @property
    def subsample_b(self) -> pd.DataFrame:
        """Consommateurs du sous-échantillon B, base des questions sur la dépense."""
        c = self.consumers
        return c[c["sous_echantillon"] == "B"]

    @property
    def is_filtered(self) -> bool:
        return any(v not in (ALL, ALL_M) for v in self.filters.values())


def apply_filters(tables: Tables, filters: dict[str, str]) -> View:
    r = tables.respondents
    mask = pd.Series(True, index=r.index)
    for column, value in filters.items():
        if value not in (ALL, ALL_M):
            mask &= r[column] == value
    kept = r[mask]
    ids = set(kept["id"])
    return View(
        respondents=kept,
        contents=tables.contents[tables.contents["id"].isin(ids)],
        subscriptions=tables.subscriptions[tables.subscriptions["id"].isin(ids)],
        illicit_means=tables.illicit_means[tables.illicit_means["id"].isin(ids)],
        reasons=tables.reasons[tables.reasons["id"].isin(ids)],
        total=len(r),
        filters=filters,
    )
