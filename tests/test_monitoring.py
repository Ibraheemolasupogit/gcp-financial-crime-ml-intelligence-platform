from pathlib import Path

import pandas as pd

from financial_crime_ml.monitoring.alert_quality_monitor import monitor_alert_quality
from financial_crime_ml.monitoring.drift_detection import (
    MonitoringConfig,
    load_monitoring_config,
    run_data_drift_checks,
)
from financial_crime_ml.monitoring.monitoring_report import run_monitoring_workflow
from financial_crime_ml.monitoring.performance_monitor import (
    monitor_prediction_and_risk_distributions,
)

REQUIRED_MONITORING_KEYS = {
    "generated_at",
    "input_sources_used",
    "data_drift_status",
    "prediction_monitoring_status",
    "alert_quality_status",
    "total_drifted_features",
    "high_priority_alert_count",
    "monitoring_observations",
    "limitations",
    "overall_status",
}


def _config(tmp_path: Path) -> MonitoringConfig:
    return MonitoringConfig(
        baseline_fraction=0.7,
        drift_percent_change_threshold=0.25,
        missing_rate_change_threshold=0.05,
        drift_score_threshold=0.1,
        high_priority_bands=("Critical", "High"),
        optional_input_paths={
            "transaction_features": Path("data/processed/transaction_features.csv").resolve(),
            "fraud_predictions": Path("outputs/sample/fraud_predictions.csv").resolve(),
            "aml_risk_scores": Path("outputs/sample/aml_risk_scores.csv").resolve(),
            "prioritised_alerts": Path("outputs/sample/prioritised_alerts.csv").resolve(),
            "anomaly_scores": Path("outputs/sample/anomaly_scores.csv").resolve(),
            "high_risk_anomalies": Path("outputs/sample/high_risk_anomalies.csv").resolve(),
            "network_risk_scores": Path("outputs/sample/network_risk_scores.csv").resolve(),
            "high_risk_networks": Path("outputs/sample/high_risk_networks.csv").resolve(),
            "nlp_alert_triage": Path("outputs/sample/nlp_alert_triage.csv").resolve(),
        },
        output_paths={
            "data_drift_summary": tmp_path / "data_drift_summary.csv",
            "prediction_monitoring_summary": tmp_path / "prediction_monitoring_summary.json",
            "alert_quality_summary": tmp_path / "alert_quality_summary.json",
            "monitoring_summary": tmp_path / "monitoring_summary.json",
            "monitoring_report": tmp_path / "model_monitoring_report.md",
        },
    )


def test_data_drift_workflow_runs_successfully(tmp_path: Path) -> None:
    config = _config(tmp_path)
    features = pd.read_csv(config.optional_input_paths["transaction_features"])

    drift = run_data_drift_checks(features, config)

    assert not drift.empty
    assert "drift_flag" in drift.columns


def test_monitoring_workflow_creates_outputs(tmp_path: Path) -> None:
    result = run_monitoring_workflow(_config(tmp_path))

    assert result["data_drift_summary_path"].exists()
    assert result["prediction_monitoring_summary_path"].exists()
    assert result["alert_quality_summary_path"].exists()
    assert result["monitoring_summary_path"].exists()
    assert result["monitoring_report_path"].exists()


def test_monitoring_summary_required_keys_exist(tmp_path: Path) -> None:
    result = run_monitoring_workflow(_config(tmp_path))

    assert REQUIRED_MONITORING_KEYS.issubset(result["monitoring_summary"])


def test_drift_flags_are_boolean_values(tmp_path: Path) -> None:
    result = run_monitoring_workflow(_config(tmp_path))
    drift = pd.read_csv(result["data_drift_summary_path"])

    assert set(drift["drift_flag"].astype(str)).issubset({"True", "False"})


def test_missing_optional_files_are_handled_gracefully(tmp_path: Path) -> None:
    config = _config(tmp_path)
    missing_paths = {
        "fraud_predictions": tmp_path / "missing_fraud.csv",
        "aml_risk_scores": tmp_path / "missing_aml.csv",
        "anomaly_scores": tmp_path / "missing_anomaly.csv",
        "network_risk_scores": tmp_path / "missing_network.csv",
        "nlp_alert_triage": tmp_path / "missing_nlp.csv",
    }

    prediction_summary = monitor_prediction_and_risk_distributions(missing_paths)

    assert set(prediction_summary["missing_optional_sources"]) == set(missing_paths)
    alert_quality = monitor_alert_quality(missing_paths, config.high_priority_bands)
    assert alert_quality["total_prioritised_alerts"] == 0


def test_monitoring_config_can_be_loaded() -> None:
    config = load_monitoring_config()

    assert config.baseline_fraction == 0.7
    assert "transaction_features" in config.optional_input_paths
    assert "monitoring_summary" in config.output_paths


def test_cli_underlying_monitoring_workflow_can_run(tmp_path: Path) -> None:
    result = run_monitoring_workflow(_config(tmp_path))

    assert result["monitoring_summary"]["overall_status"] in {"passed", "warning", "failed"}
