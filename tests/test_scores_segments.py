from __future__ import annotations

import pandas as pd
import pytest

from dcca.scores import N_CONTENTS, intensity_score
from dcca.segments import (
    NON_CONSUMER,
    SEGMENT_ORDER,
    SegmentRules,
    assign_segments,
    segment_shares_by_variant,
)
from tests.conftest import make_respondents

# --- Score d'intensité ---------------------------------------------------------


def _contents(rows):
    return pd.DataFrame(rows, columns=["id", "contenu", "frequence_code"])


def test_one_daily_content_scores_half_breadth_plus_full_regularity():
    score = intensity_score(_contents([("a", "Films", 1)]))
    assert score["a"] == pytest.approx(100 * (0.5 / N_CONTENTS + 0.5))


def test_all_contents_daily_gives_the_maximum():
    rows = [("a", f"c{i}", 1) for i in range(N_CONTENTS)]
    assert intensity_score(_contents(rows))["a"] == pytest.approx(100.0)


def test_rare_consumption_only_counts_breadth():
    score = intensity_score(_contents([("a", "Films", 4), ("a", "Séries", 4)]))
    assert score["a"] == pytest.approx(100 * 0.5 * 2 / N_CONTENTS)


def test_missing_frequency_counts_as_rare():
    with_gap = intensity_score(_contents([("a", "Films", 1), ("a", "Séries", None)]))
    rare = intensity_score(_contents([("a", "Films", 1), ("a", "Séries", 4)]))
    assert with_gap["a"] == pytest.approx(rare["a"])


def test_score_on_empty_table_is_empty():
    assert intensity_score(_contents([])).empty


def test_more_regular_consumer_scores_higher():
    score = intensity_score(_contents([("a", "Films", 1), ("b", "Films", 3)]))
    assert score["a"] > score["b"]


# --- Segments ---------------------------------------------------------------


@pytest.mark.parametrize(
    "flags,expected",
    [
        ({"consommateur": [False]}, NON_CONSUMER),
        ({"illicite": [True], "abonne_payant": [True]}, "Hybrides"),
        ({"illicite": [True]}, "Illicites sans abonnement"),
        (
            {"illicite": [True], "compte_exterieur": [True]},
            "Illicites sans abonnement",
        ),
        ({"abonne_payant": [True]}, "Abonnés légaux"),
        (
            {"abonne_payant": [True], "compte_exterieur": [True]},
            "Abonnés légaux",
        ),
        ({"compte_exterieur": [True]}, "Abonnés par procuration"),
        ({}, "Gratuit légal"),
    ],
)
def test_each_rule_places_the_respondent_in_the_expected_segment(flags, expected):
    assert assign_segments(make_respondents(**flags)).item() == expected


def test_non_consumer_wins_over_every_other_flag():
    df = make_respondents(consommateur=[False], illicite=[True], abonne_payant=[True])
    assert assign_segments(df).item() == NON_CONSUMER


def test_rules_can_point_to_another_illicit_definition():
    df = make_respondents(illicite=[True], illicite_marque=[False])
    strict = SegmentRules(illicit="illicite_marque")
    assert assign_segments(df).item() == "Illicites sans abonnement"
    assert assign_segments(df, strict).item() == "Gratuit légal"


def test_every_consumer_gets_one_of_the_five_segments():
    df = make_respondents(
        illicite=[True, True, False, False, False],
        abonne_payant=[True, False, True, False, False],
        compte_exterieur=[False, False, False, True, False],
    )
    assert sorted(assign_segments(df)) == sorted(SEGMENT_ORDER)


def test_variant_shares_sum_to_one_and_exclude_non_consumers():
    df = make_respondents(
        consommateur=[True, True, False],
        illicite=[True, False, False],
        abonne_payant=[True, False, False],
    )
    shares = segment_shares_by_variant(df)
    assert shares.sum(axis=1).round(10).eq(1.0).all()
    assert shares.loc["Définition retenue", "Hybrides"] == pytest.approx(0.5)
