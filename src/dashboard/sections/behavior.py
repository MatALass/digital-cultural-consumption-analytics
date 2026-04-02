from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.config import PALETTE_ACCESS_STYLE, PALETTE_GENERATION
from dashboard.utils.metrics import access_mix_summary, risk_profile_by_segment
from dashboard.utils.viz import bar_count, bar_grouped, bar_metric_by_group, radar_chart, scatter, violin


def render(df: pd.DataFrame, baseline_df: pd.DataFrame) -> None:  # noqa: ARG001
    st.title('Behavior & Access')

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(bar_count(df, 'access_style', 'Access style mix', color_map=PALETTE_ACCESS_STYLE), width='stretch')
    with c2:
        st.plotly_chart(bar_count(df, 'legality_type', 'Legal vs illegal self-positioning', orientation='h'), width='stretch')

    c3, c4 = st.columns(2)
    with c3:
        radar_df = risk_profile_by_segment(df)
        st.plotly_chart(
            radar_chart(radar_df, 'consumer_segment', ['vpn_score', 'dns_score', 'download_risk_score', 'cracked_apps_score'], 'Average risk pattern by segment'),
            width='stretch',
        )
    with c4:
        st.plotly_chart(violin(df, 'generation', 'risk_behavior_score', 'Risk score distribution by generation', color_map=PALETTE_GENERATION), width='stretch')

    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(bar_metric_by_group(df, 'generation', 'vpn_score', 'Average VPN score by generation', agg='mean', color_map=PALETTE_GENERATION), width='stretch')
    with c6:
        st.plotly_chart(
            scatter(df, 'engagement_score', 'raw_risk_intensity_score', 'access_style', 'Engagement vs raw risk intensity', color_map=PALETTE_ACCESS_STYLE, size='raw_illicit_channel_count'),
            width='stretch',
        )

    c7, c8 = st.columns(2)
    with c7:
        st.plotly_chart(bar_metric_by_group(df, 'generation', 'dns_score', 'Average DNS-tinkering score by generation', agg='mean', color_map=PALETTE_GENERATION), width='stretch')
    with c8:
        st.plotly_chart(bar_metric_by_group(df, 'generation', 'cracked_apps_score', 'Average cracked-app score by generation', agg='mean', color_map=PALETTE_GENERATION), width='stretch')

    st.subheader('Access-style structure by generation')
    mix = access_mix_summary(df, 'generation')
    st.plotly_chart(bar_grouped(mix, 'generation', 'share', 'access_style', 'Generation × access style share', color_map=PALETTE_ACCESS_STYLE), width='stretch')
