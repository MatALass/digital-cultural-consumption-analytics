"""Identité visuelle du dashboard : celle de la première version (octobre 2025),
reprise et nettoyée.

- sidebar en dégradé bleu nuit, texte blanc, titre en capitales ;
- carte « Sélection actuelle » sous les filtres ;
- graphiques en dégradés de bleus ;
- un bloc bleu d'interprétation sous chaque graphique (st.info) ;
- un encadré bleu clair qui conclut chaque page.
"""

from __future__ import annotations

import html

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

NAVY = "#0A2540"
NAVY_LIGHT = "#133B66"
BLUE = "#1E90FF"
BLUE_DARK = "#1E5AA8"
SKY = "#7FDBFF"
PALE = "#E8F1FB"
INK = "#0E1117"
MUTED = "#5B6B7F"
GREY = "#B6C2CF"
ACCENT = "#F28C6B"  # réservé à ce qui relève de l'illicite

BLUES = ["#0A2540", "#133B66", "#1E5AA8", "#1E90FF", "#5AAEFF", "#9CCBFF", "#CFE5FF"]

SEGMENT_COLORS = {
    "Abonnés légaux": NAVY,
    "Hybrides": BLUE,
    "Abonnés par procuration": SKY,
    "Gratuit légal": GREY,
    "Illicites sans abonnement": ACCENT,
    "Non-consommateurs": "#E3E8EE",
}

CSS = f"""
<style>
/* === SIDEBAR === */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {NAVY} 0%, {NAVY_LIGHT} 100%) !important;
}}
[data-testid="stSidebar"] * {{ color: #FFFFFF; }}
[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.25); }}
.sidebar-brand {{ text-align: center; margin: 0.5rem 0 1.2rem 0; }}
.sidebar-brand .overline {{
    font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
    color: {SKY} !important; font-weight: 600;
}}
.sidebar-brand .title {{
    font-size: 21px; font-weight: 800; text-transform: uppercase;
    letter-spacing: 0.5px; line-height: 1.2; margin-top: 4px;
}}
.sidebar-section {{
    text-align: center; font-weight: 700; font-size: 15px;
    text-transform: uppercase; letter-spacing: 0.5px; margin: 0.6rem 0 0.4rem 0;
}}

/* === FILTRES (selectbox) ===
   Deux structures selon la version de Streamlit : react-aria (récente)
   et baseweb (ancienne). Les deux sont couvertes. */
[data-testid="stSidebar"] label p {{ font-size: 14px; font-weight: 500; }}
[data-testid="stSidebar"] [data-testid="stSelectbox"] [role="group"],
[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background: rgba(255,255,255,0.12) !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: 8px !important;
    transition: background 0.2s ease;
}}
[data-testid="stSidebar"] [data-testid="stSelectbox"] [role="group"]:hover,
[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {{
    background: rgba(255,255,255,0.22) !important;
}}
[data-testid="stSidebar"] [data-testid="stSelectbox"] input,
[data-testid="stSidebar"] div[data-baseweb="select"] * {{
    color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF;
    font-weight: 600; background: transparent !important;
}}
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {{ fill: #FFFFFF !important; color: #FFFFFF !important; }}
div[data-baseweb="popover"] li, [role="listbox"] [role="option"] {{
    color: {NAVY} !important; font-size: 14px;
}}

/* === CARTE « SÉLECTION ACTUELLE » === */
.filter-tag {{
    background-color: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 8px; padding: 10px 12px; margin-top: 10px;
    font-size: 14px; line-height: 1.55;
}}
.filter-tag strong {{ display: block; margin-bottom: 2px; }}
.filter-tag span {{ color: {SKY} !important; font-weight: 600; }}

/* === NAVIGATION === */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{ gap: 2px; width: 100%; }}
[data-testid="stSidebar"] [data-testid="stRadioOption"] {{ width: 100%; }}
[data-testid="stSidebar"] .stRadio label {{
    border-radius: 8px; padding: 6px 12px; width: 100%; box-sizing: border-box;
    transition: background 0.2s ease; cursor: pointer;
}}
[data-testid="stSidebar"] .stRadio label:hover {{ background: rgba(255,255,255,0.10); }}
/* on masque la pastille ronde : la ligne entière devient le bouton */
[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child,
[data-testid="stSidebar"] .stRadio label > div:first-child:not(:has(p)) {{ display: none; }}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {{
    background-color: #FFFFFF;
}}
[data-testid="stSidebar"] .stRadio label:has(input:checked) * {{
    color: {NAVY} !important; font-weight: 700;
}}
[data-testid="stSidebar"] .stRadio label p {{ font-size: 15px; }}
.sidebar-footer {{
    text-align: center; font-size: 12px; color: rgba(255,255,255,0.7) !important;
    margin-top: 1rem; line-height: 1.5;
}}

/* === CONTENU === */
.block-container {{ padding-top: 2.2rem; max-width: 1250px; }}
h1 {{ color: {INK}; font-weight: 800 !important; }}
.lead {{ font-size: 17px; color: #2B3440; line-height: 1.6; margin-bottom: 0.4rem; }}
.kpi-card {{
    background: #FFFFFF; border: 1px solid #E3E8EE; border-left: 5px solid {BLUE};
    border-radius: 10px; padding: 14px 16px; min-height: 118px;
    box-shadow: 0 2px 6px rgba(10,37,64,0.05);
}}
.kpi-card.accent {{ border-left-color: {ACCENT}; }}
.kpi-label {{ font-size: 13px; color: {MUTED}; font-weight: 600; }}
.kpi-value {{ font-size: 30px; font-weight: 800; color: {NAVY}; line-height: 1.2; }}
.kpi-note {{ font-size: 12px; color: {MUTED}; margin-top: 2px; }}
.callout {{
    background-color: {PALE}; border-left: 6px solid {BLUE};
    padding: 20px 25px; border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05); margin-top: 25px;
}}
.callout h3 {{ color: {INK}; font-weight: 700; margin: 0 0 8px 0; padding: 0; }}
.callout p, .callout li {{ font-size: 17px; color: #1c1c1c; line-height: 1.6; }}
.callout ul {{ margin: 0; padding-left: 1.2rem; }}
footer, #MainMenu {{ visibility: hidden; }}
</style>
"""


