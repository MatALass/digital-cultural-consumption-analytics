from __future__ import annotations

import pandas as pd

from dashboard.filters import apply_filters, summarize_filters

def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            'age': [20, 35, 50],
            'region': ['A', 'B', 'B'],
            'sex': ['Male', 'Female', 'Male'],
            'generation': ['Gen Z', 'Millennial', 'Gen X'],
            'consumer_segment': ['Seg1', 'Seg2', 'Seg3'],
            'value_tier': ['Low spender', 'High spender', 'Top spender'],
            'access_style': ['Legal Free', 'Hybrid', 'Risk Heavy'],
            'urbanity_bucket': ['Urban', 'Metro', 'Rural'],
        }
    )

def test_apply_filters_by_age_and_region() -> None:
    df = _sample_df()
    filters = {
        'age': (18, 40),
        'region': ['B'],
        'sex': ['Male', 'Female'],
        'generation': ['Gen Z', 'Millennial', 'Gen X'],
        'consumer_segment': ['Seg1', 'Seg2', 'Seg3'],
        'value_tier': ['Low spender', 'High spender', 'Top spender'],
        'access_style': ['Legal Free', 'Hybrid', 'Risk Heavy'],
        'urbanity_bucket': ['Urban', 'Metro', 'Rural'],
    }
    filtered = apply_filters(df, filters)
    assert filtered.shape[0] == 1
    assert filtered.iloc[0]['region'] == 'B'

def test_summarize_filters_only_returns_restricted_dimensions() -> None:
    df = _sample_df()
    filters = {
        'age': (18, 40),
        'region': ['B'],
        'sex': ['Male', 'Female'],
        'generation': ['Gen Z', 'Millennial', 'Gen X'],
        'consumer_segment': ['Seg1', 'Seg2', 'Seg3'],
        'value_tier': ['Low spender', 'High spender', 'Top spender'],
        'access_style': ['Legal Free', 'Hybrid', 'Risk Heavy'],
        'urbanity_bucket': ['Urban', 'Metro', 'Rural'],
    }
    summary = summarize_filters(filters, df)
    assert set(summary['filter']) == {'Age', 'Region'}
