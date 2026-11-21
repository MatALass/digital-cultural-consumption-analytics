"""Page 2 : qui sont les répondants."""

from __future__ import annotations

import streamlit as st

from dcca import config as cfg
from dcca.app import charts, theme
from dcca.app.data import View
from dcca.app.text import compare_extremes, pct
from dcca.stats import share_table


def render(view: View, tables) -> None:
    r = view.respondents
    theme.header(
        "Qui sont les répondants ?",
        "Avant de regarder les pratiques, il faut savoir qui a répondu. Ifop a "
        "construit l'échantillon par quotas (sexe, âge, profession, région, taille "
        "de commune) pour qu'il ressemble aux internautes français de 15 ans et "
        "plus. Cette page sert surtout à vérifier ce point.",
    )

    st.subheader("Sexe et âge")
    left, right = st.columns(2)
    with left:
        sex = r["sexe"].value_counts().reindex(cfg.SEX_LABELS.values()).dropna()
        theme.chart(
            charts.donut(sex, "Répartition par sexe", [theme.BLUE, theme.NAVY]),
            "sex",
        )
    with right:
        theme.chart(
            charts.histogram(
                r["age"].astype(float),
                "Âge des répondants",
                "Âge",
                nbins=17,
                marker=float(r["age"].median()),
                marker_label=f"médiane : {int(r['age'].median())} ans",
            ),
            "age",
        )
    women = (r["sexe"] == "Femme").mean()
    st.info(
        f"{pct(women)} de femmes et {pct(1 - women)} d'hommes, âge médian de "
        f"**{int(r['age'].median())} ans**. Les moins de 35 ans représentent "
        f"{pct(r['tranche_age'].isin(['15-24 ans', '25-34 ans']).mean())} de la "
        "sélection. Ce sont eux qui pèsent le plus dans les pratiques illicites "
        "(page Consommation illicite)."
    )
    st.markdown("---")

    st.subheader("Où et comment ils vivent")
    left, right = st.columns(2)
    with left:
        agglo = r["agglomeration"].value_counts().reindex(cfg.AGGLOMERATION_ORDER)
        theme.chart(
            charts.count_bars(agglo.dropna().astype(int), "Taille de la commune"),
            "agglo",
        )
    with right:
        status = r["statut_foyer"].value_counts()
        theme.chart(charts.donut(status, "Situation dans le foyer"), "household")
    st.info(
        f"{pct((r['agglomeration'] == 'Commune rurale').mean())} des répondants "
        "vivent dans une commune rurale et "
        f"{pct((r['agglomeration'] == 'Agglomération parisienne').mean())} dans "
        f"l'agglomération parisienne. {pct((r['statut_foyer'] == 'En couple').mean())}"
        " vivent en couple."
    )
    st.markdown("---")

    st.subheader("Profession")
    csp = r["csp"].value_counts()
    theme.chart(charts.count_bars(csp, "Catégorie socioprofessionnelle", height=460), "csp")
    st.markdown("---")

    st.subheader("Qui ne consomme rien en ligne ?")
    table = share_table(r, "consommateur", "tranche_age", cfg.AGE_GROUP_ORDER)
    theme.chart(
        charts.share_bars(
            table,
            "tranche_age",
            "Part de répondants qui consomment au moins un contenu en ligne",
            horizontal=False,
            height=380,
        ),
        "consumer_by_age",
    )
    st.info(
        "Consommer au moins un contenu culturel en ligne : "
        + compare_extremes(table, "tranche_age")
        + " Les barres d'erreur donnent l'intervalle de confiance à 95 %."
    )

    non_consumers = r[~r["consommateur"]]
    if len(non_consumers) >= 30:
        older = (non_consumers["tranche_age"] == "65 ans et plus").mean()
        lead = f"{pct(older)} des non-consommateurs ont 65 ans ou plus."
    else:
        lead = "Trop peu de non-consommateurs dans cette sélection pour les décrire."
    theme.callout(
        "Le profil type",
        [
            "L'échantillon a la structure attendue (quotas Ifop), ce qui rend les "
            "comparaisons entre groupes lisibles. Le fichier n'a pas de poids : "
            "les chiffres sont bruts (page Méthode et limites).",
            f"Presque tout le monde consomme quelque chose en ligne. {lead}",
            "Le vrai sujet n'est donc pas l'accès à Internet, mais ce que les gens "
            "acceptent de payer : c'est l'objet des pages suivantes.",
        ],
    )
