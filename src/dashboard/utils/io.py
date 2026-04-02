from __future__ import annotations

import pandas as pd

from dashboard.config import (
    DATAMAP_PATH,
    PROCESSED_COLUMN_RENAMES,
    PROCESSED_DATA_PATH,
    RAW_BAROMETER_PATH,
)
from dashboard.utils.transforms import build_analytics_dataset

try:
    import streamlit as st
except ModuleNotFoundError:  # pragma: no cover

    class _StreamlitFallback:
        @staticmethod
        def cache_data(*args, **kwargs):
            def decorator(func):
                return func

            return decorator

    st = _StreamlitFallback()


@st.cache_data(show_spinner=False)
def load_processed_data() -> pd.DataFrame:
    df = pd.read_excel(PROCESSED_DATA_PATH)
    return df.rename(columns=PROCESSED_COLUMN_RENAMES).drop(
        columns=["Unnamed: 0"], errors="ignore"
    )


@st.cache_data(show_spinner=False)
def load_raw_barometer() -> pd.DataFrame:
    return pd.read_excel(RAW_BAROMETER_PATH)


@st.cache_data(show_spinner=False)
def load_datamap_variables() -> pd.DataFrame:
    return pd.read_excel(DATAMAP_PATH, sheet_name="VARIABLES")


@st.cache_data(show_spinner=False)
def load_datamap_texts() -> pd.DataFrame:
    return pd.read_excel(DATAMAP_PATH, sheet_name="TEXTS")


@st.cache_data(show_spinner=False)
def build_cached_analytics(
    processed: pd.DataFrame, raw_barometer: pd.DataFrame
) -> pd.DataFrame:
    return build_analytics_dataset(processed, raw_barometer)


@st.cache_data(show_spinner=False)
def load_all_sources() -> dict:
    processed = load_processed_data()
    raw_barometer = load_raw_barometer()
    analytics = build_cached_analytics(processed, raw_barometer)
    datamap_variables = load_datamap_variables()
    datamap_texts = load_datamap_texts()
    return {
        "analytics": analytics,
        "raw_barometer": raw_barometer,
        "datamap_variables": datamap_variables,
        "datamap_texts": datamap_texts,
    }
