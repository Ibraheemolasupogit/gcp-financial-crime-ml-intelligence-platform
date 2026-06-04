"""Transaction-level and velocity feature engineering."""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_transaction_features(
    transactions: pd.DataFrame,
    high_value_threshold: float,
    round_amount_multiple: int,
    high_risk_countries: set[str],
) -> pd.DataFrame:
    """Add deterministic transaction-level features."""
    features = transactions.copy()
    timestamps = pd.to_datetime(features["transaction_timestamp"])
    amounts = pd.to_numeric(features["amount"], errors="coerce")

    features["transaction_amount_log"] = np.log1p(amounts)
    features["is_round_amount"] = (amounts % round_amount_multiple).eq(0).astype(int)
    features["is_high_value_transaction"] = (amounts >= high_value_threshold).astype(int)
    features["is_cross_border_transaction"] = (
        features["origin_country"] != features["destination_country"]
    ).astype(int)
    features["is_high_risk_destination"] = (
        features["destination_country"].isin(high_risk_countries)
    ).astype(int)
    features["is_unusual_channel"] = features["channel"].isin({"api", "branch"}).astype(int)
    features["transaction_hour"] = timestamps.dt.hour
    features["transaction_day_of_week"] = timestamps.dt.dayofweek
    features["transaction_month"] = timestamps.dt.month
    features["is_night_transaction"] = (
        features["transaction_hour"].lt(6) | features["transaction_hour"].ge(22)
    ).astype(int)

    account_group = features.groupby("account_id")["amount"]
    account_mean = account_group.transform("mean")
    account_std = account_group.transform("std").replace(0, np.nan)

    features["amount_zscore_by_account"] = ((amounts - account_mean) / account_std).fillna(0)
    features["transaction_count_by_account"] = account_group.transform("count")
    features["average_amount_by_account"] = account_mean
    features["amount_vs_account_average_ratio"] = (
        amounts / account_mean.replace(0, np.nan)
    ).fillna(0)

    return features


def add_velocity_features(
    transactions: pd.DataFrame,
    high_velocity_1h_threshold: int,
    high_velocity_24h_threshold: int,
    rapid_movement_hours: int,
) -> pd.DataFrame:
    """Add simple pandas-based account velocity features."""
    features = transactions.copy()
    features["_original_index"] = features.index
    features["transaction_timestamp"] = pd.to_datetime(features["transaction_timestamp"])
    features = features.sort_values(["account_id", "transaction_timestamp"])

    enriched_groups: list[pd.DataFrame] = []
    for _, group in features.groupby("account_id", sort=False):
        rolling_group = group.set_index("transaction_timestamp").sort_index()
        rolling_group["transactions_last_1h"] = rolling_group["amount"].rolling("1h").count()
        rolling_group["transactions_last_24h"] = rolling_group["amount"].rolling("24h").count()
        rolling_group["transaction_amount_last_24h"] = rolling_group["amount"].rolling("24h").sum()
        previous_timestamp = rolling_group.index.to_series().shift(1)
        rolling_group["hours_since_previous_transaction"] = (
            (rolling_group.index.to_series() - previous_timestamp).dt.total_seconds() / 3600
        )
        enriched_groups.append(rolling_group.reset_index())

    features = pd.concat(enriched_groups, ignore_index=True)
    features["high_velocity_flag"] = (
        (features["transactions_last_1h"] >= high_velocity_1h_threshold)
        | (features["transactions_last_24h"] >= high_velocity_24h_threshold)
    ).astype(int)
    features["rapid_sequence_flag"] = (
        features["hours_since_previous_transaction"].le(rapid_movement_hours)
    ).astype(int)
    features["hours_since_previous_transaction"] = features[
        "hours_since_previous_transaction"
    ].fillna(-1)

    return (
        features.sort_values("_original_index")
        .drop(columns=["_original_index"])
        .reset_index(drop=True)
    )
