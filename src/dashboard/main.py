from __future__ import annotations

import streamlit as st

from dashboard.config import DEFAULT_LAYOUT, PAGE_ICON, PAGE_TITLE, PAGES
from dashboard.filters import apply_filters, build_sidebar_filters, summarize_filters
from dashboard.sections import (
    audience,
    behavior,
    methodology,
    monetization,
    overview,
    raw_modules,
    segmentation,
    survey_explorer,
)
from dashboard.utils.io import load_all_sources


def _make_section_renderers(sources: dict) -> dict:
    """Build a unified page → callable dispatch table.

    Sections that need extra sources (raw_barometer, datamap_*) receive them via
    closures so the routing loop stays uniform.
    """
    raw_df = sources['raw_barometer']
    datamap_variables = sources['datamap_variables']
    datamap_texts = sources['datamap_texts']

    def render_survey_explorer(filtered_df, baseline_df):  # noqa: ARG001
        survey_explorer.render(
            analytics_df=filtered_df,
            raw_df=raw_df,
            datamap_variables=datamap_variables,
            datamap_texts=datamap_texts,
        )

    def render_methodology(filtered_df, baseline_df):  # noqa: ARG001
        methodology.render(
            filtered_df=filtered_df,
            raw_df=raw_df,
            datamap_variables=datamap_variables,
            datamap_texts=datamap_texts,
        )

    return {
        'overview': overview.render,
        'audience': audience.render,
        'behavior': behavior.render,
        'monetization': monetization.render,
        'raw_modules': raw_modules.render,
        'segmentation': segmentation.render,
        'survey_explorer': render_survey_explorer,
        'methodology': render_methodology,
    }


def run_app() -> None:
    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=DEFAULT_LAYOUT)

    sources = load_all_sources()
    analytics_df = sources['analytics']
    section_renderers = _make_section_renderers(sources)

    filters = build_sidebar_filters(analytics_df)
    filtered_df = apply_filters(analytics_df, filters)

    st.sidebar.divider()
    st.sidebar.metric('Filtered respondents', f'{len(filtered_df):,}')
    coverage = len(filtered_df) / len(analytics_df) if len(analytics_df) else 0.0
    st.sidebar.metric('Coverage', f'{coverage:.1%}')

    active_filters = summarize_filters(filters, analytics_df)
    if active_filters.empty:
        st.sidebar.caption('No active restrictions beyond the default full-population view.')
    else:
        st.sidebar.caption('Active filter state')
        st.sidebar.dataframe(active_filters, width='stretch', hide_index=True)

    st.sidebar.download_button(
        'Download filtered analytics CSV',
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='filtered_analytics_dataset.csv',
        mime='text/csv',
        width='stretch',
    )

    page_label = st.sidebar.radio('Navigation', list(PAGES.keys()))
    page = PAGES[page_label]

    if filtered_df.empty:
        st.title('Digital Cultural Consumption Analytics')
        st.error(
            'The current filter combination returns no respondents. '
            'Widen the filters to continue the analysis.'
        )
        st.dataframe(active_filters, width='stretch', hide_index=True)
        return

    renderer = section_renderers.get(page)
    if renderer is None:
        st.error(f'Unknown page key: {page!r}. Check PAGES in config.py.')
        return
    renderer(filtered_df, analytics_df)
