"""Deterministic AML risk scoring."""

from __future__ import annotations

import pandas as pd

from financial_crime_ml.scoring.aml_risk_model import AMLRiskConfig


def band_from_score(score: int, severity_bands: dict[str, dict[str, int]]) -> str:
    """Map a numeric score to a configured risk band."""
    for band_name in ["Critical", "High", "Medium", "Low", "Info"]:
        band = severity_bands.get(band_name, {})
        if int(band.get("min", 0)) <= score <= int(band.get("max", 100)):
            return band_name
    return "Info"


def _score_row(row: pd.Series, config: AMLRiskConfig) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    reason_labels = {
        "high_risk_jurisdiction_flag": "High-risk jurisdiction exposure",
        "structuring_pattern_flag": "Structuring pattern indicator",
        "rapid_movement_flag": "Rapid movement of funds",
        "mule_activity_indicator": "Mule-account style activity",
        "account_takeover_indicator": "Account takeover style activity",
        "new_beneficiary_high_value_flag": "New beneficiary high-value payment",
        "round_amount_repetition_flag": "Repeated round-amount activity",
        "is_high_value_transaction": "High-value transaction",
        "is_cross_border_transaction": "Cross-border transaction",
        "high_velocity_flag": "High transaction velocity",
    }

    for column, label in reason_labels.items():
        if int(row.get(column, 0)) == 1:
            score += int(config.scoring_weights.get(column, 0))
            reasons.append(label)

    if bool(row.get("is_suspicious", False)):
        score += int(config.scoring_weights.get("synthetic_suspicious_context", 0))
        reasons.append("Synthetic suspicious helper label present")

    return min(score, 100), reasons


def score_aml_risk(feature_table: pd.DataFrame, config: AMLRiskConfig) -> pd.DataFrame:
    """Create AML risk scores and reason codes."""
    rows: list[dict[str, object]] = []
    for _, row in feature_table.iterrows():
        score, reasons = _score_row(row, config)
        output = {
            "transaction_id": row["transaction_id"],
            "account_id": row["account_id"],
            "aml_risk_score": score,
            "aml_risk_band": band_from_score(score, config.severity_bands),
            "aml_risk_reasons": "; ".join(reasons) if reasons else "No material AML indicators",
        }
        if "customer_id" in row:
            output["customer_id"] = row["customer_id"]
        rows.append(output)

    risk_scores = pd.DataFrame(rows)
    ordered_columns = [
        column
        for column in [
            "transaction_id",
            "account_id",
            "customer_id",
            "aml_risk_score",
            "aml_risk_band",
            "aml_risk_reasons",
        ]
        if column in risk_scores.columns
    ]
    return risk_scores[ordered_columns]
