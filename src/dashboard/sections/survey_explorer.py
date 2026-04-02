from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.utils.metrics import missingness_report
from dashboard.utils.viz import bar_count, bar_metric_by_group, histogram


def render(
    analytics_df: pd.DataFrame,
    raw_df: pd.DataFrame,
    datamap_variables: pd.DataFrame,
    datamap_texts: pd.DataFrame,
) -> None:
    st.title("Survey Explorer")

    c1, c2, c3 = st.columns(3)
    c1.metric("Analytics rows", f"{len(analytics_df):,}")
    c2.metric("Raw survey rows", f"{len(raw_df):,}")
    c3.metric("Raw survey columns", f"{raw_df.shape[1]:,}")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Missingness", "Variable catalog", "Text labels", "Raw column explorer"]
    )

    with tab1:
        report = missingness_report(analytics_df).head(30)
        st.dataframe(report, width="stretch", hide_index=True)
        st.plotly_chart(
            bar_metric_by_group(
                report,
                "column",
                "missing_rate",
                "Top analytical columns by missingness",
                agg="mean",
                orientation="h",
                sort="desc",
            ),
            width="stretch",
        )

    with tab2:
        search = st.text_input("Search variable name", value="QBU", key="var_search")
        vars_filtered = datamap_variables[
            datamap_variables["NAME"]
            .astype(str)
            .str.contains(search, case=False, na=False)
        ]
        st.dataframe(vars_filtered.head(100), width="stretch")

    with tab3:
        text_search = st.text_input(
            "Search text label", value="légale", key="text_search"
        )
        texts_filtered = datamap_texts[
            datamap_texts["FR:L"]
            .astype(str)
            .str.contains(text_search, case=False, na=False)
        ]
        st.dataframe(texts_filtered.head(100), width="stretch")

    with tab4:
        selected_column = st.selectbox(
            "Select a raw column", options=sorted(raw_df.columns.astype(str).tolist())
        )
        sample = raw_df[selected_column]
        st.write("Preview of raw values")
        st.dataframe(sample.head(30).to_frame(name=selected_column), width="stretch")
        if pd.api.types.is_numeric_dtype(sample):
            st.plotly_chart(
                histogram(
                    raw_df,
                    selected_column,
                    f"Distribution of {selected_column}",
                    nbins=30,
                ),
                width="stretch",
            )
        else:
            st.plotly_chart(
                bar_count(
                    raw_df.head(1000),
                    selected_column,
                    f"Distribution of {selected_column} (first 1,000 rows)",
                    orientation="h",
                ),
                width="stretch",
            )
