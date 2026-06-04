"""Rule-based AML typology indicators for synthetic datasets."""

from __future__ import annotations

import pandas as pd


def add_aml_typology_features(
    features: pd.DataFrame,
    structuring_amount_threshold: float,
    structuring_count_threshold: int,
) -> pd.DataFrame:
    """Add deterministic rule-based financial crime typology indicators."""
    enriched = features.copy()

    round_counts = (
        enriched.loc[enriched["is_round_amount"].eq(1)]
        .groupby("account_id")["transaction_id"]
        .transform("count")
    )
    enriched["round_amount_count_by_account"] = round_counts.reindex(enriched.index).fillna(0)

    enriched["structuring_pattern_flag"] = (
        (
            enriched["is_round_amount"].eq(1)
            & enriched["amount"].lt(structuring_amount_threshold)
            & enriched["round_amount_count_by_account"].ge(structuring_count_threshold)
        )
        | enriched["suspicious_pattern"].eq("round_number_payments")
    ).astype(int)
    enriched["rapid_movement_flag"] = (
        (enriched["rapid_sequence_flag"].eq(1) & enriched["is_high_value_transaction"].eq(1))
        | enriched["suspicious_pattern"].eq("rapid_movement_of_funds")
    ).astype(int)
    enriched["high_risk_jurisdiction_flag"] = enriched["is_high_risk_destination"].astype(int)
    enriched["mule_activity_indicator"] = (
        (
            enriched["high_velocity_flag"].eq(1)
            & enriched["is_cross_border_transaction"].eq(1)
            & enriched["account_suspicious_transaction_rate"].gt(0)
        )
        | enriched["suspicious_pattern"].eq("mule_account_style_behaviour")
    ).astype(int)
    enriched["account_takeover_indicator"] = (
        enriched["device_country_mismatch_flag"].eq(1)
        | (
            enriched["is_unusual_channel"].eq(1)
            & enriched["is_high_value_transaction"].eq(1)
            & enriched["device_risk_band_encoded"].ge(2)
        )
        | enriched["suspicious_pattern"].eq("account_takeover_style_behaviour")
    ).astype(int)
    enriched["new_beneficiary_high_value_flag"] = (
        (enriched["is_new_beneficiary"].eq(1) & enriched["is_high_value_transaction"].eq(1))
        | enriched["suspicious_pattern"].eq("new_beneficiary_risk")
    ).astype(int)
    enriched["round_amount_repetition_flag"] = (
        enriched["round_amount_count_by_account"].ge(structuring_count_threshold)
        | enriched["suspicious_pattern"].eq("round_number_payments")
    ).astype(int)

    return enriched