def apply_page_style() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def register_plotly_template() -> None:
    template = go.layout.Template()
    template.layout = go.Layout(
        font=dict(family="Source Sans Pro, sans-serif", size=14, color="#2B3440"),
        title=dict(font=dict(size=17, color=INK), x=0, xanchor="left"),
        colorway=BLUES[1:],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        separators=", ",
        margin=dict(l=10, r=10, t=60, b=10),
        xaxis=dict(gridcolor="#EEF2F6", zeroline=False, linecolor="#D5DCE4"),
        yaxis=dict(gridcolor="#EEF2F6", zeroline=False, linecolor="#D5DCE4"),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, title=None),
        hoverlabel=dict(bgcolor="#FFFFFF", font_size=13),
    )
    pio.templates["dcca"] = template
    pio.templates.default = "plotly_white+dcca"


def kpi(label: str, value: str, note: str = "", accent: bool = False) -> str:
    cls = "kpi-card accent" if accent else "kpi-card"
    note_html = f'<div class="kpi-note">{html.escape(note)}</div>' if note else ""
    return (
        f'<div class="{cls}"><div class="kpi-label">{html.escape(label)}</div>'
        f'<div class="kpi-value">{html.escape(value)}</div>{note_html}</div>'
    )


def kpi_row(cards: list[str]) -> None:
    for col, card in zip(st.columns(len(cards)), cards, strict=True):
        col.markdown(card, unsafe_allow_html=True)


def callout(title: str, items: list[str]) -> None:
    """Encadré de fin de page. Les items peuvent contenir du gras en <strong>."""
    body = "".join(f"<li>{item}</li>" for item in items)
    st.markdown(
        f'<div class="callout"><h3>{html.escape(title)}</h3><ul>{body}</ul></div>',
        unsafe_allow_html=True,
    )


def header(title: str, lead: str) -> None:
    """Titre de page et phrase d'accroche (HTML autorisé, ex. <strong>)."""
    st.title(title)
    st.markdown(f'<p class="lead">{lead}</p>', unsafe_allow_html=True)


def chart(fig, key: str) -> None:
    st.plotly_chart(fig, width="stretch", key=key, config={"displaylogo": False})
