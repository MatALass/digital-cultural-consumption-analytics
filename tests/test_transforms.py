from __future__ import annotations

import pandas as pd

from dashboard.utils.transforms import build_analytics_dataset


def test_build_analytics_dataset_adds_raw_features():
    processed = pd.DataFrame(
        {
            "sex": ["H", "F"],
            "age": [23, 52],
            "region": ["Île-de-France", "Grand Est"],
            "agglomeration_type": ["Paris et grandes métropoles", "Rural isolé"],
            "personal_situation": ["étudiant", "actif"],
            "main_profession": ["Prof", "Ingénieur"],
            "employment_status": [
                "Salarié du privé ou association",
                "Salarié de l’État",
            ],
            "internet_frequency": ["Plusieurs fois par jour", "1 à 2 fois par semaine"],
            "cultural_frequency": ["Tous les jours ou presque", "1 à 3 fois par mois"],
            "legality_type": ["Autant", "Légale"],
            "legality_evolution": ["autant légale", "davantage légale"],
            "payment_type": ["autant", "payante"],
            "monthly_spending": [0.0, 45.0],
            "devices_films_series": ["Autre", "Autre"],
            "vpn_usage": ["occasionnellement", "jamais"],
            "cracked_apps_usage": ["Oui", "Non"],
            "streaming_download_type": ["Gratuit", "payante"],
            "dns_settings_usage": ["De temps en temps", "Jamais"],
            "paid_services_access": ["compte partagé", "abonné"],
            "household_size": ["2 personnes", "4 personnes"],
            "children_count": ["Aucun", "2"],
            "household_status": ["célibataire", "couple"],
        }
    )

    raw = pd.DataFrame(
        {
            "QBU1_r1": [1, 5],
            "QBU1_r2": [2, 4],
            "QBU5a_r1_c1": [1, 0],
            "QBU5a_r1_c2": [1, 1],
            "QBU10a_1": [1, 0],
            "QBU10b_1": [0, 2],
            "QBU11_r1": [2, 4],
            "QBU11B_r1_c1": [1, 0],
            "QBU12_r1": [1, 5],
            "QBOL3_1": [1, 0],
            "QBOL4_1": [1, 1],
        }
    )

    out = build_analytics_dataset(processed, raw)
    expected = {
        "raw_content_paid_score",
        "raw_content_category_count",
        "raw_device_diversity",
        "raw_illicit_channel_count",
        "raw_illicit_method_count",
        "raw_stream_ripping_score",
        "raw_legal_offer_advantage_count",
        "raw_legal_motivation_count",
        "raw_behavioral_coverage_rate",
        "content_depth_score",
        "raw_risk_intensity_score",
        "consumer_segment",
    }
    assert expected.issubset(set(out.columns))
    assert out["raw_content_category_count"].tolist() == [2, 2]
