"""Page 3 : ce que les gens consomment, et à quel rythme."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dcca import config as cfg
from dcca.app import charts, theme
from dcca.app.data import View
from dcca.app.text import pct
from dcca.stats import MIN_BASE, share


def penetration_table(view: View) -> pd.DataFrame:
    """Part des répondants qui consomment chaque contenu, avec IC."""
    r = view.respondents
    consumed = view.contents.groupby("contenu")["id"].nunique()
    rows = []
    for content in cfg.CONTENT_LABELS.values():
        mask = r["id"].isin(view.contents.loc[view.contents["contenu"] == content, "id"])
        s = share(mask)
        rows.append(
            {
                "contenu": content,
                "part": s.value,
                "ic_bas": s.low,
                "ic_haut": s.high,
                "base": s.base,
                "fiable": s.reliable,
                "n": int(consumed.get(content, 0)),
            }
        )
    return pd.DataFrame(rows).sort_values("part", ascending=False).reset_index(drop=True)


def render(view: View, tables) -> None:
    r = view.respondents
    c = view.contents
    theme.header(
        "Ce qu'on consomme en ligne",
        "Le questionnaire passe en revue douze contenus, de la musique aux "
        "spectacles vivants. Pour chacun, la personne dit si elle en consomme en "
        "ligne et à quelle fréquence.",
    )

    table = penetration_table(view)
    theme.chart(
        charts.share_bars(
            table,
            "contenu",
            "Part des répondants qui consomment chaque contenu",
            height=470,
        ),
        "penetration",
    )
    top, second, last = table.iloc[0], table.iloc[1], table.iloc[-1]
    mean_n = f"{view.consumers['n_contenus'].mean():.1f}".replace(".", ",")
    st.info(
        f"**{top['contenu']}** ({pct(top['part'])}) et **{second['contenu'].lower()}** "
        f"({pct(second['part'])}) sont les contenus les plus répandus. Tout en bas, "
        f"{last['contenu'].lower()} : {pct(last['part'])}. Un consommateur cite en "
        f"moyenne **{mean_n} contenus** sur douze."
    )
    st.markdown("---")

    st.subheader("L'âge change tout")
    age_n = r.groupby("tranche_age").size()
    merged = c.merge(r[["id", "tranche_age"]], on="id")
    pivot = (
        merged.groupby(["contenu", "tranche_age"])["id"]
        .nunique()
        .unstack()
        .reindex(columns=[a for a in cfg.AGE_GROUP_ORDER if a in age_n.index])
    )
    pivot = (pivot / age_n.reindex(pivot.columns)).reindex(table["contenu"])
    pivot = pivot.loc[:, age_n.reindex(pivot.columns) >= MIN_BASE]
    if pivot.shape[1] >= 2:
        theme.chart(
            charts.heatmap(pivot, "Part de chaque tranche d'âge qui consomme le contenu", 520),
            "heatmap_age",
        )
        gaps = (pivot.iloc[:, 0] - pivot.iloc[:, -1]).sort_values(ascending=False)
        st.info(
            f"Le plus gros écart concerne **{gaps.index[0].lower()}** : "
            f"{pct(pivot.loc[gaps.index[0]].iloc[0])} chez les {pivot.columns[0]}, "
            f"contre {pct(pivot.loc[gaps.index[0]].iloc[-1])} chez les "
            f"{pivot.columns[-1]}. À l'inverse, **{gaps.index[-1].lower()}** varie peu "
            "avec l'âge, voire progresse chez les plus âgés."
        )
    else:
        st.info("Le filtre ne laisse qu'une tranche d'âge : la comparaison est masquée.")
    st.markdown("---")

    st.subheader("À quel rythme")
    theme.chart(
        charts.stacked_shares(
            c,
            "contenu",
            "frequence",
            "Fréquence de consommation, parmi les consommateurs de chaque contenu",
            category_order=list(table["contenu"]),
            stack_order=cfg.FREQUENCY_ORDER,
            colors=[theme.NAVY, theme.BLUE_DARK, "#5AAEFF", "#CFE5FF"],
            height=500,
        ),
        "frequency",
    )
    daily = c.assign(q=c["frequence_code"] == 1).groupby("contenu")["q"].mean()
    least = ", ".join(daily.sort_values().index[:3].str.lower())
    st.info(
        f"**{daily.idxmax()}** est le contenu le plus quotidien : {pct(daily.max())} "
        "de ceux qui en consomment le font tous les jours ou presque. À l'autre "
        f"bout, {least} se consomment rarement au quotidien : ce sont des contenus "
        "de rendez-vous."
    )
    st.markdown("---")

    st.subheader("Un score pour résumer l'intensité")
    consumers = view.consumers
    left, right = st.columns([3, 2])
    with left:
        theme.chart(
            charts.box_by_group(
                consumers,
                "tranche_age",
                "score_intensite",
                "Score d'intensité (0 à 100) par tranche d'âge",
                cfg.AGE_GROUP_ORDER,
                dict(zip(cfg.AGE_GROUP_ORDER, theme.BLUES[1:], strict=False)),
            ),
            "score_age",
        )
    with right:
        st.markdown(
            "**Comment il est calculé.** Moitié étendue (nombre de contenus "
            "consommés sur 12), moitié régularité (tous les jours = 1, chaque "
            "semaine = 2/3, chaque mois = 1/3, moins souvent = 0, en moyenne sur "
            "les contenus consommés).\n\n"
            "**Pourquoi ces poids.** Je n'ai pas de cible pour les estimer, donc je "
            "garde le partage le plus simple à expliquer. Je vérifie ensuite que le "
            "score suit bien la dépense et le nombre d'abonnements (page Segments)."
        )
    med = consumers.groupby("tranche_age")["score_intensite"].median()
    theme.callout(
        "Ce qu'il faut retenir",
        [
            f"Les contenus les plus partagés sont <strong>{top['contenu'].lower()}"
            f"</strong> et <strong>{second['contenu'].lower()}</strong>.",
            "La pratique dépend d'abord de l'âge, plus que de la région ou de la "
            "taille de la commune.",
            f"Score d'intensité médian : {med.max():.0f} chez les {med.idxmax()}, "
            f"{med.min():.0f} chez les {med.idxmin()}."
            if len(med) >= 2
            else f"Score d'intensité médian : {med.iloc[0]:.0f}.",
        ],
    )
