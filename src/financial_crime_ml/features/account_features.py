"""Customer and account behavioural feature engineering."""

from __future__ import annotations

import pandas as pd

RISK_BAND_ENCODING = {"low": 1, "medium": 2, "high": 3}


def add_account_customer_features(
    transactions: pd.DataFrame,
    accounts: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Join account and customer context onto transaction-level features."""
    customer_context = customers.rename(
        columns={
            "country": "customer_country",
            "risk_band": "customer_risk_band",
            "onboarding_date": "customer_onboarding_date",
        }
    )
    account_customer = accounts.merge(customer_context, on="customer_id", how="left")
    features = transactions.merge(
        account_customer,
        on="account_id",
        how="left",
        suffixes=("", "_customer"),
    )

    transaction_dates = pd.to_datetime(features["transaction_timestamp"])
    account_open_dates = pd.to_datetime(features["open_date"])
    customer_onboarding_dates = pd.to_datetime(features["customer_onboarding_date"])

    features["customer_risk_band_encoded"] = (
        features["customer_risk_band"].map(RISK_BAND_ENCODING).fillna(0)
    )
    features["account_age_days"] = (transaction_dates - account_open_dates).dt.days.clip(lower=0)
    features["customer_tenure_days"] = (
        transaction_dates - customer_onboarding_dates
    ).dt.days.clip(lower=0)

    account_metrics = transactions.groupby("account_id").agg(
        account_transaction_count=("transaction_id", "count"),
        account_total_transaction_amount=("amount", "sum"),
        account_average_transaction_amount=("amount", "mean"),
        account_suspicious_transaction_rate=("is_suspicious", "mean"),
    )
    features = features.merge(account_metrics, on="account_id", how="left")

    return features
