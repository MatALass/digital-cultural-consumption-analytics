from __future__ import annotations

import pandas as pd
import streamlit as st


FILTER_COLUMNS = [
    "region",
    "sex",
    "generation",
    "consumer_segment",
    "value_tier",
    "access_style",
    "urbanity_bucket",
]


def _choices(values: pd.Series) -> list[str]:
    normalized = values.dropna().astype(str)
    return sorted(v for v in normalized.unique() if v and v.lower() != "nan")


def build_sidebar_filters(df: pd.DataFrame) -> dict:
    st.sidebar.header("Global Filters")
    age_min = int(df["age"].min())
    age_max = int(df["age"].max())

    filters: dict = {
        "age": st.sidebar.slider("Age", age_min, age_max, (age_min, age_max)),
    }
    for column, label in [
        ("region", "Region"),
        ("sex", "Sex"),
        ("generation", "Generation"),
        ("consumer_segment", "Consumer segment"),
        ("value_tier", "Value tier"),
        ("access_style", "Access style"),
        ("urbanity_bucket", "Urbanity"),
    ]:
        choices = _choices(df[column])
        filters[column] = st.sidebar.multiselect(label, choices, default=choices)
    return filters


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Return a filtered copy of *df*.

    A multiselect that is empty (user deselected all options) is treated as
    "no restriction" rather than "no rows", which is consistent with the UX
    expectation: clearing a filter should widen, not eliminate, results.
    """
    out = df.copy()
    out = out[(out["age"] >= filters["age"][0]) & (out["age"] <= filters["age"][1])]
    for col in FILTER_COLUMNS:
        selected = filters.get(col)
        if selected:  # skip if None or empty list — do not silently return 0 rows
            out = out[out[col].astype(str).isin(selected)]
    return out


def summarize_filters(filters: dict, full_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    full_age = (int(full_df["age"].min()), int(full_df["age"].max()))
    if tuple(filters.get("age", full_age)) != full_age:
        rows.append(
            {"filter": "Age", "selection": f"{filters['age'][0]}–{filters['age'][1]}"}
        )

    for col in FILTER_COLUMNS:
        selected = filters.get(col, [])
        all_choices = _choices(full_df[col])
        if selected and len(selected) != len(all_choices):
            preview = ", ".join(selected[:3])
            if len(selected) > 3:
                preview += f" (+{len(selected) - 3})"
            rows.append({"filter": col.replace("_", " ").title(), "selection": preview})

    return pd.DataFrame(rows, columns=["filter", "selection"])
