import pandas as pd
import streamlit as st

from dashboard.config import PALETTE_GENERATION, PALETTE_SEGMENT
from dashboard.utils.metrics import segment_summary
from dashboard.utils.viz import bar_count, bar_grouped, scatter, treemap


def render(df: pd.DataFrame):
    st.title('Segmentation')

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(bar_count(df, 'consumer_segment', 'Consumer segment distribution', orientation='h', color_map=PALETTE_SEGMENT), use_container_width=True)
    with c2:
        mix_df = df.groupby(['generation', 'consumer_segment'], dropna=False).size().reset_index(name='respondents')
        st.plotly_chart(
            treemap(mix_df, path=['generation', 'consumer_segment'], values='respondents', title='Generation × segment mix', color='generation', color_map=PALETTE_GENERATION),
            use_container_width=True,
        )

    grouped = (
        df.groupby('consumer_segment', dropna=False)
        .agg(avg_engagement=('engagement_score', 'mean'), avg_risk=('risk_behavior_score', 'mean'), avg_monetization=('monetization_score', 'mean'))
        .reset_index()
        .melt(id_vars='consumer_segment', var_name='metric', value_name='value')
    )
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(bar_grouped(grouped, 'consumer_segment', 'value', 'metric', 'Average score profile by segment'), use_container_width=True)
    with c4:
        st.plotly_chart(
            scatter(df, 'risk_behavior_score', 'engagement_score', 'consumer_segment', 'Risk vs engagement by segment', color_map=PALETTE_SEGMENT, size='monthly_spending'),
            use_container_width=True,
        )

    st.subheader('Segment summary')
    st.dataframe(segment_summary(df), use_container_width=True)
