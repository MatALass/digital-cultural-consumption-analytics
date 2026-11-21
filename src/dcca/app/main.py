"""Point d'entrée du dashboard : `streamlit run app.py`."""

from __future__ import annotations

import html

import streamlit as st

from dcca.app import theme
from dcca.app.data import FILTERS, MissingDataError, apply_filters, get_tables
from dcca.app.pages import (
    abonnements,
    contenus,
    illicite,
    methode,
    overview,
    paiement,
    profil,
    segments,
)
from dcca.app.text import integer
from dcca.stats import MIN_BASE

PAGES = {
    "Vue d'ensemble": overview,
    "Profil des répondants": profil,
    "Ce qu'on consomme": contenus,
    "Payer ou non": paiement,
    "Abonnements partagés": abonnements,
    "Consommation illicite": illicite,
    "Segments": segments,
    "Méthode et limites": methode,
}


def _sidebar(tables) -> tuple[dict[str, str], str]:
    sb = st.sidebar
    sb.markdown(
        '<div class="sidebar-brand"><div class="overline">Baromètre Arcom 2024</div>'
        '<div class="title">Culture numérique<br>en France</div></div><hr>',
        unsafe_allow_html=True,
    )
    sb.markdown('<div class="sidebar-section">Filtres</div>', unsafe_allow_html=True)
    filters = {}
    for column, (label, all_value, options) in FILTERS.items():
        filters[column] = sb.selectbox(label, [all_value, *options], key=f"f_{column}")

    lines = "".join(
        f"{html.escape(FILTERS[c][0])} : <span>{html.escape(v)}</span><br>"
        for c, v in filters.items()
    )
    sb.markdown(
        f'<div class="filter-tag"><strong>Sélection actuelle</strong>{lines}</div>',
        unsafe_allow_html=True,
    )
    sb.markdown("<hr>", unsafe_allow_html=True)
    page = sb.radio("Navigation", list(PAGES), label_visibility="collapsed", key="page")
    sb.markdown(
        '<div class="sidebar-footer">© 2026 Mathieu Alassoeur<br>'
        "Données : Arcom, enquête Ifop 2024</div>",
        unsafe_allow_html=True,
    )
    return filters, page


def run_app() -> None:
    st.set_page_config(page_title="Culture numérique en France", page_icon="📊", layout="wide")
    theme.apply_page_style()
    theme.register_plotly_template()

    try:
        tables = get_tables()
    except MissingDataError:
        st.title("Culture numérique en France")
        st.error(
            "Les tables d'analyse sont introuvables dans `data/processed/`. "
            "Lance `dcca build` à la racine du projet pour les reconstruire "
            "depuis le fichier brut de l'Arcom, puis recharge la page."
        )
        return

    filters, page = _sidebar(tables)
    view = apply_filters(tables, filters)

    n = len(view.respondents)
    if n == 0:
        st.title(page)
        st.error(
            "Aucun répondant ne correspond à cette sélection. "
            "Élargis un des filtres dans la barre de gauche."
        )
        return
    if n < MIN_BASE:
        st.title(page)
        st.warning(
            f"Seulement {n} répondants dans cette sélection : c'est trop peu pour "
            f"calculer des parts fiables (minimum {MIN_BASE}). Élargis les filtres."
        )
        return
    if view.is_filtered:
        st.caption(
            f"Sélection : {integer(n)} répondants sur {integer(view.total)}. "
            "Les barres grisées reposent sur moins de 30 répondants."
        )

    with st.spinner("Mise à jour du dashboard..."):
        PAGES[page].render(view, tables)


if __name__ == "__main__":
    run_app()
