"""Page 6 : consommation illicite."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dcca import config as cfg
from dcca.app import charts, theme
from dcca.app.data import View
from dcca.app.text import compare_extremes, integer, pct
from dcca.stats import MIN_BASE, share, share_table


def _flag_table(df: pd.DataFrame, flag: str, by: str, label_col: str) -> pd.DataFrame:
    out = share_table(df, flag, by)
    return out.rename(columns={by: label_col})


def render(view: View, tables) -> None:
    consumers = view.consumers
    b = view.subsample_b
    theme.header(
        "Consommation illicite",
        "Pour chaque contenu, le répondant dit s'il le consomme uniquement "
        "légalement, surtout légalement, autant l'un que l'autre, surtout ou "
        "uniquement illégalement. Je compte comme <strong>consommateur illicite</"
        "strong> toute personne qui passe par l'illégal pour au moins un contenu, "
        "même rarement.",
    )
    illicit = share(consumers["illicite"])
    marked = share(consumers["illicite_marque"])
    vpn_illicit = share(consumers.loc[consumers["illicite"], "vpn_12_mois"])
    vpn_legal = share(consumers.loc[~consumers["illicite"], "vpn_12_mois"])
    theme.kpi_row(
        [
            theme.kpi(
                "Consommateurs illicites",
                pct(illicit.value),
                f"des {integer(illicit.base)} consommateurs",
                accent=True,
            ),
            theme.kpi(
                "Au moins autant d'illégal que de légal",
                pct(marked.value),
                "pour au moins un contenu",
                accent=True,
            ),
            theme.kpi(
                "VPN chez les illicites",
                pct(vpn_illicit.value),
                "utilisé dans les 12 derniers mois",
            ),
            theme.kpi("VPN chez les autres", pct(vpn_legal.value), "même question"),
        ]
    )
    st.markdown("---")

    st.subheader("Quels contenus, et qui")
    left, right = st.columns(2)
    with left:
        by_content = share_table(view.contents, "illicite", "contenu").sort_values(
            "part", ascending=False
        )
        theme.chart(
            charts.share_bars(
                by_content,
                "contenu",
                "Part de consommateurs qui passent par l'illégal, par contenu",
                color=theme.ACCENT,
                height=470,
            ),
            "illicit_content",
        )
    with right:
        by_age = share_table(consumers, "illicite", "tranche_age", cfg.AGE_GROUP_ORDER)
        theme.chart(
            charts.share_bars(
                by_age,
                "tranche_age",
                "Consommateurs illicites par tranche d'âge",
                horizontal=False,
                color=theme.ACCENT,
                height=470,
            ),
            "illicit_age",
        )
    reliable = by_content[by_content["fiable"]]
    st.info(
        f"Les contenus les plus piratés sont **{reliable.iloc[0]['contenu'].lower()}** "
        f"({pct(reliable.iloc[0]['part'])}) et **{reliable.iloc[1]['contenu'].lower()}** "
        f"({pct(reliable.iloc[1]['part'])}). Par âge, " + compare_extremes(by_age, "tranche_age")
        if len(reliable) >= 2
        else "Pas assez de consommateurs dans cette sélection pour comparer les contenus."
    )
    st.markdown("---")

    st.subheader("Par quels moyens (films et séries)")
    means = view.illicit_means
    if means["id"].nunique() >= MIN_BASE:
        means_table = means.groupby(["contenu", "moyen"])["cite"].agg(["sum", "size"]).reset_index()
        means_table = means_table[means_table["sum"] > 0]
        rows = []
        for row in means_table.itertuples(index=False):
            sh = share(pd.Series([True] * int(row.sum) + [False] * int(row.size - row.sum)))
            rows.append(
                {
                    "contenu": row.contenu,
                    "moyen": row.moyen,
                    "part": sh.value,
                    "ic_bas": sh.low,
                    "ic_haut": sh.high,
                }
            )
        grouped = pd.DataFrame(rows)
        order = grouped.groupby("moyen")["part"].mean().sort_values(ascending=False).index.tolist()
        theme.chart(
            charts.grouped_shares(
                grouped,
                "moyen",
                "contenu",
                "Moyens utilisés, parmi les consommateurs illicites de films ou de séries",
                {"Films": theme.ACCENT, "Séries": "#F7B9A3"},
                category_order=order,
                height=480,
            ),
            "means",
        )
        films = grouped[grouped["contenu"] == "Films"].set_index("moyen")["part"]
        st.info(
            f"Le streaming domine largement : {pct(films.get('Sites de streaming', 0))} "
            "des consommateurs illicites de films passent par des sites de streaming, "
            f"loin devant le pair-à-pair ({pct(films.get('Pair-à-pair, torrent', 0))}). "
            f"L'IPTV illicite concerne déjà {pct(films.get('IPTV illicite', 0))} d'entre eux."
        )
    else:
        st.info("Trop peu de consommateurs illicites de films ou de séries ici.")
    st.markdown("---")

    st.subheader("Pourquoi ne pas passer par le légal")
    reasons = view.reasons
    n_asked = reasons["id"].nunique()
    if n_asked >= MIN_BASE:
        reason_table = _flag_table(reasons, "citee", "raison", "raison")
        reason_table = (
            reason_table[~reason_table["raison"].isin(["Autre raison", "Aucune de ces raisons"])]
            .sort_values("part", ascending=False)
            .head(10)
        )
        theme.chart(
            charts.share_bars(
                reason_table,
                "raison",
                f"Raisons citées par les consommateurs illicites (base {integer(n_asked)})",
                color=theme.BLUE_DARK,
                height=460,
            ),
            "reasons",
        )
        price = reason_table.set_index("raison")["part"]
        st.info(
            f"Le prix arrive en tête : {pct(price.iloc[0])} citent "
            f"« {price.index[0].lower()} » et {pct(price.iloc[1])} « "
            f"{price.index[1].lower()} ». Plusieurs réponses étaient possibles. "
            "Question posée au seul sous-échantillon B."
        )
    else:
        st.info("Trop peu de répondants à cette question dans la sélection.")

    seniority = b.loc[b["illicite"], "anciennete_illicite"].dropna()
    old_habit = (seniority == "Plus de 5 ans").mean() if len(seniority) else float("nan")
    theme.callout(
        "Ce qu'il faut retenir",
        [
            f"<strong>{pct(illicit.value)}</strong> des consommateurs passent par "
            f"l'illégal au moins de temps en temps, mais seulement {pct(marked.value)} "
            "autant ou plus que par le légal.",
            "Le prix est le premier frein au légal, loin devant la qualité de " "l'offre.",
            f"{pct(old_habit)} des consommateurs illicites le font depuis plus de "
            "5 ans : c'est une habitude installée, pas un essai.",
        ],
    )
