"""Construction des tables d'analyse à partir du fichier brut de l'Arcom.

Une ligne du fichier brut = un répondant, identifié par la colonne ID. Toutes
les tables produites ici gardent cet ID, donc aucune jointure ne dépend de
l'ordre des lignes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from dcca import config as cfg
from dcca.scores import intensity_score
from dcca.segments import assign_segments


@dataclass(frozen=True)
class Tables:
    respondents: pd.DataFrame
    contents: pd.DataFrame
    subscriptions: pd.DataFrame
    illicit_means: pd.DataFrame
    reasons: pd.DataFrame

    @staticmethod
    def file_names() -> list[str]:
        return [
            cfg.RESPONDENTS_FILE,
            cfg.CONTENTS_FILE,
            cfg.SUBSCRIPTIONS_FILE,
            cfg.ILLICIT_MEANS_FILE,
            cfg.REASONS_FILE,
        ]

    def as_dict(self) -> dict[str, pd.DataFrame]:
        frames = [
            self.respondents,
            self.contents,
            self.subscriptions,
            self.illicit_means,
            self.reasons,
        ]
        return dict(zip(self.file_names(), frames, strict=True))


def read_raw(path: Path = cfg.RAW_SURVEY_PATH) -> pd.DataFrame:
    raw = pd.read_excel(path)
    if not raw["ID"].is_unique:
        raise ValueError("La colonne ID du fichier brut contient des doublons.")
    return raw


def _decode(series: pd.Series, labels: dict[int, str]) -> pd.Series:
    codes = pd.to_numeric(series, errors="coerce").astype("Int64")
    return codes.map(labels).astype("string")


def _selected(raw: pd.DataFrame, column: str, code: int) -> pd.Series:
    """Questions à choix multiples : la colonne vaut le code s'il est coché."""
    if column not in raw:
        return pd.Series(False, index=raw.index)
    return pd.to_numeric(raw[column], errors="coerce").eq(code)


