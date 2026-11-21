"""Tests sur le vrai fichier de l'Arcom : décodage, routage, cohérence."""

from __future__ import annotations

import pandas as pd
import pytest

from dcca import config as cfg
from dcca.quality import run_quality_checks


def test_quality_checks_pass_on_the_real_file(tables):
    assert run_quality_checks(tables) == []


def test_one_row_per_respondent_keyed_on_the_arcom_id(raw, tables):
    r = tables.respondents
    assert len(r) == len(raw) == 5041
    assert r["id"].is_unique
    assert set(r["id"]) == set(raw["ID"])


def test_consumer_count_matches_the_none_answer(raw, tables):
    none = pd.to_numeric(raw["Q1_11"]).eq(11).sum()
    assert tables.respondents["consommateur"].sum() == len(raw) - none == 4609


@pytest.mark.parametrize(
    "departments,region",
    [
        ([75, 77, 78, 91, 92, 93, 94, 95], "Île-de-France"),
        ([13, 6, 83, 84], "Provence-Alpes-Côte d'Azur"),
        ([69, 38, 63], "Auvergne-Rhône-Alpes"),
        ([33, 87, 17], "Nouvelle-Aquitaine"),
        ([59, 62, 80], "Hauts-de-France"),
        ([67, 57, 51], "Grand Est"),
        ([35, 29], "Bretagne"),
        ([31, 34], "Occitanie"),
        ([44, 49], "Pays de la Loire"),
        ([76, 14], "Normandie"),
        ([21, 25], "Bourgogne-Franche-Comté"),
        ([45, 37], "Centre-Val de Loire"),
    ],
)
def test_region_labels_agree_with_the_department(raw, tables, departments, region):
    # Ce test aurait détecté l'ancienne erreur (zones UDA lues comme régions).
    in_departments = pd.to_numeric(raw["DPT"]).isin(departments).to_numpy()
    assert in_departments.sum() > 0
    assert (tables.respondents.loc[in_departments, "region"] == region).all()


def test_paris_agglomeration_matches_the_insee_urban_unit(raw, tables):
    paris = tables.respondents["agglomeration"].eq("Agglomération parisienne")
    assert (raw.loc[paris.to_numpy(), "AGGLOIFOP0"] == "UU08").all()


def test_age_groups_match_the_declared_age(tables):
    r = tables.respondents
    bins = pd.cut(r["age"].astype(float), [14, 24, 34, 49, 64, 120], labels=cfg.AGE_GROUP_ORDER)
    assert (bins.astype(str) == r["tranche_age"].astype(str)).all()


@pytest.mark.parametrize("row", list(cfg.SUBSCRIPTION_LABELS))
def test_subscription_rows_follow_the_rs16bis_order(raw, row):
    # Les filtres AFRS16BISi<k> (compte extérieur) et AFRS17Ai<k> (budget)
    # portent sur la ligne k de RS12BIS : mêmes effectifs exactement.
    outside = pd.to_numeric(raw[f"RS12BIS_r{row}_c2"]).eq(2)
    household = pd.to_numeric(raw[f"RS12BIS_r{row}_c1"]).eq(1)
    assert outside.sum() == pd.to_numeric(raw[f"AFRS16BISi{row}"]).eq(row).sum()
    assert household.sum() == pd.to_numeric(raw[f"AFRS17Ai{row}"]).eq(row).sum()


def test_spending_is_only_asked_to_consumers_of_subsample_b(tables):
    r = tables.respondents
    asked = r["depense_mensuelle"].notna()
    assert set(r.loc[asked, "sous_echantillon"]) == {"B"}
    assert r.loc[asked, "consommateur"].all()


def test_spending_sentinel_is_removed(raw, tables):
    assert (pd.to_numeric(raw["QBU2"]) == 999).sum() == 1
    assert tables.respondents["depense_mensuelle"].max() < 999


def test_every_consumed_content_has_a_frequency_and_a_legality(tables):
    c = tables.contents
    assert c["frequence_code"].notna().all()
    assert c["legalite_code"].notna().all()


def test_payment_mode_only_exists_in_subsample_b(tables):
    c = tables.contents.merge(tables.respondents[["id", "sous_echantillon"]], on="id")
    assert set(c.loc[c["paiement_code"].notna(), "sous_echantillon"]) == {"B"}


def test_illicit_flag_matches_the_content_table(tables):
    r = tables.respondents.set_index("id")
    any_illicit = tables.contents.groupby("id")["illicite"].any()
    assert (r.loc[any_illicit.index, "illicite"] == any_illicit).all()


def test_no_personal_free_text_is_exported(tables):
    # Le brut ne contient pas de nom ; on vérifie qu'aucune réponse « précisez »
    # (texte libre) ne passe dans les tables.
    for frame in tables.as_dict().values():
        assert not any("precis" in col.lower() for col in frame.columns)


def test_processed_tables_are_up_to_date():
    # data/processed est versionné pour que l'app démarre vite : il doit
    # correspondre exactement à une reconstruction depuis le brut.
    from dcca.cli import main

    assert main(["check"]) == 0
