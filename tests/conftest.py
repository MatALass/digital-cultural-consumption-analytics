from __future__ import annotations

import pandas as pd
import pytest

from dcca.build import Tables, build_tables, read_raw
from dcca.codebook import Codebook, load_codebook


@pytest.fixture(scope="session")
def raw() -> pd.DataFrame:
    return read_raw()


@pytest.fixture(scope="session")
def tables(raw: pd.DataFrame) -> Tables:
    return build_tables(raw)


@pytest.fixture(scope="session")
def codebook() -> Codebook:
    return load_codebook()


def make_respondents(**overrides) -> pd.DataFrame:
    """Petite table de répondants pour tester les règles sans le fichier brut."""
    base = {
        "consommateur": [True],
        "illicite": [False],
        "illicite_marque": [False],
        "abonne_payant": [False],
        "abonne_tous_types": [False],
        "compte_exterieur": [False],
    }
    base.update({k: list(v) for k, v in overrides.items()})
    n = max(len(v) for v in base.values())
    return pd.DataFrame({k: v * n if len(v) == 1 else v for k, v in base.items()})
