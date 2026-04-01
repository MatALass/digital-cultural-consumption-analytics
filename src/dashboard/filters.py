from __future__ import annotations

import pandas as pd
import streamlit as st


def _choices(values: pd.Series) -> list[str]:
    return sorted([str(v) for v in values.dropna().astype(str).unique()])


def build_sidebar_filters(df: pd.DataFrame) -> dict:
    st.sidebar.header('Global Filters')
    age_min = int(df['age'].min())
    age_max = int(df['age'].max())

    filters = {
        'age': st.sidebar.slider('Age', age_min, age_max, (age_min, age_max)),
        'region': st.sidebar.multiselect('Region', _choices(df['region']), default=_choices(df['region'])),
        'sex': st.sidebar.multiselect('Sex', _choices(df['sex']), default=_choices(df['sex'])),
        'generation': st.sidebar.multiselect('Generation', _choices(df['generation']), default=_choices(df['generation'])),
        'consumer_segment': st.sidebar.multiselect('Consumer segment', _choices(df['consumer_segment']), default=_choices(df['consumer_segment'])),
        'value_tier': st.sidebar.multiselect('Value tier', _choices(df['value_tier']), default=_choices(df['value_tier'])),
        'access_style': st.sidebar.multiselect('Access style', _choices(df['access_style']), default=_choices(df['access_style'])),
        'urbanity_bucket': st.sidebar.multiselect('Urbanity', _choices(df['urbanity_bucket']), default=_choices(df['urbanity_bucket'])),
    }
    return filters


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    out = df.copy()
    out = out[(out['age'] >= filters['age'][0]) & (out['age'] <= filters['age'][1])]
    for col in ['region', 'sex', 'generation', 'consumer_segment', 'value_tier', 'access_style', 'urbanity_bucket']:
        selected = filters.get(col)
        if selected:
            out = out[out[col].astype(str).isin(selected)]
    return out
