from __future__ import annotations

import pandas as pd


def compute_overview_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            'respondents': 0,
            'median_spending': 0.0,
            'mean_spending': 0.0,
            'p75_spending': 0.0,
            'p90_spending': 0.0,
            'pct_paying': 0.0,
            'pct_high_value': 0.0,
            'pct_risky': 0.0,
            'pct_under_monetized_engaged': 0.0,
            'avg_raw_content_depth': 0.0,
            'avg_engagement': 0.0,
            'avg_monetization': 0.0,
            'hybrid_rate': 0.0,
            'legal_paid_rate': 0.0,
        }

    return {
        'respondents': int(len(df)),
        'median_spending': float(df['monthly_spending'].median()),
        'mean_spending': float(df['monthly_spending'].mean()),
        'p75_spending': float(df['monthly_spending'].quantile(0.75)),
        'p90_spending': float(df['monthly_spending'].quantile(0.90)),
        'pct_paying': float(df['paying_user'].mean()),
        'pct_high_value': float(df['high_value_user'].mean()),
        'pct_risky': float(df['risky_behavior_user'].mean()),
        'pct_under_monetized_engaged': float(df['under_monetized_engaged_user'].mean()),
        'avg_raw_content_depth': float(df['raw_content_category_count'].mean()),
        'avg_engagement': float(df['engagement_score'].mean()),
        'avg_monetization': float(df['monetization_score'].mean()),
        'hybrid_rate': float(df['access_style'].astype(str).eq('Hybrid').mean()),
        'legal_paid_rate': float(df['access_style'].astype(str).eq('Legal Paid').mean()),
    }


def segment_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            columns=[
                'consumer_segment',
                'respondents',
                'median_spending',
                'avg_engagement',
                'avg_risk',
                'avg_raw_depth',
                'paying_rate',
                'under_monetized_rate',
            ]
        )
    summary = (
        df.groupby('consumer_segment', dropna=False)
        .agg(
            respondents=('consumer_segment', 'size'),
            median_spending=('monthly_spending', 'median'),
            avg_engagement=('engagement_score', 'mean'),
            avg_risk=('risk_behavior_score', 'mean'),
            avg_raw_depth=('raw_content_category_count', 'mean'),
            paying_rate=('paying_user', 'mean'),
            under_monetized_rate=('under_monetized_engaged_user', 'mean'),
        )
        .reset_index()
        .sort_values(['respondents', 'median_spending'], ascending=[False, False])
    )
    return summary


def missingness_report(df: pd.DataFrame) -> pd.DataFrame:
    report = (
        df.isna().mean().rename('missing_rate').reset_index().rename(columns={'index': 'column'}).sort_values('missing_rate', ascending=False)
    )
    report['non_missing_rate'] = 1 - report['missing_rate']
    return report


def spending_distribution_by_group(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[group_col, 'respondents', 'median_spending', 'mean_spending', 'payer_rate'])
    return (
        df.groupby(group_col, dropna=False)
        .agg(
            respondents=(group_col, 'size'),
            median_spending=('monthly_spending', 'median'),
            mean_spending=('monthly_spending', 'mean'),
            payer_rate=('paying_user', 'mean'),
        )
        .reset_index()
        .sort_values('median_spending', ascending=False)
    )


def risk_profile_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=['consumer_segment', 'vpn_score', 'dns_score', 'download_risk_score', 'cracked_apps_score'])
    return (
        df.groupby('consumer_segment', dropna=False)
        .agg(
            vpn_score=('vpn_score', 'mean'),
            dns_score=('dns_score', 'mean'),
            download_risk_score=('download_risk_score', 'mean'),
            cracked_apps_score=('cracked_apps_score', 'mean'),
        )
        .reset_index()
    )


def engagement_vs_spending_quintiles(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=['spending_quintile', 'avg_engagement', 'avg_risk', 'respondents'])
    working = df[['monthly_spending', 'engagement_score', 'risk_behavior_score']].copy()
    working['spending_quintile'] = pd.qcut(working['monthly_spending'].rank(method='first'), 5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
    return (
        working.groupby('spending_quintile', dropna=False, observed=False)
        .agg(avg_engagement=('engagement_score', 'mean'), avg_risk=('risk_behavior_score', 'mean'), respondents=('spending_quintile', 'size'))
        .reset_index()
    )


def access_mix_summary(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[group_col, 'access_style', 'share'])
    ctab = pd.crosstab(df[group_col].astype(str), df['access_style'].astype(str), normalize='index')
    return ctab.reset_index().melt(id_vars=group_col, var_name='access_style', value_name='share')


def percentile_table(df: pd.DataFrame, group_col: str, metric_col: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[group_col, 'p25', 'p50', 'p75', 'p90'])
    rows = []
    for key, grp in df.groupby(group_col, dropna=False):
        rows.append(
            {
                group_col: key,
                'p25': float(grp[metric_col].quantile(0.25)),
                'p50': float(grp[metric_col].quantile(0.50)),
                'p75': float(grp[metric_col].quantile(0.75)),
                'p90': float(grp[metric_col].quantile(0.90)),
            }
        )
    return pd.DataFrame(rows).sort_values('p50', ascending=False)
