# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 1. Exploration et qualité des données
#
# Ce notebook part du fichier brut publié par l'Arcom et explique comment je
# construis les tables d'analyse. Toute la logique est dans `src/dcca` : ici je
# ne fais que l'appeler et montrer les vérifications.
#
# Le fichier : Baromètre 2024 de la consommation des contenus culturels et
# sportifs dématérialisés, enquête Ifop pour l'Arcom, publié sur data.gouv.fr
# sous Licence Ouverte 2.0.

# %%
import pandas as pd

from dcca import config as cfg
from dcca.build import build_tables, read_raw
from dcca.codebook import load_codebook
from dcca.quality import run_quality_checks

pd.set_option("display.max_columns", 20)
raw = read_raw()
codebook = load_codebook()
print(f"{raw.shape[0]} répondants, {raw.shape[1]} colonnes, ID unique : {raw['ID'].is_unique}")

# %% [markdown]
# ## Un fichier large, mais pas si gros
#
# 1 518 colonnes, mais la plupart viennent des grilles : une question comme
# « à quelle fréquence consommez-vous chaque contenu ? » occupe 14 colonnes
# (`Q2_r1` à `Q2_r14`), une par contenu. Le dictionnaire (`2024-datamap.xlsx`)
# compte 223 variables, dont une partie n'a pas été posée en 2024.

# %%
n_empty = int(raw.isna().all().sum())
print(f"{n_empty} colonnes entièrement vides (questions non posées cette année)")

# %% [markdown]
# ## Ce que l'ancienne version du projet lisait mal
#
# En reprenant le questionnaire, j'ai trouvé trois erreurs dans mon premier
# nettoyage. Elles expliquent pourquoi je reconstruis tout depuis le brut.
#
# **1. Les régions.** La variable `REG` n'est pas la région administrative mais
# la zone Ifop (UDA1 à UDA9). Le bon code est `REG13`. Le département le prouve :

# %%
check = pd.DataFrame(
    {
        "DPT": raw["DPT"],
        "REG (zone UDA)": raw["REG"].map(codebook.labels("REG")),
        "REG13": raw["REG13"].map(cfg.REGION_LABELS),
    }
)
check[check["DPT"].isin([13, 35, 75])].drop_duplicates().sort_values("DPT")

# %% [markdown]
# Les Bouches-du-Rhône (13) sont en zone UDA9, pas en UDA6 : lire `REG` comme
# une région plaçait donc des répondants dans la mauvaise région sur les cartes.
#
# **2. Les grilles par contenu.** La « légalité », le « gratuit ou payant » et
# la « fréquence » de l'ancienne table n'étaient que la première ligne de leur
# grille (`Q5_r1`, `QBU1_r1`, `Q2_r1`), c'est-à-dire la musique. Les 42 % de
# « valeurs manquantes » étaient les gens qui n'écoutent pas de musique en ligne.

# %%
print("Non-réponse à Q5_r1 :", f"{raw['Q5_r1'].isna().mean():.1%}")
print("Ne consomment pas de musique (Q1_1 = 0) :", f"{(raw['Q1_1'] == 0).mean():.1%}")

# %% [markdown]
# **3. Une ligne perdue.** L'ancien nettoyage supprimait un doublon, puis
# alignait le fichier nettoyé et le brut par numéro de ligne : 342 répondants
# récupéraient les réponses de leur voisin. Ici, tout passe par la colonne `ID`.

# %% [markdown]
# ## Deux sous-échantillons
#
# Le questionnaire existe en deux versions (`CELLULE`). Beaucoup de « valeurs
# manquantes » sont en fait des questions non posées, pas des non-réponses.

# %%
consumer = ~raw["Q1_11"].eq(11)
routing = pd.DataFrame(
    {
        "sous-échantillon": raw["CELLULE"].map({1: "A", 2: "B"}),
        "consommateur": consumer,
        "dépense (QBU2) renseignée": raw["QBU2"].notna(),
        "gratuit/payant (QBU1) renseigné": raw.filter(like="QBU1_r").notna().any(axis=1),
    }
)
routing.groupby(["sous-échantillon", "consommateur"]).sum()

# %% [markdown]
# La dépense n'est posée qu'aux consommateurs du sous-échantillon B. Chaque
# indicateur du dashboard est donc calculé sur sa vraie base.
#
# ## Les montants
#
# La dépense mensuelle est une saisie libre. Une seule valeur vaut 999 €, très
# au-dessus de toutes les autres : c'est un code de saisie, je la retire.

# %%
raw["QBU2"].describe(percentiles=[0.5, 0.9, 0.99]).round(1)

# %%
raw["QBU2"].sort_values(ascending=False).head(6).tolist()

# %% [markdown]
# ## Pas de variable de poids
#
# Le dictionnaire (feuille LEVELS) a une colonne `WEIGHT`, vide. L'Arcom redresse
# ses résultats mais ne publie pas les poids : tous les chiffres sont bruts.

# %%
pd.read_excel(cfg.DATAMAP_PATH, sheet_name="LEVELS")[["NAME", "WEIGHT"]]

# %% [markdown]
# ## Construction et contrôles qualité
#
# `build_tables` produit cinq tables (répondants, contenus, abonnements, moyens
# illicites, raisons). `run_quality_checks` vérifie le schéma, l'unicité, le
# routage et les valeurs plausibles. La commande `dcca build` s'arrête si un
# contrôle échoue.

# %%
tables = build_tables(raw)
failures = run_quality_checks(tables)
print("Contrôles en échec :", failures or "aucun")
{name: frame.shape for name, frame in tables.as_dict().items()}

# %%
tables.respondents.head(3).T
