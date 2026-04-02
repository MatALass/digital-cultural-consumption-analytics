from __future__ import annotations

import re

import numpy as np
import pandas as pd

from dashboard.config import (
    AGE_GROUP_BINS,
    AGE_GROUP_LABELS,
    CULTURAL_FREQUENCY_SCORE,
    DNS_SCORE,
    DOWNLOAD_RISK_SCORE,
    INTERNET_FREQUENCY_SCORE,
    LEGALITY_SCORE,
    PAID_ACCESS_SCORE,
    PAYMENT_SCORE,
    RAW_MODULE_PATTERNS,
    VPN_SCORE,
)


def _parse_numeric_children(value: object) -> int:
    if pd.isna(value):
        return 0
    text = str(value).strip()
    if text == "Aucun":
        return 0
    if text == "4 et plus":
        return 4
    try:
        return int(text)
    except ValueError:
        return 0


def _parse_household_size(value: object) -> int:
    if pd.isna(value):
        return 0
    text = str(value).strip()
    if text == "9 personnes et plus":
        return 9
    digits = "".join(ch for ch in text if ch.isdigit())
    return int(digits) if digits else 0


def _normalize_sex(value: object) -> str:
    return {"H": "Male", "F": "Female"}.get(str(value).strip(), str(value))


def _generation_from_age(age: float) -> str:
    if pd.isna(age):
        return "Unknown"
    if age <= 28:
        return "Gen Z"
    if age <= 44:
        return "Millennial"
    if age <= 60:
        return "Gen X"
    return "Boomer+"


def _urbanity_bucket(value: object) -> str:
    text = str(value)
    if "Rural" in text:
        return "Rural"
    if "Paris" in text or "métropoles" in text:
        return "Metro"
    if "ville" in text.lower():
        return "Urban"
    return "Other"


def _family_stage(row: pd.Series) -> str:
    if row["has_children"]:
        return "Family with children"
    if str(row["household_status"]) == "couple":
        return "Couple without children"
    return "Single / other"


def _access_style(row: pd.Series) -> str:
    legality = str(row["legality_type"])
    payment = str(row["payment_type"])
    if legality == "Légale" and payment in {"payante", "souvent payante"}:
        return "Legal Paid"
    if legality == "Légale" and payment in {"gratuit", "souvent gratuit"}:
        return "Legal Free"
    if legality in {"Autant", "Souvent légale"}:
        return "Hybrid"
    if legality in {"Souvent illégale", "Illégale"}:
        return "Risk Heavy"
    return "Unspecified"


def _value_tier(spending: float, q50: float, q75: float, q90: float) -> str:
    if spending <= 0:
        return "Non-spender"
    if spending <= q50:
        return "Low spender"
    if spending <= q75:
        return "Mid spender"
    if spending <= q90:
        return "High spender"
    return "Top spender"


def _consumer_segment(row: pd.Series) -> str:
    if (
        row["high_value_user"]
        and row["access_style"] == "Legal Paid"
        and row["risk_behavior_score"] <= 1
    ):
        return "Premium Legal Users"
    if row["high_value_user"] and row["raw_illicit_channel_count"] >= 1:
        return "Hybrid Monetizers"
    if (
        row["monthly_spending"] <= 0
        and row["engagement_score"] >= 0.65
        and row["raw_content_category_count"] >= 3
    ):
        return "Heavy Free Users"
    if row["risk_behavior_score"] >= 4 and row["raw_illicit_method_count"] >= 2:
        return "Risk-Oriented Free Users"
    if row["monthly_spending"] > 0 and row["engagement_score"] < 0.65:
        return "Casual Value Seekers"
    return "Low Engagement Users"


def _profile_label(row: pd.Series) -> str:
    children = "with children" if row["has_children"] else "without children"
    return f"{row['generation']} | {row['payment_bucket']} | {children}"


def _select_columns(raw_df: pd.DataFrame, pattern: str) -> list[str]:
    regex = re.compile(pattern)
    return [col for col in raw_df.columns if regex.match(str(col))]


def _rowwise_selected_count(df: pd.DataFrame) -> pd.Series:
    if df.shape[1] == 0:
        return pd.Series(0, index=df.index)
    numeric = df.apply(pd.to_numeric, errors="coerce")
    return (numeric.fillna(0) > 0).sum(axis=1)


