"""Milestone 5 fraud model and AML scoring workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from financial_crime_ml.governance import generate_model_card
from financial_crime_ml.models.fraud_classifier import (
    FraudModelConfig,
    load_fraud_model_config,
    train_fraud_classifier,
)
from financial_crime_ml.models.model_utils import load_feature_table
from financial_crime_ml.scoring import load_aml_risk_config, prioritise_alerts, score_aml_risk
from financial_crime_ml.scoring.aml_risk_model import AMLRiskConfig


def run_fraud_model_workflow(
    model_config: FraudModelConfig | None = None,
    risk_config: AMLRiskConfig | None = None,
) -> dict[str, Any]:
    """Train fraud classifier, score AML risk, prioritise alerts, and write governance output."""
    resolved_model_config = model_config or load_fraud_model_config()
    resolved_risk_config = risk_config or load_aml_risk_config()
    feature_table = load_feature_table(resolved_model_config.input_path)

    fraud_predictions, metrics, feature_columns = train_fraud_classifier(resolved_model_config)
    aml_risk_scores = score_aml_risk(feature_table, resolved_risk_config)
    resolved_risk_config.output_path.parent.mkdir(parents=True, exist_ok=True)
    aml_risk_scores.to_csv(resolved_risk_config.output_path, index=False)

    prioritised_alerts = prioritise_alerts(fraud_predictions, aml_risk_scores, feature_table)
    resolved_risk_config.prioritised_alerts_output_path.parent.mkdir(parents=True, exist_ok=True)
    prioritised_alerts.to_csv(resolved_risk_config.prioritised_alerts_output_path, index=False)

    model_card_path = generate_model_card(
        metrics,
        feature_columns,
        resolved_model_config.model_card_output_path,
    )

    return {
        "metrics": metrics,
        "fraud_predictions_path": resolved_model_config.predictions_output_path,
        "model_metrics_path": resolved_model_config.metrics_output_path,
        "aml_risk_scores_path": resolved_risk_config.output_path,
        "prioritised_alerts_path": resolved_risk_config.prioritised_alerts_output_path,
        "model_card_path": Path(model_card_path),
        "fraud_prediction_count": len(fraud_predictions),
        "aml_score_count": len(aml_risk_scores),
        "prioritised_alert_count": len(prioritised_alerts),
    }
