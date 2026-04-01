import streamlit as st

from dashboard.config import DEFAULT_LAYOUT, PAGE_ICON, PAGE_TITLE, PAGES
from dashboard.filters import apply_filters, build_sidebar_filters
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


SECTION_RENDERERS = {
    'overview': overview.render,
    'audience': audience.render,
    'behavior': behavior.render,
    'monetization': monetization.render,
    'raw_modules': raw_modules.render,
    'segmentation': segmentation.render,
}


def run_app() -> None:
    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=DEFAULT_LAYOUT)

    sources = load_all_sources()
    analytics_df = sources['analytics']

    filters = build_sidebar_filters(analytics_df)
    filtered_df = apply_filters(analytics_df, filters)

    st.sidebar.divider()
    st.sidebar.metric('Filtered respondents', f'{len(filtered_df):,}')
    st.sidebar.metric('Coverage', f'{(len(filtered_df) / len(analytics_df)):.1%}')

    page_label = st.sidebar.radio('Navigation', list(PAGES.keys()))
    page = PAGES[page_label]

    if page in SECTION_RENDERERS:
        SECTION_RENDERERS[page](filtered_df)
    elif page == 'survey_explorer':
        survey_explorer.render(
            analytics_df=filtered_df,
            raw_df=sources['raw_barometer'],
            datamap_variables=sources['datamap_variables'],
            datamap_texts=sources['datamap_texts'],
        )
    else:
        methodology.render(
            filtered_df=filtered_df,
            raw_df=sources['raw_barometer'],
            datamap_variables=sources['datamap_variables'],
            datamap_texts=sources['datamap_texts'],
        )
