from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.config import PALETTE_ACCESS_STYLE, PALETTE_SEGMENT, PALETTE_VALUE_TIER
from dashboard.utils.metrics import access_mix_summary, percentile_table
from dashboard.utils.viz import bar_grouped, box, funnel_chart, scatter, treemap

def render(df: pd.DataFrame, baseline_df: pd.DataFrame) -> None:  # noqa: ARG001
    st.title('Monetization')

    funnel_df = pd.DataFrame(
        {
            'stage': ['All respondents', 'Engaged users', 'Paying users', 'High-value users'],
            'value': [
                len(df),
                int(df['engagement_score'].ge(0.65).sum()),
                int(df['paying_user'].sum()),
                int(df['high_value_user'].sum()),
            ],
        }
    )

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(funnel_chart(funnel_df, 'stage', 'value', 'Conversion funnel'), width='stretch')
    with c2:
        tree_df = df.groupby(['consumer_segment', 'value_tier'], dropna=False).size().reset_index(name='respondents')
        st.plotly_chart(
            treemap(tree_df, path=['consumer_segment', 'value_tier'], values='respondents', title='Segment × value tier mix', color='consumer_segment', color_map=PALETTE_SEGMENT),
            width='stretch',
        )

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(box(df, 'value_tier', 'engagement_score', 'Engagement distribution by value tier', color_map=PALETTE_VALUE_TIER), width='stretch')
    with c4:
        st.plotly_chart(
            scatter(df, 'engagement_score', 'monthly_spending', 'consumer_segment', 'Engagement vs monthly spending', color_map=PALETTE_SEGMENT, size='raw_content_category_count'),
            width='stretch',
        )

    st.subheader('Access style by value tier')
    access_by_tier = access_mix_summary(df, 'value_tier')
    st.plotly_chart(bar_grouped(access_by_tier, 'value_tier', 'share', 'access_style', 'Access style share by value tier', color_map=PALETTE_ACCESS_STYLE), width='stretch')

    st.subheader('Spending percentiles by segment')
    st.dataframe(percentile_table(df, 'consumer_segment', 'monthly_spending'), width='stretch', hide_index=True)
