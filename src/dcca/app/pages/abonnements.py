"""Page 5 : abonnements et comptes partagés."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dcca import config as cfg
from dcca.app import charts, theme
from dcca.app.data import View
from dcca.app.text import compare_extremes, integer, one_in, pct
from dcca.stats import share, share_table


def render(view: View, tables) -> None:
    r = view.respondents
    s = view.subscriptions
    theme.header(
        "Abonnements et comptes partagés",
        "Pour chaque type d'abonnement, le répondant dit s'il y est abonné dans son "
        "foyer, s'il utilise le compte d'une personne extérieure, ou s'il n'y a pas "
        "accès. La question est posée à tout l'échantillon.",
    )

    svod = share(r["abonne_svod"])
    shared_any = share(r["compte_exterieur"])
    shared_svod = share(r["compte_exterieur_svod"])
    ads = share(r["offre_pub_acceptee"])
    theme.kpi_row(
        [
            theme.kpi(
                "Abonnés SVOD dans le foyer",
                pct(svod.value),
                "Netflix, Disney+, Prime...",
            ),
            theme.kpi(
                "Utilisent un compte extérieur",
                pct(shared_any.value),
                "au moins un type d'abonnement",
            ),
            theme.kpi("Dont pour la SVOD", pct(shared_svod.value), "des répondants"),
            theme.kpi("Prêts pour une offre avec pub", pct(ads.value), "pour payer moins cher"),
        ]
    )
    st.markdown("---")

    st.subheader("Qui accède à quoi")
    order = (
        s.groupby("abonnement")["abonne_foyer"].mean().sort_values(ascending=False).index
    ).tolist()
    theme.chart(
        charts.stacked_shares(
            s,
            "abonnement",
            "statut",
            "Accès à chaque type d'abonnement",
            category_order=order,
            stack_order=cfg.SUBSCRIPTION_STATUS_ORDER,
            colors={
                cfg.SUBSCRIPTION_STATUS_ORDER[0]: theme.NAVY,
                cfg.SUBSCRIPTION_STATUS_ORDER[1]: theme.SKY,
                cfg.SUBSCRIPTION_STATUS_ORDER[2]: "#E3E8EE",
            },
            height=480,
        ),
        "subscription_status",
    )
    ratio = (
        s.groupby("abonnement")[["abonne_foyer", "compte_exterieur"]]
        .sum()
        .query("abonne_foyer >= 30")
    )
    ratio["ratio"] = ratio["compte_exterieur"] / ratio["abonne_foyer"]
    top = ratio["ratio"].idxmax() if not ratio.empty else None
    text = (
        f"La SVOD est l'abonnement le plus répandu ({pct(svod.value)} des foyers). "
        "Quand on rapporte les comptes extérieurs aux abonnés, le partage pèse "
        "le plus pour **"
        f"{top.lower()}** : {round(100 * ratio.loc[top, 'ratio'])} utilisateurs "
        "de compte extérieur pour 100 abonnés. Pour la SVOD, on en compte "
        f"{round(100 * ratio.loc['Vidéo à la demande (SVOD)', 'ratio'])} pour 100."
        if top and "Vidéo à la demande (SVOD)" in ratio.index
        else "Trop peu d'abonnés dans cette sélection pour comparer les types."
    )
    st.info(text)
    st.markdown("---")

    st.subheader("Qui partage, et avec qui")
    left, right = st.columns(2)
    with left:
        table = share_table(r, "compte_exterieur", "tranche_age", cfg.AGE_GROUP_ORDER)
        theme.chart(
            charts.share_bars(
                table,
                "tranche_age",
                "Utilisent le compte d'une personne extérieure au foyer",
                horizontal=False,
                color=theme.BLUE,
                height=400,
            ),
            "shared_age",
        )
    with right:
        users = s[s["compte_exterieur"]]
        per_person = users.groupby("id")[list(cfg.SHARED_CODE_ORIGIN_COLUMNS.values())].any()
        n_users = len(per_person)
        rows = []
        for code, column in cfg.SHARED_CODE_ORIGIN_COLUMNS.items():
            sh = share(per_person[column])
            rows.append(
                {
                    "origine": cfg.SHARED_CODE_ORIGIN_LABELS[code],
                    "part": sh.value,
                    "ic_bas": sh.low,
                    "ic_haut": sh.high,
                    "base": sh.base,
                    "fiable": sh.reliable,
                }
            )
        origin_table = pd.DataFrame(rows)
        origin = origin_table.set_index("origine")["part"]
        if n_users >= 30:
            theme.chart(
                charts.share_bars(
                    origin_table.sort_values("part", ascending=False),
                    "origine",
                    "À qui appartiennent les codes utilisés",
                    color=theme.BLUE_DARK,
                    height=400,
                ),
                "shared_origin",
            )
        else:
            st.info("Trop peu d'utilisateurs de comptes extérieurs dans cette sélection.")
    st.info(
        "Utiliser un compte extérieur : "
        + compare_extremes(table, "tranche_age")
        + (
            f" Les codes viennent surtout de la **famille** ({pct(origin['Famille'])} "
            f"des utilisateurs) et des **amis** ({pct(origin['Amis'])}). Les codes "
            f"trouvés sur Internet restent rares "
            f"({pct(origin['Codes trouvés sur Internet'])})."
            if n_users >= 30
            else ""
        )
    )
    st.markdown("---")

    st.subheader("Une offre moins chère avec publicité ?")
    ads_by = share_table(
        r.assign(profil=r["abonne_svod"].map({True: "Abonnés SVOD", False: "Non abonnés SVOD"})),
        "offre_pub_acceptee",
        "profil",
        ["Abonnés SVOD", "Non abonnés SVOD"],
    )
    theme.chart(
        charts.share_bars(
            ads_by,
            "profil",
            "Prêts à prendre une offre SVOD avec publicité",
            height=260,
        ),
        "ads",
    )
    st.info(
        "Être prêt à accepter la pub pour payer moins : "
        + compare_extremes(ads_by, "profil")
        + " La question ne dit pas à quel prix, donc c'est une intention, pas un "
        "comportement d'achat."
    )
    theme.callout(
        "Ce qu'il faut retenir",
        [
            f"<strong>{one_in(shared_any.value).capitalize()}</strong> répondants "
            "profite d'un abonnement payé par quelqu'un d'autre, presque toujours un "
            "proche.",
            "Ceux qui en profitent sans payer d'abonnement et sans passer par "
            "l'illégal (les abonnés par procuration, page Segments) sont les clients "
            "les plus simples à convertir pour les plateformes.",
            f"{pct(ads.value)} accepteraient la publicité pour payer moins : "
            f"{integer(round(ads.value * len(r)))} répondants dans cette sélection.",
        ],
    )
