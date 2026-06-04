import json
from pathlib import Path

import pandas as pd

from financial_crime_ml.models.fraud_classifier import FraudModelConfig, train_fraud_classifier
from financial_crime_ml.models.workflow import run_fraud_model_workflow
from financial_crime_ml.scoring.alert_prioritiser import priority_band_from_score
from financial_crime_ml.scoring.aml_risk_model import AMLRiskConfig
from financial_crime_ml.scoring.risk_scorer import score_aml_risk


def _model_config(tmp_path: Path) -> FraudModelConfig:
    return FraudModelConfig(
        random_seed=42,
        test_size=0.2,
        target_column="is_suspicious",
        model_type="logistic_regression",
        prediction_threshold=0.5,
        input_path=Path("data/processed/transaction_features.csv").resolve(),
        metrics_output_path=tmp_path / "model_metrics.json",
        predictions_output_path=tmp_path / "fraud_predictions.csv",
        model_card_output_path=tmp_path / "model_card.md",
        excluded_columns=(
            "transaction_id",
            "account_id",
            "customer_id",
            "beneficiary_id",
            "device_id",
            "suspicious_pattern",
            "transaction_timestamp",
            "currency",
            "transaction_type",
            "merchant_category",
            "origin_country",
            "destination_country",
            "channel",
        ),
    )


def _risk_config(tmp_path: Path) -> AMLRiskConfig:
    return AMLRiskConfig(
        output_path=tmp_path / "aml_risk_scores.csv",
        prioritised_alerts_output_path=tmp_path / "prioritised_alerts.csv",
        severity_bands={
            "Critical": {"min": 90, "max": 100},
            "High": {"min": 70, "max": 89},
            "Medium": {"min": 40, "max": 69},
            "Low": {"min": 10, "max": 39},
            "Info": {"min": 0, "max": 9},
        },
        scoring_weights={
            "high_risk_jurisdiction_flag": 22,
            "structuring_pattern_flag": 18,
            "rapid_movement_flag": 18,
            "mule_activity_indicator": 20,
            "account_takeover_indicator": 24,
            "new_beneficiary_high_value_flag": 16,
            "round_amount_repetition_flag": 12,
            "is_high_value_transaction": 10,
            "is_cross_border_transaction": 8,
            "high_velocity_flag": 12,
            "synthetic_suspicious_context": 5,
        },
        recommended_action_thresholds={
            "immediate_investigator_review": 90,
            "investigator_review": 70,
            "queue_for_monitoring": 40,
        },
    )


def test_fraud_model_training_runs_and_writes_metrics(tmp_path: Path) -> None:
    predictions, metrics, feature_columns = train_fraud_classifier(_model_config(tmp_path))

    assert not predictions.empty
    assert feature_columns
    assert (tmp_path / "model_metrics.json").exists()
    assert (tmp_path / "fraud_predictions.csv").exists()


def test_required_metric_keys_exist(tmp_path: Path) -> None:
    _, metrics, _ = train_fraud_classifier(_model_config(tmp_path))

    required_keys = {
        "model_name",
        "target_column",
        "feature_count",
        "training_row_count",
        "test_row_count",
        "precision",
        "recall",
        "f1_score",
        "roc_auc",
        "confusion_matrix",
        "positive_class_rate",
        "threshold_used",
        "notes",
    }
    assert required_keys.issubset(metrics)


def test_aml_risk_scores_and_bands_are_created(tmp_path: Path) -> None:
    feature_table = pd.read_csv("data/processed/transaction_features.csv")

    scores = score_aml_risk(feature_table, _risk_config(tmp_path))

    assert not scores.empty
    assert set(scores["aml_risk_band"]).issubset({"Critical", "High", "Medium", "Low", "Info"})


def test_prioritised_alerts_and_model_card_are_created(tmp_path: Path) -> None:
    result = run_fraud_model_workflow(_model_config(tmp_path), _risk_config(tmp_path))

    assert result["prioritised_alerts_path"].exists()
    assert result["model_card_path"].exists()
    alerts = pd.read_csv(result["prioritised_alerts_path"])
    assert set(alerts["priority_band"]).issubset({"Critical", "High", "Medium", "Low", "Info"})


def test_workflow_outputs_contain_expected_files(tmp_path: Path) -> None:
    result = run_fraud_model_workflow(_model_config(tmp_path), _risk_config(tmp_path))

    assert result["model_metrics_path"].exists()
    assert result["fraud_predictions_path"].exists()
    assert result["aml_risk_scores_path"].exists()
    assert result["prioritised_alerts_path"].exists()
    metrics = json.loads(result["model_metrics_path"].read_text(encoding="utf-8"))
    assert metrics["model_name"] == "LogisticRegression"


def test_scoring_logic_produces_higher_scores_for_stronger_typology_signals(tmp_path: Path) -> None:
    base_row = {
        "transaction_id": "TXN_LOW",
        "account_id": "ACCT_LOW",
        "customer_id": "CUST_LOW",
        "is_suspicious": False,
        "high_risk_jurisdiction_flag": 0,
        "structuring_pattern_flag": 0,
        "rapid_movement_flag": 0,
        "mule_activity_indicator": 0,
        "account_takeover_indicator": 0,
        "new_beneficiary_high_value_flag": 0,
        "round_amount_repetition_flag": 0,
        "is_high_value_transaction": 0,
        "is_cross_border_transaction": 0,
        "high_velocity_flag": 0,
    }
    strong_row = {
        **base_row,
        "transaction_id": "TXN_HIGH",
        "account_id": "ACCT_HIGH",
        "customer_id": "CUST_HIGH",
        "is_suspicious": True,
        "high_risk_jurisdiction_flag": 1,
        "structuring_pattern_flag": 1,
        "rapid_movement_flag": 1,
        "account_takeover_indicator": 1,
        "is_high_value_transaction": 1,
        "high_velocity_flag": 1,
    }
    scores = score_aml_risk(pd.DataFrame([base_row, strong_row]), _risk_config(tmp_path))

    low_score = scores.loc[scores["transaction_id"].eq("TXN_LOW"), "aml_risk_score"].iloc[0]
    high_score = scores.loc[scores["transaction_id"].eq("TXN_HIGH"), "aml_risk_score"].iloc[0]
    assert high_score > low_score


def test_priority_band_mapping_is_valid() -> None:
    assert priority_band_from_score(95) == "Critical"
    assert priority_band_from_score(75) == "High"
    assert priority_band_from_score(50) == "Medium"
    assert priority_band_from_score(20) == "Low"
    assert priority_band_from_score(5) == "Info"
