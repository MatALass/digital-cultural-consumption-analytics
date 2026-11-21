"""Graphiques Plotly du dashboard, tous dans la même charte de bleus."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dcca.app import theme
from dcca.app.text import NBSP, pct

HEIGHT = 420


def _text_color(background: str) -> str:
    """Texte blanc sur fond foncé, bleu nuit sur fond clair."""
    if not isinstance(background, str) or not background.startswith("#"):
        return "white"
    r, g, b = (int(background[i : i + 2], 16) for i in (1, 3, 5))
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return theme.NAVY if luminance > 0.6 else "white"


def _pct_axis(fig: go.Figure, axis: str = "x", max_value: float | None = None) -> None:
    update = dict(tickformat=".0%", rangemode="tozero")
    if max_value is not None:
        update["range"] = [0, min(1.0, max_value * 1.18 + 0.02)]
    if axis == "x":
        fig.update_xaxes(**update)
    else:
        fig.update_yaxes(**update)


def share_bars(
    table: pd.DataFrame,
    category: str,
    title: str,
    horizontal: bool = True,
    color: str = theme.BLUE,
    highlight: str | None = None,
    height: int = HEIGHT,
    colors: dict[str, str] | None = None,
) -> go.Figure:
    """Barres de parts avec intervalle de confiance à 95 %.

    Les modalités dont la base est trop petite sont grisées.
    """
    df = table.copy()
    df["couleur"] = np.where(df["fiable"], color, theme.GREY)
    if colors is not None:
        df["couleur"] = [
            colors.get(c, color) if ok else theme.GREY
            for c, ok in zip(df[category], df["fiable"], strict=True)
        ]
    if highlight is not None:
        df.loc[df[category] == highlight, "couleur"] = theme.ACCENT
    err_plus = (df["ic_haut"] - df["part"]).clip(lower=0)
    err_minus = (df["part"] - df["ic_bas"]).clip(lower=0)
    labels = [
        pct(p) if ok else f"{pct(p)} (base {b})"
        for p, ok, b in zip(df["part"], df["fiable"], df["base"], strict=True)
    ]
    hover = (
        "<b>%{customdata[0]}</b><br>%{customdata[1]}<br>"
        "IC 95 % : %{customdata[2]}<br>Base : %{customdata[3]} répondants<extra></extra>"
    )
    custom = np.column_stack(
        [
            df[category].astype(str),
            [pct(p, 1) for p in df["part"]],
            [
                f"{pct(lo, 1)} à {pct(hi, 1)}"
                for lo, hi in zip(df["ic_bas"], df["ic_haut"], strict=True)
            ],
            df["base"],
        ]
    )
    bar = go.Bar(
        x=df["part"] if horizontal else df[category],
        y=df[category] if horizontal else df["part"],
        orientation="h" if horizontal else "v",
        marker_color=df["couleur"],
        text=labels,
        textposition="inside",
        insidetextanchor="start",
        textfont=dict(color=[_text_color(c) for c in df["couleur"]], size=13),
        constraintext="none",
        customdata=custom,
        hovertemplate=hover,
    )
    error = dict(
        type="data",
        array=err_plus,
        arrayminus=err_minus,
        color="#8A9BB0",
        thickness=1.2,
    )
    if horizontal:
        bar.error_x = error
    else:
        bar.error_y = error
    fig = go.Figure(bar)
    fig.update_layout(title=title, height=height, showlegend=False)
    top = float(df["ic_haut"].max()) if not df.empty else 1.0
    if horizontal:
        _pct_axis(fig, "x", top)
        fig.update_yaxes(autorange="reversed", title=None)
        fig.update_xaxes(title=None)
    else:
        _pct_axis(fig, "y", top)
        fig.update_xaxes(title=None)
        fig.update_yaxes(title=None)
    return fig


def stacked_shares(
    df: pd.DataFrame,
    category: str,
    stack: str,
    title: str,
    category_order: list[str],
    stack_order: list[str],
    colors: dict[str, str] | list[str] | None = None,
    height: int = HEIGHT,
) -> go.Figure:
    """Barres empilées à 100 % : répartition de `stack` dans chaque `category`."""
    counts = df.groupby([category, stack], observed=True).size().rename("n").reset_index()
    counts["part"] = counts["n"] / counts.groupby(category)["n"].transform("sum")
    if isinstance(colors, dict):
        color_map = colors
    else:
        palette = colors or theme.BLUES
        color_map = {s: palette[i % len(palette)] for i, s in enumerate(stack_order)}
    fig = px.bar(
        counts,
        y=category,
        x="part",
        color=stack,
        orientation="h",
        category_orders={category: category_order, stack: stack_order},
        color_discrete_map=color_map,
        custom_data=[stack, "n"],
        text=counts["part"].map(lambda p: pct(p) if p >= 0.06 else ""),
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>%{customdata[0]} : %{x:.1%}<br>"
        "%{customdata[1]} répondants<extra></extra>",
        textposition="inside",
        insidetextanchor="middle",
    )
    for trace in fig.data:
        trace.textfont = dict(color=_text_color(trace.marker.color), size=12)
    fig.update_layout(title=title, height=height, barmode="stack", legend_title=None)
    fig.update_layout(legend=dict(y=1.02, yanchor="bottom", font=dict(size=12)))
    _pct_axis(fig, "x")
    fig.update_xaxes(range=[0, 1], title=None)
    fig.update_yaxes(title=None)
    return fig


def heatmap(pivot: pd.DataFrame, title: str, height: int = HEIGHT) -> go.Figure:
    text = pivot.map(lambda v: pct(v) if pd.notna(v) else "")
    fig = go.Figure(
        go.Heatmap(
            z=pivot.to_numpy(),
            x=list(pivot.columns),
            y=list(pivot.index),
            colorscale="Blues",
            text=text.to_numpy(),
            texttemplate="%{text}",
            textfont=dict(size=12),
            hovertemplate="%{y} · %{x}<br>%{z:.1%}<extra></extra>",
            colorbar=dict(tickformat=".0%", title=None, thickness=12),
        )
    )
    fig.update_layout(title=title, height=height)
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(side="top")
    return fig


def _rings(geometry: dict) -> list[list[list[float]]]:
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"][0]]
    return [poly[0] for poly in geometry["coordinates"]]


def _interpolate(colorscale: str, t: float) -> str:
    scale = px.colors.get_colorscale(colorscale)
    return px.colors.sample_colorscale(scale, [min(max(t, 0.0), 1.0)])[0]


def region_map(
    values: pd.DataFrame,
    geojson: dict,
    value: str,
    title: str,
    colorscale: str = "Blues",
    is_share: bool = False,
) -> go.Figure:
    """Carte des régions dessinée à partir du GeoJSON local.

    Je trace les contours moi-même plutôt que d'utiliser px.choropleth : le
    fond de carte de Plotly se télécharge depuis un CDN, que certains réseaux
    (entreprise, déploiement hors ligne) bloquent, et la carte restait vide.
    """
    data = values.set_index("region")
    known = data[value].dropna()
    vmin, vmax = (float(known.min()), float(known.max())) if len(known) else (0.0, 1.0)
    span = (vmax - vmin) or 1.0
    lat0 = np.cos(np.radians(46.5))  # projection simple, juste pour la France
    fig = go.Figure()
    for feature in geojson["features"]:
        name = feature["properties"]["nom"]
        v = data[value].get(name, np.nan)
        has_value = pd.notna(v)
        fill = _interpolate(colorscale, (v - vmin) / span) if has_value else "#F1F4F8"
        text = data["texte"].get(name, "") if has_value else "base trop faible"
        for ring in _rings(feature["geometry"]):
            lon, lat = zip(*ring, strict=True)
            fig.add_trace(
                go.Scatter(
                    x=np.array(lon) * lat0,
                    y=lat,
                    mode="lines",
                    fill="toself",
                    fillcolor=fill,
                    line=dict(color="white", width=1),
                    hoveron="fills",
                    hoverinfo="text",
                    text=f"<b>{name}</b><br>{text}",
                    showlegend=False,
                )
            )
    # Trace invisible qui porte l'échelle de couleur
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(
                colorscale=colorscale,
                cmin=vmin,
                cmax=vmax,
                color=[vmin],
                showscale=True,
                colorbar=dict(
                    thickness=12,
                    len=0.7,
                    tickformat=".0%" if is_share else ",d",
                ),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.update_layout(
        title=title,
        height=520,
        margin=dict(l=0, r=0, t=50, b=0),
        hovermode="closest",
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)
    return fig


def donut(counts: pd.Series, title: str, colors: list[str] | None = None) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            labels=counts.index.astype(str),
            values=counts.to_numpy(),
            hole=0.55,
            sort=False,
            marker=dict(colors=colors or theme.BLUES[1:], line=dict(color="white", width=2)),
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>%{value} répondants (%{percent})<extra></extra>",
        )
    )
    fig.update_layout(title=title, height=HEIGHT, legend=dict(orientation="v", x=1, y=0.5))
    return fig


def histogram(
    values: pd.Series,
    title: str,
    x_title: str,
    nbins: int = 30,
    color: str = theme.BLUE,
    marker: float | None = None,
    marker_label: str = "",
) -> go.Figure:
    fig = go.Figure(
        go.Histogram(
            x=values,
            nbinsx=nbins,
            marker_color=color,
            marker_line=dict(color="white", width=1),
            hovertemplate="%{x}<br>%{y} répondants<extra></extra>",
        )
    )
    if marker is not None:
        fig.add_vline(x=marker, line_dash="dash", line_color=theme.NAVY)
        fig.add_annotation(
            x=marker,
            y=1,
            yref="paper",
            text=marker_label,
            showarrow=False,
            xanchor="left",
            xshift=6,
            font=dict(color=theme.NAVY, size=13),
        )
    fig.update_layout(title=title, height=HEIGHT, bargap=0.05)
    fig.update_xaxes(title=x_title)
    fig.update_yaxes(title="Répondants")
    return fig


def count_bars(
    counts: pd.Series, title: str, color: str = theme.BLUE_DARK, height: int = HEIGHT
) -> go.Figure:
    total = counts.sum()
    fig = go.Figure(
        go.Bar(
            x=counts.to_numpy(),
            y=counts.index.astype(str),
            orientation="h",
            marker_color=color,
            text=[f"{v:,}".replace(",", NBSP) + f" ({pct(v / total)})" for v in counts],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x} répondants<extra></extra>",
        )
    )
    fig.update_layout(title=title, height=height, showlegend=False)
    fig.update_yaxes(autorange="reversed", title=None)
    fig.update_xaxes(title=None, range=[0, counts.max() * 1.3 if len(counts) else 1])
    return fig


def median_bars(
    table: pd.DataFrame,
    category: str,
    title: str,
    unit: str = "€",
    height: int = HEIGHT,
) -> go.Figure:
    """Médianes avec intervalle bootstrap (colonnes mediane, ic_bas, ic_haut, base)."""
    fig = go.Figure(
        go.Bar(
            x=table[category],
            y=table["mediane"],
            marker_color=theme.BLUE,
            error_y=dict(
                type="data",
                array=table["ic_haut"] - table["mediane"],
                arrayminus=table["mediane"] - table["ic_bas"],
                color="#8A9BB0",
                thickness=1.2,
            ),
            text=[f"{m:.0f}{NBSP}{unit}" for m in table["mediane"]],
            textposition="outside",
            cliponaxis=False,
            customdata=np.column_stack([table["ic_bas"], table["ic_haut"], table["base"]]),
            hovertemplate=(
                "<b>%{x}</b><br>Médiane : %{y:.0f} "
                + unit
                + "<br>IC 95 % : %{customdata[0]:.0f} à %{customdata[1]:.0f} "
                + unit
                + "<br>Base : %{customdata[2]}<extra></extra>"
            ),
        )
    )
    fig.update_layout(title=title, height=height, showlegend=False)
    fig.update_yaxes(title=None, rangemode="tozero", ticksuffix=f"{NBSP}{unit}")
    fig.update_xaxes(title=None)
    return fig


def grouped_shares(
    df: pd.DataFrame,
    category: str,
    group: str,
    title: str,
    colors: dict[str, str],
    category_order: list[str] | None = None,
    height: int = HEIGHT,
) -> go.Figure:
    """Barres groupées de parts (colonnes part, ic_bas, ic_haut) par groupe."""
    fig = go.Figure()
    for name, sub in df.groupby(group, sort=False):
        fig.add_bar(
            name=str(name),
            y=sub[category],
            x=sub["part"],
            orientation="h",
            marker_color=colors.get(name, theme.BLUE),
            error_x=dict(
                type="data",
                array=(sub["ic_haut"] - sub["part"]).clip(lower=0),
                arrayminus=(sub["part"] - sub["ic_bas"]).clip(lower=0),
                color="#8A9BB0",
                thickness=1,
            ),
            text=[pct(p) for p in sub["part"]],
            textposition="inside",
            insidetextanchor="start",
            textfont=dict(color=_text_color(colors.get(name, theme.BLUE)), size=12),
            constraintext="none",
            hovertemplate="<b>%{y}</b><br>" + str(name) + " : %{x:.1%}<extra></extra>",
        )
    fig.update_layout(title=title, height=height, barmode="group", legend_title=None)
    _pct_axis(fig, "x", float(df["ic_haut"].max()) if not df.empty else 1.0)
    fig.update_yaxes(
        autorange="reversed",
        title=None,
        categoryorder="array" if category_order else None,
        categoryarray=category_order,
    )
    fig.update_xaxes(title=None)
    return fig


def box_by_group(
    df: pd.DataFrame, group: str, value: str, title: str, order: list[str], colors: dict
) -> go.Figure:
    fig = px.box(
        df,
        x=group,
        y=value,
        color=group,
        category_orders={group: order},
        color_discrete_map=colors,
        points=False,
    )
    fig.update_layout(title=title, height=HEIGHT, showlegend=False)
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None, range=[0, 100])
    return fig
