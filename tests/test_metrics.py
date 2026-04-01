import pandas as pd

from dashboard.utils.metrics import (
    access_mix_summary,
    compute_overview_kpis,
    engagement_vs_spending_quintiles,
    percentile_table,
    risk_profile_by_segment,
    segment_summary,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            'monthly_spending': [0.0, 10.0, 25.0, 50.0, 90.0],
            'paying_user': [False, True, True, True, True],
            'high_value_user': [False, False, False, True, True],
            'risky_behavior_user': [False, True, False, True, True],
            'under_monetized_engaged_user': [True, False, False, False, False],
            'raw_content_category_count': [2, 3, 4, 4, 5],
            'engagement_score': [0.70, 0.40, 0.55, 0.75, 0.90],
            'monetization_score': [0.10, 0.30, 0.50, 0.70, 0.90],
            'access_style': ['Hybrid', 'Legal Free', 'Hybrid', 'Legal Paid', 'Legal Paid'],
            'consumer_segment': ['Heavy Free Users', 'Low Engagement Users', 'Casual Value Seekers', 'Premium Legal Users', 'Premium Legal Users'],
            'risk_behavior_score': [1, 3, 2, 4, 5],
            'vpn_score': [0, 1, 0, 2, 3],
            'dns_score': [0, 0, 1, 1, 2],
            'download_risk_score': [0, 2, 1, 0, 0],
            'cracked_apps_score': [0, 3, 0, 0, 0],
            'generation': ['Gen Z', 'Gen Z', 'Millennial', 'Gen X', 'Boomer+'],
        }
    )


def test_compute_overview_kpis():
    kpis = compute_overview_kpis(_sample_df())
    assert kpis['respondents'] == 5
    assert kpis['pct_paying'] == 0.8
    assert kpis['pct_high_value'] == 0.4
    assert kpis['hybrid_rate'] == 0.4
    assert kpis['legal_paid_rate'] == 0.4


def test_segment_summary_contains_expected_columns():
    summary = segment_summary(_sample_df())
    assert 'paying_rate' in summary.columns
    assert summary['respondents'].sum() == 5


def test_risk_profile_by_segment():
    profile = risk_profile_by_segment(_sample_df())
    assert set(profile.columns) == {'consumer_segment', 'vpn_score', 'dns_score', 'download_risk_score', 'cracked_apps_score'}
    assert not profile.empty


def test_engagement_vs_spending_quintiles():
    result = engagement_vs_spending_quintiles(_sample_df())
    assert result['respondents'].sum() == 5
    assert set(result['spending_quintile']) == {'Q1', 'Q2', 'Q3', 'Q4', 'Q5'}


def test_access_mix_summary_and_percentiles():
    df = _sample_df()
    access = access_mix_summary(df, 'generation')
    percentiles = percentile_table(df, 'consumer_segment', 'monthly_spending')
    assert not access.empty
    assert {'p25', 'p50', 'p75', 'p90'}.issubset(percentiles.columns)
