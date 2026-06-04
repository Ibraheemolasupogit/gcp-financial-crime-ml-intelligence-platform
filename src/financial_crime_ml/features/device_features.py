"""Device risk feature engineering."""

from __future__ import annotations

import pandas as pd

RISK_BAND_ENCODING = {"low": 1, "medium": 2, "high": 3}


def add_device_features(transactions: pd.DataFrame, devices: pd.DataFrame) -> pd.DataFrame:
    """Join device context and simple shared-device indicators."""
    device_context = devices.rename(columns={"first_seen_date": "device_first_seen_date"})
    features = transactions.merge(device_context, on="device_id", how="left")
    features["device_risk_band_encoded"] = (
        features["device_risk_band"].map(RISK_BAND_ENCODING).fillna(0)
    )
    features["device_country_mismatch_flag"] = (
        features["ip_country"] != features["origin_country"]
    ).astype(int)

    device_metrics = transactions.groupby("device_id").agg(
        device_transaction_count=("transaction_id", "count"),
        account_count_by_device=("account_id", "nunique"),
    )
    features = features.merge(device_metrics, on="device_id", how="left")
    features["shared_device_flag"] = features["account_count_by_device"].gt(1).astype(int)

    return features.drop(columns=["account_count_by_device"])