def _rowwise_non_null_count(df: pd.DataFrame) -> pd.Series:
    if df.shape[1] == 0:
        return pd.Series(0, index=df.index)
    return df.notna().sum(axis=1)


def _rowwise_numeric_mean(df: pd.DataFrame) -> pd.Series:
    if df.shape[1] == 0:
        return pd.Series(0.0, index=df.index)
    return df.apply(pd.to_numeric, errors="coerce").mean(axis=1).fillna(0.0)


def _build_raw_feature_layer(raw_df: pd.DataFrame, target_len: int) -> pd.DataFrame:
    raw = raw_df.reset_index(drop=True).iloc[:target_len].copy()

    module_cols = {
        name: _select_columns(raw, pattern)
        for name, pattern in RAW_MODULE_PATTERNS.items()
    }
    selected = [col for cols in module_cols.values() for col in cols]
    module_df = raw[selected].copy() if selected else pd.DataFrame(index=raw.index)

    out = pd.DataFrame(index=raw.index)
    out["raw_content_paid_score"] = _rowwise_numeric_mean(
        raw[module_cols["qbu1_paid_matrix"]]
    )
    out["raw_content_category_count"] = _rowwise_non_null_count(
        raw[module_cols["qbu1_paid_matrix"]]
    )
    out["raw_device_diversity"] = _rowwise_selected_count(
        raw[module_cols["qbu5a_devices"]]
    )

    illegal_cols = (
        module_cols["qbu10a_illegal_means"]
        + module_cols["qbu10b_illegal_means"]
        + module_cols["qbu10c_illegal_means"]
        + module_cols["qbu10d_illegal_means"]
    )
    out["raw_illicit_channel_count"] = _rowwise_selected_count(raw[illegal_cols])
    out["raw_illicit_frequency_mean"] = _rowwise_numeric_mean(
        raw[module_cols["qbu11_illegal_frequency"]]
    )
    out["raw_illicit_method_count"] = _rowwise_selected_count(
        raw[module_cols["qbu11b_illicit_methods"]]
    )
    out["raw_stream_ripping_score"] = _rowwise_numeric_mean(
        raw[module_cols["qbu12_stream_ripping"]]
    )
    out["raw_legal_offer_advantage_count"] = _rowwise_selected_count(
        raw[module_cols["qbol3_legal_advantages"]]
    )
    out["raw_legal_motivation_count"] = _rowwise_selected_count(
        raw[module_cols["qbol4_legal_motivations"]]
    )
    out["raw_behavioral_coverage_rate"] = (
        module_df.notna().mean(axis=1) if not module_df.empty else 0.0
    )
    return out.reset_index(drop=True)


