import pandas as pd
import streamlit as st

from dashboard.config import PALETTE_GENERATION, PALETTE_SEGMENT
from dashboard.utils.metrics import spending_distribution_by_group
from dashboard.utils.viz import bar_metric_by_group, sunburst, treemap, violin


def render(df: pd.DataFrame):
    st.title('Audience & Context')

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(violin(df, 'generation', 'monthly_spending', 'Spending distribution by generation', color_map=PALETTE_GENERATION), use_container_width=True)
    with c2:
        sunburst_df = (
            df.groupby(['generation', 'family_stage', 'consumer_segment'], dropna=False)
            .size()
            .reset_index(name='respondents')
        )
        st.plotly_chart(
            sunburst(sunburst_df, path=['generation', 'family_stage', 'consumer_segment'], values='respondents', title='Generation → family stage → segment', color='consumer_segment', color_map=PALETTE_SEGMENT),
            use_container_width=True,
        )

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(bar_metric_by_group(df, 'urbanity_bucket', 'raw_content_category_count', 'Average content breadth by urbanity', agg='mean', orientation='h', sort='desc'), use_container_width=True)
    with c4:
        profession_df = spending_distribution_by_group(df, 'main_profession').head(12)
        st.plotly_chart(
            treemap(profession_df, path=['main_profession'], values='respondents', title='Top professions by respondent volume', color='main_profession'),
            use_container_width=True,
        )

    st.subheader('Audience deep-dive')
    st.dataframe(
        spending_distribution_by_group(df, 'generation').rename(columns={'payer_rate': 'paying_rate'}),
        use_container_width=True,
    )
