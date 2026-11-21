"""Page 4 : gratuit ou payant, et combien."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dcca import config as cfg
from dcca.app import charts, theme
from dcca.app.data import View
from dcca.app.text import eur, integer, pct
from dcca.stats import MIN_BASE, bootstrap_median, share

SPEND_DISPLAY_CAP = 150  # au-delà, regroupé dans la dernière barre de l'histogramme


def median_table(df: pd.DataFrame, by: str, value: str, order: list[str]) -> pd.DataFrame:
    rows = []
    for level in order:
        values = df.loc[df[by] == level, value].dropna()
        if len(values) < MIN_BASE:
            continue
        m, lo, hi = bootstrap_median(values, n_boot=1000)
        rows.append({by: level, "mediane": m, "ic_bas": lo, "ic_haut": hi, "base": len(values)})
    return pd.DataFrame(rows, columns=[by, "mediane", "ic_bas", "ic_haut", "base"])


def render(view: View, tables) -> None:
    b = view.subsample_b
    theme.header(
        "Payer ou non",
        "Ces questions n'ont été posées qu'à une partie de l'échantillon (le "
        f"sous-échantillon B, ici <strong>{integer(len(b))} consommateurs</strong>). "
        "Les parts de cette page se lisent donc sur cette base.",
    )
    if len(b) < MIN_BASE:
        st.warning("Pas assez de répondants du sous-échantillon B dans cette sélection.")
        return

    spend = b["depense_mensuelle"].dropna()
    payers = spend[spend > 0]
    paying = share(b["payeur"])
    med_all = bootstrap_median(spend)
    med_payers = bootstrap_median(payers)
    theme.kpi_row(
        [
            theme.kpi("Paient chaque mois", pct(paying.value), f"base {integer(paying.base)}"),
            theme.kpi(
                "Dépense médiane",
                eur(med_all[0]),
                f"IC 95 % : {eur(med_all[1])} à {eur(med_all[2])}",
            ),
            theme.kpi(
                "Médiane chez les payeurs",
                eur(med_payers[0]),
                f"IC 95 % : {eur(med_payers[1])} à {eur(med_payers[2])}",
            ),
            theme.kpi(
                "Dépense moyenne",
                eur(spend.mean()),
                "tirée vers le haut par quelques gros budgets",
            ),
        ]
    )
    st.markdown("---")

    st.subheader("Gratuit ou payant, contenu par contenu")
    c = view.contents[view.contents["paiement"].notna()]
    order = (
        c.assign(paid=c["paiement_code"] >= 4)
        .groupby("contenu")["paid"]
        .mean()
        .sort_values(ascending=False)
        .index.tolist()
    )
    theme.chart(
        charts.stacked_shares(
            c,
            "contenu",
            "paiement",
            "Mode d'accès, parmi les consommateurs de chaque contenu",
            category_order=order,
            stack_order=cfg.PAYMENT_ORDER,
            colors=["#CFE5FF", "#9CCBFF", "#5AAEFF", theme.BLUE_DARK, theme.NAVY],
            height=500,
        ),
        "payment_mode",
    )
    paid = c.assign(paid=c["paiement_code"] >= 4).groupby("contenu")["paid"].mean()
    free = c.assign(free=c["paiement_code"] == 1).groupby("contenu")["free"].mean()
    mostly_free = c.assign(f=c["paiement_code"] <= 2).groupby("contenu")["f"].mean()
    st.info(
        f"**{paid.idxmax()}** est le contenu le plus payé : {pct(paid.max())} de ses "
        f"consommateurs paient surtout ou uniquement. À l'opposé, {pct(free.max())} "
        f"des consommateurs de **{free.idxmax().lower()}** ne paient jamais. Pour "
        f"{(mostly_free > 0.5).sum()} contenus sur {len(mostly_free)}, la majorité "
        "des consommateurs passe surtout ou uniquement par le gratuit."
    )
    st.markdown("---")

    st.subheader("Combien par mois")
    left, right = st.columns(2)
    with left:
        capped = spend.clip(upper=SPEND_DISPLAY_CAP)
        theme.chart(
            charts.histogram(
                capped,
                "Dépense mensuelle déclarée",
                f"€ par mois (dernière barre : {SPEND_DISPLAY_CAP} € et plus)",
                nbins=30,
                marker=med_all[0],
                marker_label=f"médiane : {eur(med_all[0])}",
            ),
            "spend_hist",
        )
    with right:
        table = median_table(b, "tranche_age", "depense_mensuelle", cfg.AGE_GROUP_ORDER)
        if len(table) >= 2:
            theme.chart(
                charts.median_bars(table, "tranche_age", "Dépense médiane par tranche d'âge"),
                "spend_age",
            )
        else:
            st.info("Le filtre laisse trop peu de tranches d'âge pour comparer.")
    zero = (spend == 0).mean()
    above = (spend >= 100).mean()
    st.info(
        f"{pct(zero)} des consommateurs déclarent ne rien dépenser, et "
        f"{pct(above)} dépensent 100 € ou plus par mois. La médiane "
        f"({eur(med_all[0])}) décrit mieux le cas typique que la moyenne "
        f"({eur(spend.mean())}). Une valeur saisie à 999 € a été retirée : c'est un "
        "code de saisie, pas une dépense."
    )

    subscribers = view.respondents[view.respondents["abonne_payant"]]
    budget = subscribers["budget_abonnements"].dropna()
    theme.callout(
        "Ce qu'il faut retenir",
        [
            f"<strong>{pct(paying.value)}</strong> des consommateurs paient chaque mois "
            f"pour des contenus en ligne, pour une médiane de {eur(med_payers[0])} "
            "chez ceux qui paient.",
            f"Le payant est le plus présent pour {paid.idxmax().lower()} "
            f"({pct(paid.max())} paient surtout ou uniquement), mais le gratuit reste "
            f"majoritaire pour {(mostly_free > 0.5).sum()} contenus sur "
            f"{len(mostly_free)}.",
            f"Côté abonnements, les foyers abonnés déclarent un budget médian de "
            f"<strong>{eur(budget.median())}</strong> par mois, tous abonnements "
            "confondus.",
        ],
    )
