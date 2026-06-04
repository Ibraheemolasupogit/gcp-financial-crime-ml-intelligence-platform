"""Combine fraud predictions and AML scores into prioritised alert outputs."""

from __future__ import annotations

import pandas as pd


def priority_band_from_score(score: float) -> str:
    """Map priority score to an alert priority band."""
    if score >= 90:
        return "Critical"
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    if score >= 10:
        return "Low"
    return "Info"


def recommended_action(priority_band: str) -> str:
    """Map priority band to an investigator action."""
    return {
        "Critical": "Immediate investigator review",
        "High": "Investigator review",
        "Medium": "Queue for monitoring",
        "Low": "No immediate action",
        "Info": "No immediate action",
    }[priority_band]


def prioritise_alerts(
    fraud_predictions: pd.DataFrame,
    aml_risk_scores: pd.DataFrame,
    feature_table: pd.DataFrame,
) -> pd.DataFrame:
    """Create prioritised alert rows from model and AML scoring outputs."""
    typology_columns = [
        "structuring_pattern_flag",
        "rapid_movement_flag",
        "high_risk_jurisdiction_flag",
        "mule_activity_indicator",
        "account_takeover_indicator",
        "new_beneficiary_high_value_flag",
        "round_amount_repetition_flag",
    ]
    context_columns = ["transaction_id", *typology_columns]
    merged = fraud_predictions.merge(
        aml_risk_scores,
        on=["transaction_id", "account_id"],
        how="left",
    )
    merged = merged.merge(feature_table[context_columns], on="transaction_id", how="left")
    if "customer_id_x" in merged.columns:
        merged["customer_id"] = merged["customer_id_x"].fillna(merged.get("customer_id_y"))
        merged = merged.drop(
            columns=[col for col in ["customer_id_x", "customer_id_y"] if col in merged]
        )

    merged["priority_score"] = (
        (merged["fraud_probability"] * 100 * 0.45) + (merged["aml_risk_score"] * 0.55)
    ).round(2)
    merged["priority_band"] = merged["priority_score"].map(priority_band_from_score)
    merged["recommended_action"] = merged["priority_band"].map(recommended_action)

    def _priority_reasons(row: pd.Series) -> str:
        reasons = []
        if int(row["fraud_prediction"]) == 1:
            reasons.append("Fraud probability above threshold")
        if row["aml_risk_band"] in {"Critical", "High"}:
            reasons.append(f"AML risk band {row['aml_risk_band']}")
        active_typologies = [
            column.replace("_", " ")
            for column in typology_columns
            if int(row.get(column, 0)) == 1
        ]
        reasons.extend(active_typologies[:3])
        return "; ".join(reasons) if reasons else "No immediate priority indicators"

    merged["priority_reasons"] = merged.apply(_priority_reasons, axis=1)
    output_columns = [
        "transaction_id",
        "account_id",
        "customer_id",
        "fraud_probability",
        "fraud_prediction",
        "aml_risk_score",
        "aml_risk_band",
        "priority_score",
        "priority_band",
        "priority_reasons",
        "recommended_action",
    ]
    return merged[[column for column in output_columns if column in merged.columns]].sort_values(
        "priority_score",
        ascending=False,
    )
