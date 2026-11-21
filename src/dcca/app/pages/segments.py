"""Page 7 : segmentation des consommateurs."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from scipy import stats as sps

from dcca import config as cfg
from dcca.app import charts, theme
from dcca.app.data import View
from dcca.app.text import eur, integer, pct
from dcca.segments import SEGMENT_ORDER, SEGMENTS, segment_shares_by_variant
from dcca.stats import MIN_BASE, independence_test, share


def segment_table(consumers: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for segment in SEGMENT_ORDER:
        sh = share(consumers["segment"] == segment)
        rows.append(
            {
                "segment": segment,
                "part": sh.value,
                "ic_bas": sh.low,
                "ic_haut": sh.high,
                "base": sh.base,
                "fiable": sh.reliable,
                "n": sh.successes,
            }
        )
    return pd.DataFrame(rows)


def profile_table(consumers: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for segment in SEGMENT_ORDER:
        g = consumers[consumers["segment"] == segment]
        spend = g["depense_mensuelle"].dropna()
        rows.append(
            {
                "Segment": segment,
                "Effectif": len(g),
                "Moins de 35 ans": pct(g["tranche_age"].isin(["15-24 ans", "25-34 ans"]).mean())
                if len(g)
                else "n.d.",
                "Score d'intensité médian": f"{g['score_intensite'].median():.0f}"
                if len(g)
                else "n.d.",
                "Dépense médiane (B)": eur(spend.median())
                if len(spend) >= MIN_BASE
                else "base < 30",
                "VPN (12 mois)": pct(g["vpn_12_mois"].mean()) if len(g) else "n.d.",
                "OK pour la pub": pct(g["offre_pub_acceptee"].mean()) if len(g) else "n.d.",
            }
        )
    return pd.DataFrame(rows)


def render(view: View, tables) -> None:
    consumers = view.consumers
    theme.header(
        "Cinq profils de consommateurs",
        "Pour passer de la description à la décision, je range chaque consommateur "
        "dans un segment à partir de <strong>deux questions</strong> : paie-t-il au "
        "moins un abonnement culturel dans son foyer, et passe-t-il par l'illégal, "
        "même rarement ? Ceux qui ne paient pas sont séparés selon qu'ils utilisent "
        "ou non le compte de quelqu'un d'autre.",
    )
    if len(consumers) < MIN_BASE:
        st.warning("Pas assez de consommateurs dans cette sélection.")
        return

    rules = pd.DataFrame({"Segment": list(SEGMENTS), "Règle": list(SEGMENTS.values())})
    st.dataframe(rules, hide_index=True, width="stretch")

    table = segment_table(consumers)
    theme.chart(
        charts.share_bars(
            table,
            "segment",
            f"Répartition des {integer(len(consumers))} consommateurs",
            colors=theme.SEGMENT_COLORS,
            height=380,
        ),
        "segments",
    )
    shares = table.set_index("segment")["part"]
    illicit_total = shares["Hybrides"] + shares["Illicites sans abonnement"]
    paying_illicit = shares["Hybrides"] / illicit_total if illicit_total else float("nan")
    st.info(
        f"Les **abonnés légaux** forment le premier groupe ({pct(shares['Abonnés légaux'])}). "
        f"Le résultat le plus parlant : parmi les consommateurs illicites, "
        f"**{pct(paying_illicit)} paient déjà au moins un abonnement** (les hybrides). "
        f"Les illicites qui ne paient rien ne pèsent que "
        f"{pct(shares['Illicites sans abonnement'])} des consommateurs."
    )
    st.markdown("---")

    st.subheader("Les segments changent avec l'âge")
    theme.chart(
        charts.stacked_shares(
            consumers,
            "tranche_age",
            "segment",
            "Composition de chaque tranche d'âge",
            category_order=cfg.AGE_GROUP_ORDER,
            stack_order=SEGMENT_ORDER,
            colors=theme.SEGMENT_COLORS,
            height=400,
        ),
        "segments_age",
    )
    test = independence_test(consumers, "segment", "tranche_age")
    if test.n:
        strength = (
            "forte" if test.cramers_v >= 0.3 else "moyenne" if test.cramers_v >= 0.15 else "faible"
        )
        p_text = "< 0,001" if test.p_value < 0.001 else f"{test.p_value:.3f}".replace(".", ",")
        st.info(
            f"Test du khi-deux entre segment et tranche d'âge : p {p_text}, V de "
            f"Cramér = {test.cramers_v:.2f}".replace(".", ",", 1)
            + f". Le lien est réel et d'intensité **{strength}** : l'âge ne fait pas "
            "tout, mais il déplace nettement le poids des segments, surtout celui "
            "des hybrides."
        )
    else:
        st.info("Le filtre ne laisse qu'une tranche d'âge : le test n'a pas de sens ici.")
    st.markdown("---")

    st.subheader("Portrait de chaque segment")
    st.dataframe(profile_table(consumers), hide_index=True, width="stretch")
    left, right = st.columns([3, 2])
    with left:
        theme.chart(
            charts.box_by_group(
                consumers,
                "segment",
                "score_intensite",
                "Score d'intensité par segment",
                SEGMENT_ORDER,
                theme.SEGMENT_COLORS,
            ),
            "segment_score",
        )
    with right:
        b = view.subsample_b.dropna(subset=["depense_mensuelle"])
        if len(b) >= MIN_BASE:
            rho_spend = sps.spearmanr(b["score_intensite"], b["depense_mensuelle"])
            rho_subs = sps.spearmanr(consumers["score_intensite"], consumers["n_abonnements"])
            st.markdown(
                "**Le score tient-il la route ?** Il n'utilise ni la dépense ni les "
                "abonnements, donc je peux le confronter à ces deux variables :\n\n"
                f"- corrélation de Spearman avec la dépense : "
                f"**{rho_spend.statistic:.2f}**".replace(".", ",")
                + "\n" f"- avec le nombre d'abonnements : **{rho_subs.statistic:.2f}**".replace(
                    ".", ","
                )
                + "\n\nUne corrélation positive et modérée : le score capte bien "
                "l'engagement, sans être un simple doublon de la dépense."
            )
    st.markdown("---")

    st.subheader("Les segments changent-ils si je change les règles ?")
    variants = segment_shares_by_variant(view.respondents)
    shown = variants.map(pct)
    shown.index.name = "Variante"
    st.dataframe(shown.reset_index(), hide_index=True, width="stretch")
    paying_share = variants["Hybrides"] / (
        variants["Hybrides"] + variants["Illicites sans abonnement"]
    )
    strict = "Illicite = au moins autant d'illégal que de légal"
    st.info(
        "Le seuil de l'illicite est la seule règle qui compte. Avec la définition "
        "stricte, les hybrides passent de "
        f"{pct(variants.iloc[0]['Hybrides'])} à {pct(variants.loc[strict, 'Hybrides'])}"
        " : la plupart ne piratent que de temps en temps. Mais la part des "
        "illicites qui paient un abonnement bouge à peine "
        f"({pct(paying_share.iloc[0])} contre {pct(paying_share[strict])}) : le "
        "résultat principal tient. Inclure « autre abonnement » ne change presque "
        "rien."
    )

    def seg_rate(segment: str, column: str) -> float:
        g = consumers[consumers["segment"] == segment]
        return g[column].mean() if len(g) else float("nan")

    def seg_median(segment: str) -> float:
        g = consumers[consumers["segment"] == segment]
        return g["score_intensite"].median() if len(g) else float("nan")

    def seg_young(segment: str) -> float:
        g = consumers[consumers["segment"] == segment]
        return g["tranche_age"].isin(["15-24 ans", "25-34 ans"]).mean() if len(g) else float("nan")

    theme.callout(
        "Lecture métier",
        [
            "<strong>Cible prioritaire</strong> : les abonnés par procuration "
            f"({pct(shares['Abonnés par procuration'])}). Ils consomment déjà l'offre "
            "légale avec le compte d'un proche, et "
            f"{pct(seg_rate('Abonnés par procuration', 'offre_pub_acceptee'))} "
            "accepteraient une offre moins chère avec publicité.",
            f"<strong>Peu convertible</strong> : le gratuit légal "
            f"({pct(shares['Gratuit légal'])}). Seulement "
            f"{pct(seg_young('Gratuit légal'))} ont moins de 35 ans, leur score "
            f"d'intensité médian est de {seg_median('Gratuit légal'):.0f} et "
            f"{pct(seg_rate('Gratuit légal', 'offre_pub_acceptee'))} seulement "
            "accepteraient la pub : ils consomment peu et n'en attendent pas plus.",
            "<strong>Les hybrides</strong> ne sont pas des pirates à convertir : ils "
            "paient déjà. Pour eux, le sujet est le catalogue et le prix des "
            "abonnements en plus, pas l'accès au légal.",
        ],
    )
