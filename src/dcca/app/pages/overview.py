"""Page 1 : vue d'ensemble."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dcca.app import charts, theme
from dcca.app.data import View, get_geojson
from dcca.app.text import eur, integer, interval, one_in, pct
from dcca.stats import MIN_BASE, bootstrap_median, share, share_table


def _region_table(view: View) -> pd.DataFrame:
    r = view.respondents
    consumers = view.consumers
    counts = r.groupby("region").size().rename("repondants")
    illicit = consumers.groupby("region")["illicite"].agg(["mean", "size"])
    out = pd.concat([counts, illicit], axis=1).reset_index()
    out.columns = ["region", "repondants", "part_illicite", "base"]
    out["part_illicite"] = out["part_illicite"].where(out["base"] >= MIN_BASE)
    return out


def render(view: View, tables) -> None:
    r = view.respondents
    consumers = view.consumers
    b = view.subsample_b

    consuming = share(r["consommateur"])
    illicit = share(consumers["illicite"])
    paying = share(b["payeur"])
    median, _, _ = bootstrap_median(b["depense_mensuelle"])

    theme.header(
        "Culture numérique en France : qui consomme, qui paie, qui pirate ?",
        "Musique, films, séries, jeux vidéo, presse : en 2024, la consommation "
        "culturelle passe d'abord par Internet. Ce dashboard reprend les réponses "
        f"des <strong>{integer(len(r))} internautes</strong> interrogés par Ifop pour "
        "l'Arcom, et cherche à répondre à trois questions : <strong>qui consomme "
        "quoi, qui paie, et qui passe par l'illégal</strong>.",
    )

    theme.kpi_row(
        [
            theme.kpi("Répondants", integer(len(r)), "internautes de 15 ans et plus"),
            theme.kpi(
                "Consomment en ligne",
                pct(consuming.value),
                f"IC 95 % {interval(consuming.low, consuming.high)}",
            ),
            theme.kpi(
                "Paient chaque mois",
                pct(paying.value),
                f"des consommateurs (base {integer(paying.base)})",
            ),
            theme.kpi("Dépense médiane", eur(median), "par mois, payeurs ou non"),
            theme.kpi(
                "Passent par l'illégal",
                pct(illicit.value),
                "des consommateurs, au moins parfois",
                accent=True,
            ),
        ]
    )
    st.markdown("---")

    regions = _region_table(view)
    regions["texte"] = [f"{integer(n)} répondants" for n in regions["repondants"]]
    geo = get_geojson()
    left, right = st.columns(2)
    with left:
        theme.chart(
            charts.region_map(regions, geo, "repondants", "Où vivent les répondants"),
            "map_respondents",
        )
    with right:
        shown = regions.dropna(subset=["part_illicite"]).copy()
        shown["texte"] = [
            f"{pct(p)} des consommateurs ({integer(n)} consommateurs)"
            for p, n in zip(shown["part_illicite"], shown["base"], strict=True)
        ]
        if shown.empty:
            st.info("Pas assez de répondants par région pour cette carte.")
        else:
            theme.chart(
                charts.region_map(
                    shown,
                    geo,
                    "part_illicite",
                    "Part de consommateurs qui passent par l'illégal",
                    colorscale="YlGnBu",
                    is_share=True,
                ),
                "map_illicit",
            )

    top_region = regions.sort_values("repondants", ascending=False).iloc[0]
    reliable = regions.dropna(subset=["part_illicite"])
    region_text = (
        f"L'échantillon suit la population : **{top_region['region']}** pèse "
        f"{pct(top_region['repondants'] / len(r))} des répondants. "
    )
    if len(reliable) >= 2:
        hi = reliable.loc[reliable["part_illicite"].idxmax()]
        lo = reliable.loc[reliable["part_illicite"].idxmin()]
        region_text += (
            f"La consommation illicite va de {pct(lo['part_illicite'])} "
            f"({lo['region']}) à {pct(hi['part_illicite'])} ({hi['region']}). "
            "L'écart entre régions est faible à côté de l'écart entre tranches "
            "d'âge (page Consommation illicite) : la géographie explique peu. "
        )
    region_text += (
        f"Les régions de moins de {MIN_BASE} consommateurs (la Corse, par exemple) "
        "sont laissées en blanc."
    )
    st.info(region_text)

    top_contents = view.contents["contenu"].value_counts().index[:2].str.lower()
    by_age = share_table(consumers, "illicite", "tranche_age")
    by_age = by_age[by_age["fiable"]]
    age_text = (
        f", surtout chez les {by_age.loc[by_age['part'].idxmax(), 'tranche_age']}"
        if len(by_age) >= 2
        else ""
    )
    hybrids = (consumers["segment"] == "Hybrides").sum()
    illicit_n = consumers["illicite"].sum()
    paying_share_of_illicit = hybrids / illicit_n if illicit_n else float("nan")
    theme.callout(
        "À retenir",
        [
            f"<strong>{pct(consuming.value)}</strong> des internautes consomment au "
            "moins un contenu culturel en ligne. En tête : "
            f"{' et '.join(top_contents)}.",
            f"<strong>{one_in(illicit.value).capitalize()}</strong> consommateurs passe "
            f"par l'illégal, au moins de temps en temps{age_text}.",
            f"Parmi eux, <strong>{pct(paying_share_of_illicit)}</strong> paient déjà "
            "un abonnement : le piratage complète l'offre payante bien plus qu'il "
            "ne la remplace.",
        ],
    )
