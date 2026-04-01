import pandas as pd

from dashboard.filters import apply_filters


def _df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            'age': [20, 30, 40],
            'region': ['A', 'B', 'A'],
            'sex': ['Male', 'Female', 'Male'],
            'generation': ['Gen Z', 'Millennial', 'Gen X'],
            'consumer_segment': ['S1', 'S2', 'S3'],
            'value_tier': ['Low', 'Mid', 'High'],
            'access_style': ['Legal Free', 'Hybrid', 'Legal Paid'],
            'urbanity_bucket': ['Urban', 'Rural', 'Metro'],
        }
    )


def test_apply_filters_all_columns():
    filters = {
        'age': (18, 35),
        'region': ['A', 'B'],
        'sex': ['Female'],
        'generation': ['Millennial'],
        'consumer_segment': ['S2'],
        'value_tier': ['Mid'],
        'access_style': ['Hybrid'],
        'urbanity_bucket': ['Rural'],
    }
    out = apply_filters(_df(), filters)
    assert len(out) == 1
    assert out.iloc[0]['consumer_segment'] == 'S2'


def test_apply_filters_with_missing_optional_lists():
    filters = {'age': (18, 50), 'region': ['A', 'B'], 'sex': ['Male', 'Female'], 'generation': ['Gen Z', 'Millennial', 'Gen X'], 'consumer_segment': ['S1', 'S2', 'S3'], 'value_tier': ['Low', 'Mid', 'High'], 'access_style': ['Legal Free', 'Hybrid', 'Legal Paid'], 'urbanity_bucket': ['Urban', 'Rural', 'Metro']}
    out = apply_filters(_df(), filters)
    assert len(out) == 3