def _clean_amount(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    return values.mask(values.isin(cfg.SPENDING_SENTINELS) | (values < 0))


# --- Tables longues -----------------------------------------------------------


def build_contents(raw: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par répondant et par contenu consommé."""
    frames = []
    for code, label in cfg.CONTENT_LABELS.items():
        consumed = _selected(raw, f"Q1_{code}", code)
        part = pd.DataFrame(
            {
                "id": raw.loc[consumed, "ID"].to_numpy(),
                "contenu": label,
                "frequence_code": pd.to_numeric(raw.loc[consumed, f"Q2_r{code}"]),
                "legalite_code": pd.to_numeric(raw.loc[consumed, f"Q5_r{code}"]),
                "paiement_code": pd.to_numeric(raw.loc[consumed, f"QBU1_r{code}"]),
                "frequence_illicite_code": pd.to_numeric(raw.loc[consumed, f"Q6_r{code}"]),
            }
        )
        frames.append(part)
    out = pd.concat(frames, ignore_index=True)
    out["frequence"] = _decode(out["frequence_code"], cfg.FREQUENCY_LABELS)
    out["legalite"] = _decode(out["legalite_code"], cfg.LEGALITY_LABELS)
    out["paiement"] = _decode(out["paiement_code"], cfg.PAYMENT_LABELS)
    out["frequence_illicite"] = _decode(out["frequence_illicite_code"], cfg.FREQUENCY_LABELS)
    out["illicite"] = out["legalite_code"] >= 2
    for col in ["frequence_code", "legalite_code", "paiement_code"]:
        out[col] = out[col].astype("Int64")
    out["frequence_illicite_code"] = out["frequence_illicite_code"].astype("Int64")
    return out


def build_subscriptions(raw: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par répondant et par type d'abonnement (RS12BIS, RS16BIS, RS17A)."""
    frames = []
    for code, label in cfg.SUBSCRIPTION_LABELS.items():
        monthly = _clean_amount(raw.get(f"RS17A_r{code}_c1"))
        yearly = _clean_amount(raw.get(f"RS17A_r{code}_c2"))
        part = pd.DataFrame(
            {
                "id": raw["ID"].to_numpy(),
                "abonnement": label,
                "abonnement_code": code,
                "abonne_foyer": _selected(raw, f"RS12BIS_r{code}_c1", 1).to_numpy(),
                "compte_exterieur": _selected(raw, f"RS12BIS_r{code}_c2", 2).to_numpy(),
                "budget_mensuel": monthly.fillna(yearly / 12).to_numpy(),
            }
        )
        for origin_code, column in cfg.SHARED_CODE_ORIGIN_COLUMNS.items():
            part[column] = _selected(raw, f"RS16BIS_r{code}_c{origin_code}", origin_code).to_numpy()
        frames.append(part)
    out = pd.concat(frames, ignore_index=True)
    # Statut exclusif pour les graphiques : être abonné dans son foyer prime
    # sur le fait d'utiliser aussi un compte extérieur du même type.
    out["statut"] = np.select(
        [out["abonne_foyer"], out["compte_exterieur"]],
        [cfg.SUBSCRIPTION_STATUS_LABELS[1], cfg.SUBSCRIPTION_STATUS_LABELS[2]],
        default=cfg.SUBSCRIPTION_STATUS_LABELS[3],
    )
    return out


def build_illicit_means(raw: pd.DataFrame) -> pd.DataFrame:
    """Moyens illicites cités pour les films et les séries (QBU10b, QBU10c)."""
    frames = []
    for question, content_code in cfg.ILLICIT_MEANS_QUESTIONS.items():
        asked = raw[[c for c in raw.columns if c.startswith(f"{question}_")]]
        asked_mask = asked.notna().any(axis=1)
        for code, label in cfg.ILLICIT_MEANS_LABELS.items():
            chosen = _selected(raw, f"{question}_{code}", code) & asked_mask
            frames.append(
                pd.DataFrame(
                    {
                        "id": raw.loc[asked_mask, "ID"].to_numpy(),
                        "contenu": cfg.CONTENT_LABELS[content_code],
                        "moyen": label,
                        "cite": chosen[asked_mask].to_numpy(),
                    }
                )
            )
    return pd.concat(frames, ignore_index=True)


def build_reasons(raw: pd.DataFrame) -> pd.DataFrame:
    """Raisons de ne pas consommer légalement (QBU6), une ligne par raison."""
    asked = raw[[c for c in raw.columns if c.startswith("QBU6_")]].notna().any(axis=1)
    frames = [
        pd.DataFrame(
            {
                "id": raw.loc[asked, "ID"].to_numpy(),
                "raison": label,
                "citee": _selected(raw, f"QBU6_{code}", code)[asked].to_numpy(),
            }
        )
        for code, label in cfg.ILLICIT_REASON_LABELS.items()
    ]
    return pd.concat(frames, ignore_index=True)


# --- Table des répondants ------------------------------------------------------


def build_respondents(
    raw: pd.DataFrame, contents: pd.DataFrame, subscriptions: pd.DataFrame
) -> pd.DataFrame:
    out = pd.DataFrame({"id": raw["ID"].astype("string")})
    out["sous_echantillon"] = _decode(raw["CELLULE"], cfg.SUBSAMPLE_LABELS)
    out["sexe"] = _decode(raw["SEXE"], cfg.SEX_LABELS)
    out["age"] = pd.to_numeric(raw["AGE"]).astype("Int64")
    out["tranche_age"] = _decode(raw["RAGE2"], cfg.AGE_GROUP_LABELS)
    out["region"] = _decode(raw["REG13"], cfg.REGION_LABELS)
    out["agglomeration"] = _decode(raw["AGGLO"], cfg.AGGLOMERATION_LABELS)
    out["situation"] = _decode(raw["SITI"], cfg.SITUATION_LABELS)
    out["csp"] = _decode(raw["RECPPIA"], cfg.CSP_LABELS)
    out["statut_foyer"] = _decode(raw["STATUT"], cfg.HOUSEHOLD_STATUS_LABELS)
    out["taille_foyer"] = pd.to_numeric(raw["FOYER"]).astype("Int64")
    out["enfants"] = _decode(raw["ENF"], cfg.CHILDREN_LABELS)
    out["frequence_internet"] = _decode(raw["RS6"], cfg.INTERNET_FREQUENCY_LABELS)

    out["consommateur"] = ~_selected(raw, f"Q1_{cfg.CONTENT_NONE_CODE}", 11)

    per_person = contents.groupby("id").agg(
        n_contenus=("contenu", "size"),
        n_contenus_quotidiens=("frequence_code", lambda s: int((s == 1).sum())),
        illicite=("illicite", "any"),
        illicite_marque=("legalite_code", lambda s: bool((s >= 3).any())),
    )
    out = out.merge(per_person, left_on="id", right_index=True, how="left")
    out["n_contenus"] = out["n_contenus"].fillna(0).astype(int)
    out["n_contenus_quotidiens"] = out["n_contenus_quotidiens"].fillna(0).astype(int)
    out["illicite"] = out["illicite"].astype("boolean").fillna(False).astype(bool)
    out["illicite_marque"] = out["illicite_marque"].astype("boolean").fillna(False).astype(bool)
    out["evolution_legal"] = _decode(raw["Q7"], cfg.EVOLUTION_LABELS)
    out["anciennete_illicite"] = _decode(raw["QBU8"], cfg.ILLICIT_SENIORITY_LABELS)

    # Dépense mensuelle (QBU2) : posée aux consommateurs du sous-échantillon B.
    out["depense_mensuelle"] = _clean_amount(raw["QBU2"]).to_numpy()
    out["payeur"] = (
        out["depense_mensuelle"].gt(0).astype("boolean").mask(out["depense_mensuelle"].isna())
    )

    subs = subscriptions.assign(
        payant=subscriptions["abonne_foyer"]
        & subscriptions["abonnement_code"].isin(cfg.PAID_SUBSCRIPTION_CODES)
    )
    per_sub = subs.groupby("id").agg(
        n_abonnements=("payant", "sum"),
        abonne_tous_types=("abonne_foyer", "any"),
        compte_exterieur=("compte_exterieur", "any"),
        budget_abonnements=("budget_mensuel", lambda s: s.sum(min_count=1)),
    )
    out = out.merge(per_sub, left_on="id", right_index=True, how="left")
    out["n_abonnements"] = out["n_abonnements"].astype(int)
    out["abonne_payant"] = out["n_abonnements"] > 0
    svod = subscriptions[subscriptions["abonnement_code"] == 2].set_index("id")
    out["abonne_svod"] = out["id"].map(svod["abonne_foyer"]).astype(bool)
    out["compte_exterieur_svod"] = out["id"].map(svod["compte_exterieur"]).astype(bool)
    out["offre_pub_acceptee"] = pd.to_numeric(raw["RS15BIS"]).eq(1).to_numpy()

    out["vpn"] = _decode(raw["RS7BIS"], cfg.VPN_LABELS)
    out["vpn_12_mois"] = pd.to_numeric(raw["RS7BIS"]).isin([1, 2]).to_numpy()
    out["dns"] = _decode(raw["RS8"], cfg.DNS_LABELS)
    out["dns_alternatif"] = pd.to_numeric(raw["RS8"]).isin([1, 2]).to_numpy()
    cracked_asked = raw[[f"QBU11C_{k}" for k in range(1, 6)]].notna().any(axis=1)
    cracked = pd.concat([_selected(raw, f"QBU11C_{k}", k) for k in (1, 2, 3)], axis=1).any(axis=1)
    out["appli_crackee"] = cracked.astype("boolean").mask(~cracked_asked).to_numpy(dtype=object)
    out["appli_crackee"] = out["appli_crackee"].astype("boolean")

    out = out.merge(
        intensity_score(contents).rename("score_intensite"),
        left_on="id",
        right_index=True,
        how="left",
    )
    out["score_intensite"] = out["score_intensite"].astype(float).fillna(0.0)
    out["segment"] = assign_segments(out)
    return out.reset_index(drop=True)


def build_tables(raw: pd.DataFrame) -> Tables:
    contents = build_contents(raw)
    subscriptions = build_subscriptions(raw)
    return Tables(
        respondents=build_respondents(raw, contents, subscriptions),
        contents=contents,
        subscriptions=subscriptions,
        illicit_means=build_illicit_means(raw),
        reasons=build_reasons(raw),
    )


def write_tables(tables: Tables, directory: Path = cfg.PROCESSED_DIR) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    written = []
    for name, frame in tables.as_dict().items():
        path = directory / name
        frame.to_parquet(path, index=False)
        written.append(path)
    return written


def load_tables(directory: Path = cfg.PROCESSED_DIR) -> Tables:
    fields = Tables.__dataclass_fields__.keys()
    frames = {
        field: pd.read_parquet(directory / name)
        for field, name in zip(fields, Tables.file_names(), strict=True)
    }
    return Tables(**frames)
