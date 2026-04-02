from __future__ import annotations

import pandas as pd

from dashboard.utils.metrics import (
    compare_kpis_to_baseline,
    compute_overview_kpis,
    engagement_vs_spending_quintiles,
    opportunity_segments,
    segment_summary,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "monthly_spending": [0, 10, 20, 30, 50],
            "paying_user": [False, True, True, True, True],
            "high_value_user": [False, False, False, True, True],
            "risky_behavior_user": [False, False, True, True, False],
            "under_monetized_engaged_user": [True, False, False, False, False],
            "raw_content_category_count": [1, 2, 3, 4, 5],
            "engagement_score": [0.7, 0.5, 0.8, 0.9, 0.6],
            "monetization_score": [0.1, 0.4, 0.6, 0.7, 0.8],
            "access_style": [
                "Hybrid",
                "Legal Paid",
                "Legal Paid",
                "Risk Heavy",
                "Legal Paid",
            ],
            "consumer_segment": ["A", "A", "B", "B", "C"],
            "risk_behavior_score": [0, 1, 3, 5, 1],
            "vpn_score": [0, 0, 1, 2, 0],
            "dns_score": [0, 0, 1, 1, 0],
            "download_risk_score": [0, 0, 1, 1, 0],
            "cracked_apps_score": [0, 0, 1, 1, 0],
        }
    )


def test_compute_overview_kpis_counts() -> None:
    kpis = compute_overview_kpis(_sample_df())
    assert kpis["respondents"] == 5
    assert kpis["pct_paying"] == 0.8
    assert kpis["hybrid_rate"] == 0.2


def test_segment_summary_returns_rows() -> None:
    summary = segment_summary(_sample_df())
    assert set(summary["consumer_segment"]) == {"A", "B", "C"}


def test_engagement_vs_spending_quintiles_has_five_rows() -> None:
    quintiles = engagement_vs_spending_quintiles(_sample_df())
    assert list(quintiles["spending_quintile"]) == ["Q1", "Q2", "Q3", "Q4", "Q5"]


def test_compare_kpis_to_baseline_contains_expected_metrics() -> None:
    baseline = _sample_df()
    filtered = baseline[baseline["monthly_spending"] >= 20]
    benchmark = compare_kpis_to_baseline(filtered, baseline)
    assert "Median spending (€)" in set(benchmark["metric"])
    assert benchmark.shape[0] == 7


def test_opportunity_segments_sorts_by_headroom() -> None:
    ranked = opportunity_segments(_sample_df())
    assert ranked.iloc[0]["consumer_segment"] in {"A", "B"}