def build_analytics_dataset(
    processed_df: pd.DataFrame, raw_df: pd.DataFrame
) -> pd.DataFrame:
    out = processed_df.copy().reset_index(drop=True)

    # Conservative alignment: keep only the shared row span and avoid pretending to have a perfect keyed join.
    target_len = min(len(out), len(raw_df))
    out = out.iloc[:target_len].copy()

    out["age"] = pd.to_numeric(out["age"], errors="coerce")
    out["monthly_spending"] = pd.to_numeric(
        out["monthly_spending"], errors="coerce"
    ).fillna(0)
    out["sex"] = out["sex"].map(_normalize_sex)

    out["age_group"] = pd.cut(
        out["age"],
        bins=AGE_GROUP_BINS,
        labels=AGE_GROUP_LABELS,
        include_lowest=True,
        right=True,
    ).astype(str)
    out["generation"] = out["age"].apply(_generation_from_age)
    out["children_count_numeric"] = out["children_count"].apply(_parse_numeric_children)
    out["household_size_numeric"] = out["household_size"].apply(_parse_household_size)
    out["has_children"] = out["children_count_numeric"] > 0
    out["family_stage"] = out.apply(_family_stage, axis=1)
    out["urbanity_bucket"] = out["agglomeration_type"].apply(_urbanity_bucket)

    out["internet_intensity_score"] = (
        out["internet_frequency"].map(INTERNET_FREQUENCY_SCORE).fillna(0)
    )
    out["cultural_frequency_score"] = (
        out["cultural_frequency"].map(CULTURAL_FREQUENCY_SCORE).fillna(0)
    )
    out["legality_score"] = out["legality_type"].map(LEGALITY_SCORE).fillna(0)
    out["payment_orientation_score"] = out["payment_type"].map(PAYMENT_SCORE).fillna(0)
    out["paid_access_score"] = (
        out["paid_services_access"].map(PAID_ACCESS_SCORE).fillna(0)
    )
    out["vpn_score"] = out["vpn_usage"].map(VPN_SCORE).fillna(0)
    out["dns_score"] = out["dns_settings_usage"].map(DNS_SCORE).fillna(0)
    out["download_risk_score"] = (
        out["streaming_download_type"].map(DOWNLOAD_RISK_SCORE).fillna(0)
    )
    out["cracked_apps_score"] = (
        out["cracked_apps_usage"].map({"Non": 0, "Oui": 3}).fillna(0)
    )

    behavior_cols = [
        "internet_frequency",
        "cultural_frequency",
        "legality_type",
        "payment_type",
        "monthly_spending",
        "vpn_usage",
        "cracked_apps_usage",
        "streaming_download_type",
        "dns_settings_usage",
        "paid_services_access",
    ]
    out["module_completion_rate"] = out[behavior_cols].notna().mean(axis=1)
    out["response_depth_score"] = out[behavior_cols].notna().sum(axis=1)

    out["engagement_score"] = (
        0.45 * (out["internet_intensity_score"] / 7.0)
        + 0.35 * (out["cultural_frequency_score"] / 4.0)
        + 0.20 * (out["monthly_spending"] > 0).astype(int)
    )
    out["risk_behavior_score"] = (
        out["vpn_score"]
        + out["dns_score"]
        + out["download_risk_score"]
        + out["cracked_apps_score"]
    )
    out["monetization_score"] = (
        0.50 * (out["payment_orientation_score"] / 5.0)
        + 0.20 * (out["paid_access_score"] / 2.0)
        + 0.30 * (out["monthly_spending"] > 0).astype(int)
    )

    raw_features = _build_raw_feature_layer(raw_df, target_len)
    out = pd.concat([out.reset_index(drop=True), raw_features], axis=1)

    out["content_depth_score"] = (
        0.45
        * (
            out["raw_content_category_count"]
            / max(float(out["raw_content_category_count"].max()), 1.0)
        )
        + 0.25
        * (
            out["raw_device_diversity"]
            / max(float(out["raw_device_diversity"].max()), 1.0)
        )
        + 0.30 * out["raw_behavioral_coverage_rate"]
    )
    out["raw_risk_intensity_score"] = (
        out["raw_illicit_channel_count"]
        + out["raw_illicit_method_count"]
        + out["raw_stream_ripping_score"]
    )
    out["legal_value_perception_score"] = (
        out["raw_legal_offer_advantage_count"] + out["raw_legal_motivation_count"]
    )

    out["paying_user"] = out["monthly_spending"] > 0
    out["hybrid_access_user"] = (
        out["legality_type"]
        .astype(str)
        .isin(["Autant", "Souvent légale", "Souvent illégale"])
    )
    out["risky_behavior_user"] = (out["risk_behavior_score"] >= 4) | (
        out["raw_risk_intensity_score"] >= 3
    )

    out["payment_bucket"] = np.select(
        [
            out["payment_orientation_score"] <= 2,
            out["payment_orientation_score"] == 3,
            out["payment_orientation_score"] >= 4,
        ],
        ["Free-oriented", "Balanced", "Paid-oriented"],
        default="Unknown",
    )
    out["access_style"] = out.apply(_access_style, axis=1)

    q50 = float(out["monthly_spending"].quantile(0.50))
    q75 = float(out["monthly_spending"].quantile(0.75))
    q90 = float(out["monthly_spending"].quantile(0.90))
    out["value_tier"] = out["monthly_spending"].apply(
        lambda x: _value_tier(float(x), q50, q75, q90)
    )

    out["high_value_user"] = out["monthly_spending"] >= q75
    out["under_monetized_engaged_user"] = (
        (out["engagement_score"] >= 0.65)
        & (out["monthly_spending"] <= 0)
        & (out["raw_content_category_count"] >= 2)
    )

    out["consumer_segment"] = out.apply(_consumer_segment, axis=1)
    out["consumer_profile"] = out.apply(_profile_label, axis=1)
    return out
