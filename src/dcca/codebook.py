"""Lecture du dictionnaire des variables fourni par l'Arcom (datamap Ifop)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from dcca.config import DATAMAP_PATH


@dataclass(frozen=True)
class Variable:
    name: str
    title: str
    labels: dict[int, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Codebook:
    variables: dict[str, Variable]

    def title(self, name: str) -> str:
        return self.variables[name.upper()].title

    def labels(self, name: str) -> dict[int, str]:
        """Libellés d'une variable, ou de la liste partagée qu'elle référence."""
        return self.variables[name.upper()].labels

    def __contains__(self, name: str) -> bool:
        return name.upper() in self.variables


def load_codebook(path: Path = DATAMAP_PATH) -> Codebook:
    texts = pd.read_excel(path, sheet_name="TEXTS")
    variables = pd.read_excel(path, sheet_name="VARIABLES")

    titles = (
        texts[texts["TYPE"] == "TITLE"]
        .drop_duplicates("NAME")
        .set_index("NAME")["FR:L"]
        .astype(str)
        .to_dict()
    )
    label_rows = texts[(texts["TYPE"] == "LABEL") & texts["CODE"].notna()]
    labels: dict[str, dict[int, str]] = {}
    for name, group in label_rows.groupby("NAME"):
        labels[str(name)] = dict(
            zip(group["CODE"].astype(int), group["FR:L"].astype(str), strict=True)
        )

    out: dict[str, Variable] = {}
    for row in variables.itertuples(index=False):
        name = str(row.NAME)
        own = labels.get(name, {})
        shared = row.TEXT_LABELS if isinstance(row.TEXT_LABELS, str) else None
        out[name] = Variable(
            name=name,
            title=titles.get(name, name),
            labels=own or labels.get(shared or "", {}),
        )
    return Codebook(out)
