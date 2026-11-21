"""Le dashboard s'affiche sans erreur, avec et sans filtres, et gère les cas vides."""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from dcca.app.main import PAGES
from dcca.app.text import compare_extremes, eur, one_in, pct

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def _run(page: str, **filters) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    for column, value in filters.items():
        at.selectbox(key=f"f_{column}").set_value(value)
    at.radio(key="page").set_value(page)
    at.run()
    return at


@pytest.mark.parametrize("page", list(PAGES))
def test_every_page_renders_on_the_full_sample(page):
    at = _run(page)
    assert not at.exception, at.exception[0].value if at.exception else ""
    assert not at.error


@pytest.mark.parametrize("page", list(PAGES))
def test_every_page_renders_with_a_narrow_filter(page):
    at = _run(page, tranche_age="65 ans et plus", region="Bretagne")
    assert not at.exception, at.exception[0].value if at.exception else ""


def test_tiny_selection_shows_a_warning_instead_of_charts():
    at = _run("Segments", region="Corse", tranche_age="15-24 ans")
    assert not at.exception
    assert at.warning or at.error


def test_french_number_formatting():
    assert pct(0.243) == "24 %"
    assert pct(0.2434, 1) == "24,3 %"
    assert eur(1234.5) == "1 234 €"
    assert pct(float("nan")) == "n.d."
    assert one_in(0.24) == "1 sur 4"


def test_compare_extremes_with_one_level_does_not_compare():
    import pandas as pd

    table = pd.DataFrame({"g": ["a"], "part": [0.5], "fiable": [True]})
    assert "plus haute" not in compare_extremes(table, "g")
