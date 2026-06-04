"""High-risk anomaly ranking with optional model/scoring joins."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from financial_crime_ml.ingestion.load_data import REPO_ROOT

BAND_ORDER = {"Critical": 5, "High": 4, "Medium": 3, "Low": 2, "Info": 1}


def _optional_csv(path: str | Path) -> pd.DataFrame | None:
    resolved_path = Path(path)
    if not resolved_path.is_absolute():
        resolved_path = REPO_ROOT / resolved_path
    if not resolved_path.exists():
        return None
    return pd.read_csv(resolved_path)


def rank_high_risk_anomalies(
    anomaly_scores: pd.DataFrame,
    max_rows: int,
    fraud_predictions_path: str | Path = "outputs/sample/fraud_predictions.csv",
    aml_risk_scores_path: str | Path = "outputs/sample/aml_risk_scores.csv",
    prioritised_alerts_path: str | Path = "outputs/sample/prioritised_alerts.csv",
) -> pd.DataFrame:
    """Rank anomalies and enrich them with optional fraud/AML outputs."""
    ranked = anomaly_scores.copy()

    fraud_predictions = _optional_csv(fraud_predictions_path)
    if fraud_predictions is not None:
        fraud_columns = [
            column
            for column in ["transaction_id", "fraud_probability", "fraud_prediction"]
            if column in fraud_predictions.columns
        ]
        ranked = ranked.merge(fraud_predictions[fraud_columns], on="transaction_id", how="left")

    aml_scores = _optional_csv(aml_risk_scores_path)
    if aml_scores is not None:
        aml_columns = [
            column
            for column in ["transaction_id", "aml_risk_score", "aml_risk_band", "aml_risk_reasons"]
            if column in aml_scores.columns
        ]
        ranked = ranked.merge(aml_scores[aml_columns], on="transaction_id", how="left")

    prioritised_alerts = _optional_csv(prioritised_alerts_path)
    if prioritised_alerts is not None:
        priority_columns = [
            column
            for column in [
                "transaction_id",
                "priority_score",
                "priority_band",
                "recommended_action",
            ]
            if column in prioritised_alerts.columns
        ]
        ranked = ranked.merge(prioritised_alerts[priority_columns], on="transaction_id", how="left")

    ranked["anomaly_band_order"] = ranked["anomaly_band"].map(BAND_ORDER).fillna(0)
    if "aml_risk_score" not in ranked.columns:
        ranked["aml_risk_score"] = 0
    if "fraud_probability" not in ranked.columns:
        ranked["fraud_probability"] = 0.0

    ranked = ranked.sort_values(
        ["anomaly_band_order", "anomaly_score", "aml_risk_score", "fraud_probability"],
        ascending=[False, False, False, False],
    ).head(max_rows)

    return ranked.drop(columns=["anomaly_band_order"]).reset_index(drop=True)
