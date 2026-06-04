from pathlib import Path

import pandas as pd

from financial_crime_ml.models.anomaly_detector import (
    AnomalyDetectionConfig,
    load_anomaly_detection_config,
    run_anomaly_detector,
    select_anomaly_features,
)
from financial_crime_ml.models.model_utils import load_feature_table
from financial_crime_ml.monitoring import run_anomaly_detection_workflow
from financial_crime_ml.scoring.anomaly_ranker import rank_high_risk_anomalies

VALID_BANDS = {"Critical", "High", "Medium", "Low", "Info"}
REQUIRED_SCORE_COLUMNS = {
    "transaction_id",
    "account_id",
    "customer_id",
    "anomaly_score",
    "anomaly_rank",
    "is_anomaly",
    "anomaly_band",
    "is_suspicious",
    "suspicious_pattern",
    "top_anomaly_reasons",
}


def _config(tmp_path: Path) -> AnomalyDetectionConfig:
    return AnomalyDetectionConfig(
        anomaly_model_type="isolation_forest",
        contamination=0.08,
        random_seed=42,
        input_path=Path("data/processed/transaction_features.csv").resolve(),
        anomaly_scores_output_path=tmp_path / "anomaly_scores.csv",
        high_risk_anomalies_output_path=tmp_path / "high_risk_anomalies.csv",
        anomaly_summary_output_path=tmp_path / "anomaly_summary.json",
        anomaly_report_output_path=tmp_path / "anomaly_detection_report.md",
        max_high_risk_anomalies=25,
        excluded_columns=(
            "transaction_id",
            "account_id",
            "customer_id",
            "beneficiary_id",
            "device_id",
            "suspicious_pattern",
            "transaction_timestamp",
            "is_suspicious",
            "currency",
            "transaction_type",
            "merchant_category",
            "origin_country",
            "destination_country",
            "channel",
        ),
    )


def test_anomaly_workflow_runs_successfully(tmp_path: Path) -> None:
    result = run_anomaly_detection_workflow(_config(tmp_path))

    assert result["summary"]["row_count"] == 5000
    assert result["summary"]["anomaly_count"] > 0


def test_anomaly_outputs_are_created(tmp_path: Path) -> None:
    result = run_anomaly_detection_workflow(_config(tmp_path))

    assert result["anomaly_scores_path"].exists()
    assert result["high_risk_anomalies_path"].exists()
    assert result["anomaly_summary_path"].exists()
    assert result["anomaly_report_path"].exists()


def test_required_output_columns_and_bands_exist(tmp_path: Path) -> None:
    result = run_anomaly_detection_workflow(_config(tmp_path))
    scores = pd.read_csv(result["anomaly_scores_path"])

    assert REQUIRED_SCORE_COLUMNS.issubset(scores.columns)
    assert set(scores["anomaly_band"]).issubset(VALID_BANDS)


def test_anomaly_reasons_are_generated(tmp_path: Path) -> None:
    result = run_anomaly_detection_workflow(_config(tmp_path))
    scores = pd.read_csv(result["anomaly_scores_path"])

    assert scores["top_anomaly_reasons"].notna().all()
    assert (scores["top_anomaly_reasons"].str.len() > 0).all()


def test_is_suspicious_is_not_used_as_training_feature(tmp_path: Path) -> None:
    config = _config(tmp_path)
    features = load_feature_table(config.input_path)
    feature_columns = select_anomaly_features(features, config)

    assert "is_suspicious" not in feature_columns


def test_missing_optional_outputs_are_handled_gracefully(tmp_path: Path) -> None:
    config = _config(tmp_path)
    anomaly_scores, _ = run_anomaly_detector(config)

    ranked = rank_high_risk_anomalies(
        anomaly_scores,
        max_rows=10,
        fraud_predictions_path=tmp_path / "missing_fraud.csv",
        aml_risk_scores_path=tmp_path / "missing_aml.csv",
        prioritised_alerts_path=tmp_path / "missing_priority.csv",
    )

    assert len(ranked) == 10
    assert "fraud_probability" in ranked.columns
    assert "aml_risk_score" in ranked.columns


def test_cli_underlying_workflow_can_run(tmp_path: Path) -> None:
    result = run_anomaly_detection_workflow(_config(tmp_path))

    assert result["anomaly_scores_path"].exists()


def test_anomaly_config_can_be_loaded() -> None:
    config = load_anomaly_detection_config()

    assert config.anomaly_model_type == "isolation_forest"
    assert config.contamination > 0
