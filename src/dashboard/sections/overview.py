import pandas as pd
import streamlit as st

from dashboard.config import PALETTE_GENERATION, PALETTE_SEGMENT
from dashboard.utils.metrics import compute_overview_kpis, engagement_vs_spending_quintiles
from dashboard.utils.viz import bar_metric_by_group, histogram, line_chart, scatter


def render(df: pd.DataFrame):
    st.title('Executive Overview')
    st.caption('Decision-oriented dashboard built from the curated analytical layer and raw module enrichment.')

    k = compute_overview_kpis(df)

    row1 = st.columns(6)
    row1[0].metric('Respondents', f"{k['respondents']:,}")
    row1[1].metric('Median spend', f"{k['median_spending']:.1f}€")
    row1[2].metric('P75 spend', f"{k['p75_spending']:.1f}€")
    row1[3].metric('P90 spend', f"{k['p90_spending']:.1f}€")
    row1[4].metric('Paying rate', f"{k['pct_paying'] * 100:.1f}%")
    row1[5].metric('High-value rate', f"{k['pct_high_value'] * 100:.1f}%")

    row2 = st.columns(6)
    row2[0].metric('Mean spend', f"{k['mean_spending']:.1f}€")
    row2[1].metric('Risky behavior', f"{k['pct_risky'] * 100:.1f}%")
    row2[2].metric('Under-monetized engaged', f"{k['pct_under_monetized_engaged'] * 100:.1f}%")
    row2[3].metric('Avg engagement', f"{k['avg_engagement']:.2f}")
    row2[4].metric('Hybrid access', f"{k['hybrid_rate'] * 100:.1f}%")
    row2[5].metric('Legal paid', f"{k['legal_paid_rate'] * 100:.1f}%")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(histogram(df, 'monthly_spending', 'Monthly spending distribution', nbins=35), use_container_width=True)
    with c2:
        st.plotly_chart(
            bar_metric_by_group(df, 'generation', 'raw_content_category_count', 'Average content breadth by generation', agg='mean', color_map=PALETTE_GENERATION),
            use_container_width=True,
        )

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(
            scatter(df, x='engagement_score', y='monthly_spending', color='consumer_segment', title='Engagement vs monthly spending', color_map=PALETTE_SEGMENT, size='raw_content_category_count'),
            use_container_width=True,
        )
    with c4:
        quintiles = engagement_vs_spending_quintiles(df)
        st.plotly_chart(line_chart(quintiles, 'spending_quintile', 'avg_engagement', 'Average engagement by spending quintile', markers=True), use_container_width=True)

    st.subheader('Interpretation')
    st.info(f"The top quartile starts at {k['p75_spending']:.1f}€, which confirms revenue concentration in a limited share of respondents.")
    st.warning(f"{k['pct_under_monetized_engaged'] * 100:.1f}% of the filtered population appears engaged but still non-paying, which is the cleanest conversion opportunity.")
    st.success(f"Raw module enrichment adds an average of {k['avg_raw_content_depth']:.2f} observed content-category signals per respondent.")
