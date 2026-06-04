"""Beneficiary risk feature engineering."""

from __future__ import annotations

import pandas as pd

RISK_BAND_ENCODING = {"low": 1, "medium": 2, "high": 3}


def add_beneficiary_features(
    transactions: pd.DataFrame,
    beneficiaries: pd.DataFrame,
    high_risk_countries: set[str],
    new_beneficiary_days: int,
) -> pd.DataFrame:
    """Join beneficiary context and aggregate features."""
    beneficiary_context = beneficiaries.rename(
        columns={
            "risk_band": "beneficiary_risk_band",
            "first_seen_date": "beneficiary_first_seen_date",
        }
    )
    features = transactions.merge(beneficiary_context, on="beneficiary_id", how="left")
    transaction_dates = pd.to_datetime(features["transaction_timestamp"])
    first_seen_dates = pd.to_datetime(features["beneficiary_first_seen_date"])

    features["beneficiary_risk_band_encoded"] = (
        features["beneficiary_risk_band"].map(RISK_BAND_ENCODING).fillna(0)
    )
    features["is_new_beneficiary"] = (
        (transaction_dates - first_seen_dates).dt.days.between(0, new_beneficiary_days)
    ).astype(int)
    features["beneficiary_country_risk_flag"] = (
        features["beneficiary_country"].isin(high_risk_countries)
    ).astype(int)

    beneficiary_metrics = transactions.groupby("beneficiary_id").agg(
        beneficiary_transaction_count=("transaction_id", "count"),
        beneficiary_total_amount=("amount", "sum"),
    )
    features = features.merge(beneficiary_metrics, on="beneficiary_id", how="left")

    return features
