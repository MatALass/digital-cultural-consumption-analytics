from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from dashboard.utils.viz import (
    bar_count,
    bar_grouped,
    bar_metric_by_group,
    box,
    funnel_chart,
    heatmap_share,
    histogram,
    indicator_gauge,
    line_chart,
    radar_chart,
    scatter,
    sunburst,
    treemap,
    violin,
)

def _df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            'group': ['A', 'A', 'B', 'B'],
            'subgroup': ['X', 'Y', 'X', 'Y'],
            'value': [1, 2, 3, 4],
            'metric': [10, 20, 30, 40],
        }
    )

def test_all_factories_return_figures():
    df = _df()
    grouped = df.groupby(['group', 'subgroup']).size().reset_index(name='respondents')
    radar_df = pd.DataFrame({'segment': ['A', 'B'], 'vpn_score': [1, 2], 'dns_score': [0, 1]})

    figures = [
        bar_count(df, 'group', 'title'),
        bar_metric_by_group(df, 'group', 'metric', 'title', agg='mean'),
        heatmap_share(df, 'group', 'subgroup', 'title'),
        histogram(df, 'metric', 'title'),
        scatter(df, 'value', 'metric', 'group', 'title'),
        box(df, 'group', 'metric', 'title'),
        violin(df, 'group', 'metric', 'title'),
        treemap(grouped, ['group', 'subgroup'], 'respondents', 'title'),
        sunburst(grouped, ['group', 'subgroup'], 'respondents', 'title'),
        funnel_chart(pd.DataFrame({'stage': ['A', 'B'], 'value': [10, 5]}), 'stage', 'value', 'title'),
        line_chart(pd.DataFrame({'x': ['Q1', 'Q2'], 'y': [1, 2]}), 'x', 'y', 'title'),
        bar_grouped(pd.DataFrame({'x': ['A', 'A'], 'y': [1, 2], 'color': ['m1', 'm2']}), 'x', 'y', 'color', 'title'),
        radar_chart(radar_df, 'segment', ['vpn_score', 'dns_score'], 'title'),
        indicator_gauge(0.7, 'title'),
    ]
    assert all(isinstance(fig, go.Figure) for fig in figures)
