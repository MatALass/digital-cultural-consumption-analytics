"""Page 8 : méthode, bases et limites."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dcca.app import theme
from dcca.app.data import View, get_codebook
from dcca.app.text import integer, pct


def render(view: View, tables) -> None:
    full = tables.respondents
    theme.header(
        "Méthode et limites",
        "D'où viennent les chiffres, sur quelle base ils sont calculés, et ce "
        "qu'ils ne disent pas.",
    )

    st.subheader("Source")
    st.markdown(
        "- **Enquête** : Baromètre 2024 de la consommation des contenus culturels et "
        "sportifs dématérialisés, réalisé par **Ifop pour l'Arcom** (terrain "
        "avril-mai 2024).\n"
        "- **Données** : fichier individuel publié sur data.gouv.fr sous Licence "
        "Ouverte 2.0, avec son dictionnaire des variables. Crédit : Arcom.\n"
        f"- **Échantillon** : {integer(len(full))} internautes de 15 ans et plus, "
        "construit par quotas (sexe, âge, profession, région, taille de commune).\n"
        "- **Fond de carte** : contours des régions de france-geojson (données "
        "Admin Express, Licence Ouverte)."
    )

    st.subheader("Deux sous-échantillons, donc deux bases")
    st.markdown(
        "Le questionnaire existe en deux versions. Les questions sur le gratuit et "
        "le payant, la dépense, les raisons de l'illicite et les applis crackées "
        "ne sont posées qu'au sous-échantillon B. Chaque indicateur est donc calculé "
        "sur la base qui a vraiment reçu la question :"
    )
    consumers = full[full["consommateur"]]
    b = consumers[consumers["sous_echantillon"] == "B"]
    bases = pd.DataFrame(
        [
            (
                "Consommer en ligne, contenus, fréquence",
                "Tous les répondants",
                len(full),
            ),
            ("Légal ou illégal, par contenu", "Tous les consommateurs", len(consumers)),
            (
                "Abonnements, comptes extérieurs, offre avec pub",
                "Tous les répondants",
                len(full),
            ),
            ("VPN, DNS alternatif", "Tous les répondants", len(full)),
            (
                "Gratuit ou payant, dépense mensuelle",
                "Consommateurs du sous-échantillon B",
                len(b),
            ),
            (
                "Raisons de ne pas passer par le légal",
                "Consommateurs illicites du sous-échantillon B",
                int(b["illicite"].sum()),
            ),
            ("Segments", "Tous les consommateurs", len(consumers)),
        ],
        columns=["Indicateur", "Base", "Effectif"],
    )
    bases["Effectif"] = bases["Effectif"].map(integer)
    st.dataframe(bases, hide_index=True, width="stretch")

    st.subheader("Pas de pondération")
    legal_only = (full["consommateur"] & ~full["illicite"]).mean()
    st.markdown(
        "Le fichier publié ne contient pas de variable de poids, alors que l'Arcom "
        "redresse ses résultats. Tous les chiffres ici sont donc **bruts**. Les "
        "intervalles de confiance (Wilson à 95 %, bootstrap pour les médianes) "
        "supposent un tirage aléatoire simple : sur un échantillon par quotas, ils "
        "donnent un ordre de grandeur de la précision, pas une garantie.\n\n"
        "Pour vérifier que l'écart reste raisonnable, je compare deux chiffres à "
        "ceux publiés par l'Arcom pour 2024 :"
    )
    check = pd.DataFrame(
        [
            (
                "Internautes qui consomment au moins un contenu",
                "91 %",
                pct(full["consommateur"].mean(), 1),
            ),
            (
                "Internautes qui consomment uniquement légalement",
                "67 %",
                pct(legal_only, 1),
            ),
        ],
        columns=["Indicateur", "Arcom 2024 (pondéré)", "Ce projet (brut)"],
    )
    st.dataframe(check, hide_index=True, width="stretch")
    st.markdown(
        "Le premier chiffre colle. Le second est 2 points plus haut chez moi : "
        "soit l'effet du redressement, soit une définition un peu différente de "
        "l'Arcom. Je ne peux pas trancher sans les poids. Pour la dépense, l'Arcom "
        "publie une moyenne de 32 € dont je ne connais pas la base exacte : je ne la "
        "compare pas."
    )

    st.subheader("Définitions")
    st.markdown(
        "- **Consommateur** : cite au moins un contenu (y compris « autre ») à la "
        "question Q1.\n"
        "- **Consommateur illicite** : répond autre chose que « uniquement de façon "
        "légale » pour au moins un contenu (Q5). Variante stricte : au moins autant "
        "d'illégal que de légal.\n"
        "- **Abonné payant** : abonné dans son foyer à au moins un des huit types "
        "d'abonnement culturel (RS12BIS), hors « autre abonnement ».\n"
        "- **Compte extérieur** : utilise le compte d'une personne hors du foyer, "
        "pour au moins un type d'abonnement.\n"
        "- **Score d'intensité** : 50 % étendue (contenus consommés sur 12) + 50 % "
        "régularité (fréquence moyenne des contenus consommés), ramené sur 100.\n"
        "- **Dépense** : montant mensuel déclaré (QBU2). La valeur 999 est traitée "
        "comme un code de saisie."
    )

    st.subheader("Limites")
    st.markdown(
        "- **Déclaratif** : l'illicite est sans doute sous-déclaré, même en ligne.\n"
        "- **Ligne par ligne** : les lignes de la grille d'abonnements (RS12BIS) n'ont "
        "pas de libellé dans le dictionnaire. Je les ai reprises de la question "
        "suivante (RS16BIS), et un test vérifie que les filtres du questionnaire ont "
        "exactement les mêmes effectifs.\n"
        "- **Petites bases** : la Corse compte 12 répondants. Toute part calculée "
        "sur moins de 30 personnes est grisée ou masquée.\n"
        "- **Pas de causalité** : les liens avec l'âge ou le segment sont des "
        "corrélations, pas des effets."
    )

    st.subheader("Chercher une question du questionnaire")
    codebook = get_codebook()
    query = st.text_input("Mot-clé (ex. VPN, abonnement, prix)", "")
    if query:
        rows = [
            (name, var.title)
            for name, var in codebook.variables.items()
            if query.lower() in var.title.lower() or query.lower() in name.lower()
        ]
        if rows:
            st.dataframe(
                pd.DataFrame(rows, columns=["Variable", "Intitulé"]),
                hide_index=True,
                width="stretch",
            )
        else:
            st.info(f"Aucune question ne contient « {query} ».")
