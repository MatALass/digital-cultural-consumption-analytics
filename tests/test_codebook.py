"""Les libellés courts de config.py couvrent bien les codes du dictionnaire."""

from __future__ import annotations

import unicodedata

import pytest

from dcca import config as cfg


@pytest.mark.parametrize(
    "variable,labels",
    [
        ("SEXE", cfg.SEX_LABELS),
        ("RAGE2", cfg.AGE_GROUP_LABELS),
        ("REG13", cfg.REGION_LABELS),
        ("AGGLO", cfg.AGGLOMERATION_LABELS),
        ("SITI", cfg.SITUATION_LABELS),
        ("RECPPIA", cfg.CSP_LABELS),
        ("STATUT", cfg.HOUSEHOLD_STATUS_LABELS),
        ("ENF", cfg.CHILDREN_LABELS),
        ("RS6", cfg.INTERNET_FREQUENCY_LABELS),
        ("Q2", cfg.FREQUENCY_LABELS),
        ("Q5", cfg.LEGALITY_LABELS),
        ("QBU1", cfg.PAYMENT_LABELS),
        ("Q7", cfg.EVOLUTION_LABELS),
        ("RS12BIS", cfg.SUBSCRIPTION_STATUS_LABELS),
        ("RS16BIS", cfg.SHARED_CODE_ORIGIN_LABELS),
        ("RS7BIS", cfg.VPN_LABELS),
        ("RS8", cfg.DNS_LABELS),
        ("QBU11C", cfg.CRACKED_APP_LABELS),
        ("QBU8", cfg.ILLICIT_SENIORITY_LABELS),
        ("QBU10B", cfg.ILLICIT_MEANS_LABELS),
        ("QBU6", cfg.ILLICIT_REASON_LABELS),
    ],
)
def test_short_labels_cover_exactly_the_datamap_codes(codebook, variable, labels):
    assert set(labels) == set(codebook.labels(variable))


def test_content_codes_are_the_q1_items_without_other_and_none(codebook):
    q1 = codebook.labels("Q1")
    expected = set(q1) - {cfg.CONTENT_OTHER_CODE, cfg.CONTENT_NONE_CODE}
    assert set(cfg.CONTENT_LABELS) == expected
    assert q1[cfg.CONTENT_NONE_CODE].startswith("Aucun")


def test_region_codes_follow_the_datamap_names(codebook):
    # Le dictionnaire écrit « IleDeFrance1 », « ProvenceAlpesCoteDAzur »...
    raw_names = codebook.labels("REG13")
    for code, label in cfg.REGION_LABELS.items():
        ascii_label = unicodedata.normalize("NFKD", label).encode("ascii", "ignore")
        squashed = "".join(ch for ch in ascii_label.decode() if ch.isalpha())
        assert raw_names[code].rstrip("1").lower() == squashed.lower()


def test_series_and_films_share_the_same_illicit_means_list(codebook):
    assert codebook.labels("QBU10B") == codebook.labels("QBU10C")


def test_titles_are_read_from_the_texts_sheet(codebook):
    assert codebook.title("Q5").startswith("Q5 - Plus précisément")
    assert "QBU2" in codebook
