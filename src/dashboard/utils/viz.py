from __future__ import annotations

import math
from typing import Iterable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboard.config import CHART_HEIGHT

def _empty_figure(title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text='No data available for the current filters',
        showarrow=False,
        x=0.5,
        y=0.5,
        xref='paper',
        yref='paper',
        font={'size': 16},
    )
    return _apply_layout(fig, title=title)

def _apply_layout(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title=title,
        template='plotly_dark',
        height=CHART_HEIGHT,
        margin={'l': 32, 'r': 24, 't': 64, 'b': 32},
        legend_title_text='',
        hoverlabel={'namelength': -1},
    )
    return fig

def _sort_frame(plot_df: pd.DataFrame, value_col: str, sort: str) -> pd.DataFrame:
    if sort == 'alphabetical':
        first_col = [c for c in plot_df.columns if c != value_col][0]
        return plot_df.sort_values(first_col)
    return plot_df.sort_values(value_col, ascending=(sort == 'asc'))

def bar_count(
    df: pd.DataFrame,
    column: str,
    title: str,
    *,
    orientation: str = 'v',
    color_map: dict[str, str] | None = None,
    normalize: bool = False,
    sort: str = 'desc',
):
    if df.empty:
        return _empty_figure(title)
    plot_df = df[column].astype(str).value_counts(dropna=False, normalize=normalize).rename_axis(column).reset_index(name='value')
    plot_df = _sort_frame(plot_df, 'value', sort)
    if orientation == 'h':
        fig = px.bar(plot_df, x='value', y=column, color=column, orientation='h', color_discrete_map=color_map)
    else:
        fig = px.bar(plot_df, x=column, y='value', color=column, color_discrete_map=color_map)
    if normalize:
        fig.update_yaxes(tickformat='.0%') if orientation == 'v' else fig.update_xaxes(tickformat='.0%')
    return _apply_layout(fig, title)

def bar_metric_by_group(
    df: pd.DataFrame,
    group_col: str,
    metric_col: str,
    title: str,
    *,
    agg: str = 'median',
    color_map: dict[str, str] | None = None,
    orientation: str = 'v',
    sort: str = 'desc',
):
    if df.empty:
        return _empty_figure(title)
    series = getattr(df.groupby(group_col, dropna=False)[metric_col], agg)()
    plot_df = series.reset_index().rename(columns={metric_col: 'value'})
    plot_df[group_col] = plot_df[group_col].astype(str)
    plot_df = _sort_frame(plot_df, 'value', sort)
    if orientation == 'h':
        fig = px.bar(plot_df, x='value', y=group_col, color=group_col, orientation='h', color_discrete_map=color_map)
    else:
        fig = px.bar(plot_df, x=group_col, y='value', color=group_col, color_discrete_map=color_map)
    return _apply_layout(fig, title)

def heatmap_share(df: pd.DataFrame, index: str, columns: str, title: str):
    if df.empty:
        return _empty_figure(title)
    ctab = pd.crosstab(df[index].astype(str), df[columns].astype(str), normalize='index')
    fig = px.imshow(ctab, aspect='auto', text_auto='.0%', color_continuous_scale='Tealgrn')
    fig.update_xaxes(title=columns)
    fig.update_yaxes(title=index)
    return _apply_layout(fig, title)

def histogram(df: pd.DataFrame, column: str, title: str, *, nbins: int = 25, color: str | None = None):
    if df.empty:
        return _empty_figure(title)
    fig = px.histogram(df, x=column, nbins=nbins, color=color)
    return _apply_layout(fig, title)

def scatter(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str,
    title: str,
    *,
    color_map: dict[str, str] | None = None,
    size: str | None = None,
):
    if df.empty:
        return _empty_figure(title)
    fig = px.scatter(df, x=x, y=y, color=color, opacity=0.7, color_discrete_map=color_map, size=size)
    return _apply_layout(fig, title)

def box(df: pd.DataFrame, x: str, y: str, title: str, *, color: str | None = None, color_map: dict[str, str] | None = None):
    if df.empty:
        return _empty_figure(title)
    fig = px.box(df, x=x, y=y, color=color or x, color_discrete_map=color_map)
    return _apply_layout(fig, title)

def violin(df: pd.DataFrame, x: str, y: str, title: str, *, color: str | None = None, color_map: dict[str, str] | None = None):
    if df.empty:
        return _empty_figure(title)
    fig = px.violin(df, x=x, y=y, color=color or x, box=True, points=False, color_discrete_map=color_map)
    return _apply_layout(fig, title)

def treemap(df: pd.DataFrame, path: list[str], values: str, title: str, *, color: str | None = None, color_map: dict[str, str] | None = None):
    if df.empty:
        return _empty_figure(title)
    fig = px.treemap(df, path=path, values=values, color=color, color_discrete_map=color_map)
    return _apply_layout(fig, title)

def sunburst(df: pd.DataFrame, path: list[str], values: str, title: str, *, color: str | None = None, color_map: dict[str, str] | None = None):
    if df.empty:
        return _empty_figure(title)
    fig = px.sunburst(df, path=path, values=values, color=color, color_discrete_map=color_map)
    return _apply_layout(fig, title)

def funnel_chart(df: pd.DataFrame, stage_col: str, value_col: str, title: str):
    if df.empty:
        return _empty_figure(title)
    fig = px.funnel(df, x=value_col, y=stage_col)
    return _apply_layout(fig, title)

def line_chart(df: pd.DataFrame, x: str, y: str, title: str, *, color: str | None = None, markers: bool = True):
    if df.empty:
        return _empty_figure(title)
    fig = px.line(df, x=x, y=y, color=color, markers=markers)
    return _apply_layout(fig, title)

def bar_grouped(df: pd.DataFrame, x: str, y: str, color: str, title: str, *, color_map: dict[str, str] | None = None):
    if df.empty:
        return _empty_figure(title)
    fig = px.bar(df, x=x, y=y, color=color, barmode='group', color_discrete_map=color_map)
    return _apply_layout(fig, title)

def radar_chart(df: pd.DataFrame, category_col: str, value_cols: Iterable[str], title: str):
    if df.empty:
        return _empty_figure(title)
    value_cols = list(value_cols)
    fig = go.Figure()
    theta = value_cols + [value_cols[0]]
    for _, row in df.iterrows():
        values = [float(row[col]) for col in value_cols]
        values.append(values[0])
        fig.add_trace(go.Scatterpolar(r=values, theta=theta, fill='toself', name=str(row[category_col])))
    fig.update_layout(polar={'radialaxis': {'visible': True, 'range': [0, max(1.0, math.ceil(df[value_cols].max().max()))]}})
    return _apply_layout(fig, title)

def indicator_gauge(value: float, title: str, *, min_value: float = 0.0, max_value: float = 1.0, suffix: str = ''):
    fig = go.Figure(
        go.Indicator(
            mode='gauge+number',
            value=float(value),
            number={'suffix': suffix},
            title={'text': title},
            gauge={'axis': {'range': [min_value, max_value]}},
        )
    )
    return _apply_layout(fig, title)
