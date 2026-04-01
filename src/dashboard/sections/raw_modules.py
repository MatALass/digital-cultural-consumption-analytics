import pandas as pd
import streamlit as st

from dashboard.config import PALETTE_SEGMENT
from dashboard.utils.viz import bar_metric_by_group, box, heatmap_share, scatter, violin


def render(df: pd.DataFrame):
    st.title('Raw Modules')
    st.caption('Direct exploitation of additional raw barometer columns instead of relying only on the curated export.')

    metrics = st.columns(4)
    metrics[0].metric('Avg content categories', f"{df['raw_content_category_count'].mean():.2f}")
    metrics[1].metric('Avg device diversity', f"{df['raw_device_diversity'].mean():.2f}")
    metrics[2].metric('Avg illicit channels', f"{df['raw_illicit_channel_count'].mean():.2f}")
    metrics[3].metric('Avg legal motivations', f"{df['raw_legal_motivation_count'].mean():.2f}")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(violin(df, 'consumer_segment', 'raw_device_diversity', 'Device diversity by segment', color_map=PALETTE_SEGMENT), use_container_width=True)
    with c2:
        st.plotly_chart(bar_metric_by_group(df, 'generation', 'raw_illicit_method_count', 'Average illicit-method breadth by generation', agg='mean'), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(heatmap_share(df, 'consumer_segment', 'payment_bucket', 'Payment orientation within segments'), use_container_width=True)
    with c4:
        st.plotly_chart(box(df, 'payment_bucket', 'legal_value_perception_score', 'Legal value perception by payment bucket'), use_container_width=True)

    st.plotly_chart(
        scatter(df, 'raw_content_category_count', 'monthly_spending', 'consumer_segment', 'Content breadth vs monthly spending', color_map=PALETTE_SEGMENT, size='raw_device_diversity'),
        use_container_width=True,
    )
