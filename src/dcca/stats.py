"""Indicateurs statistiques : parts avec intervalle de confiance, médiane,
tests d'indépendance.

Le fichier publié n'a pas de variable de pondération. Les intervalles sont
donc calculés comme pour un tirage aléatoire simple : sur un échantillon par
quotas, ils donnent un ordre de grandeur de la précision, pas une garantie.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats as sps

Z_95 = 1.959963984540054
MIN_BASE = 30  # en dessous, une part n'est pas affichée


@dataclass(frozen=True)
class Share:
    successes: int
    base: int
    low: float
    high: float

    @property
    def value(self) -> float:
        return self.successes / self.base if self.base else float("nan")

    @property
    def reliable(self) -> bool:
        return self.base >= MIN_BASE


def wilson_interval(successes: int, base: int, z: float = Z_95) -> tuple[float, float]:
    """Intervalle de Wilson : reste dans [0, 1] et tient sur les petites bases."""
    if base <= 0:
        return float("nan"), float("nan")
    if not 0 <= successes <= base:
        raise ValueError("successes doit être compris entre 0 et base")
    p = successes / base
    denom = 1 + z**2 / base
    centre = (p + z**2 / (2 * base)) / denom
    half = z * math.sqrt(p * (1 - p) / base + z**2 / (4 * base**2)) / denom
    low = 0.0 if successes == 0 else max(0.0, centre - half)
    high = 1.0 if successes == base else min(1.0, centre + half)
    return low, high


def share(mask: pd.Series) -> Share:
    """Part de True dans une série booléenne ; les valeurs manquantes sont exclues."""
    values = mask.dropna().astype(bool)
    k, n = int(values.sum()), int(values.size)
    low, high = wilson_interval(k, n)
    return Share(k, n, low, high)


def share_table(
    df: pd.DataFrame, flag: str, by: str, order: list[str] | None = None
) -> pd.DataFrame:
    """Part de `flag` par modalité de `by`, avec base et intervalle à 95 %."""
    rows = []
    for level, group in df.groupby(by, observed=True):
        s = share(group[flag])
        rows.append(
            {
                by: level,
                "part": s.value,
                "ic_bas": s.low,
                "ic_haut": s.high,
                "base": s.base,
                "fiable": s.reliable,
            }
        )
    out = pd.DataFrame(rows, columns=[by, "part", "ic_bas", "ic_haut", "base", "fiable"])
    if order is not None:
        out[by] = pd.Categorical(out[by], categories=order, ordered=True)
        out = out.sort_values(by).reset_index(drop=True)
    return out


def bootstrap_median(
    values: pd.Series, n_boot: int = 2000, seed: int = 2024
) -> tuple[float, float, float]:
    """Médiane et intervalle bootstrap percentile à 95 %."""
    data = pd.to_numeric(values, errors="coerce").dropna().to_numpy()
    if data.size == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    samples = rng.choice(data, size=(n_boot, data.size), replace=True)
    medians = np.median(samples, axis=1)
    return (
        float(np.median(data)),
        float(np.quantile(medians, 0.025)),
        float(np.quantile(medians, 0.975)),
    )


@dataclass(frozen=True)
class IndependenceTest:
    chi2: float
    dof: int
    p_value: float
    cramers_v: float
    n: int


def independence_test(df: pd.DataFrame, row: str, col: str) -> IndependenceTest:
    """Test du khi-deux et V de Cramér entre deux variables qualitatives."""
    table = pd.crosstab(df[row], df[col])
    if table.shape[0] < 2 or table.shape[1] < 2:
        return IndependenceTest(float("nan"), 0, float("nan"), float("nan"), 0)
    chi2, p_value, dof, _ = sps.chi2_contingency(table)
    n = int(table.to_numpy().sum())
    v = math.sqrt(chi2 / (n * (min(table.shape) - 1)))
    return IndependenceTest(float(chi2), int(dof), float(p_value), v, n)
