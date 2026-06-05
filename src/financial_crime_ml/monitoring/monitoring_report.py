"""End-to-end local monitoring workflow and report generation."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from financial_crime_ml.models.model_utils import load_feature_table
from financial_crime_ml.monitoring.alert_quality_monitor import monitor_alert_quality
from financial_crime_ml.monitoring.drift_detection import (
    MonitoringConfig,
    load_monitoring_config,
    run_data_drift_checks,
)
from financial_crime_ml.monitoring.performance_monitor import (
    monitor_prediction_and_risk_distributions,
)


def _status_from_counts(total_drifted_features: int, missing_sources: list[str]) -> str:
    if total_drifted_features > 10:
        return "warning"
    if missing_sources:
        return "warning"
    return "passed"


def _input_sources_used(config: MonitoringConfig) -> list[str]:
    return [name for name, path in config.optional_input_paths.items() if path.exists()]


def create_monitoring_summary(
    config: MonitoringConfig,
    drift_summary: pd.DataFrame,
    prediction_summary: dict[str, Any],
    alert_quality_summary: dict[str, Any],
) -> dict[str, Any]:
    """Create overall monitoring summary."""
    total_drifted_features = (
        int(drift_summary["drift_flag"].sum()) if not drift_summary.empty else 0
    )
    missing_sources = prediction_summary.get("missing_optional_sources", [])
    status = _status_from_counts(total_drifted_features, missing_sources)
    observations = [
        f"{total_drifted_features} drifted features detected.",
        f"{alert_quality_summary.get('high_priority_alert_count', 0)} high-priority alerts found.",
        "Review monitoring trends before any model or rule changes.",
    ]
    if missing_sources:
        observations.append(f"Missing optional sources: {', '.join(missing_sources)}.")

    return {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "input_sources_used": _input_sources_used(config),
        "data_drift_status": "warning" if total_drifted_features else "passed",
        "prediction_monitoring_status": "warning" if missing_sources else "passed",
        "alert_quality_status": "passed",
        "total_drifted_features": total_drifted_features,
        "high_priority_alert_count": int(alert_quality_summary.get("high_priority_alert_count", 0)),
        "monitoring_observations": observations,
        "limitations": [
            "Local monitoring uses static synthetic artefacts.",
            (
                "No live service, cloud integration, dashboard, registry, or retraining "
                "automation is implemented."
            ),
            (
                "Thresholds are simple demonstration defaults and require governance review "
                "in real systems."
            ),
        ],
        "overall_status": status,
    }


def generate_monitoring_report(
    monitoring_summary: dict[str, Any],
    drift_summary: pd.DataFrame,
    prediction_summary: dict[str, Any],
    alert_quality_summary: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Write markdown monitoring report."""
    path = Path(output_path)
    drifted_features = (
        drift_summary.loc[drift_summary["drift_flag"], "feature_name"].head(20).tolist()
        if not drift_summary.empty
        else []
    )
    content = f"""# Model Monitoring Report

## Purpose

This report summarises Milestone 9 local monitoring and drift reporting across synthetic
financial crime model, scoring, anomaly, network, and NLP outputs.

## Monitoring Scope

Sources used: {monitoring_summary["input_sources_used"]}

## Data Drift Methodology

The transaction feature table is split into baseline and current periods using a deterministic
70/30 split, sorted by transaction timestamp when available. Numeric and boolean engineered
features are monitored using mean change, missing-rate change, and a simple PSI-style score.

## Prediction And Risk Monitoring Methodology

The workflow summarises fraud probability, fraud prediction rate, AML risk scores, anomaly
scores, network risk scores, NLP triage scores, and associated band distributions where
outputs are available.

## Alert Quality Monitoring Methodology

The workflow monitors prioritised alert volume, high/critical counts across AML, anomaly,
network, and NLP outputs, duplicate transaction coverage, and recurring reason codes.

## Key Findings

- Overall status: {monitoring_summary["overall_status"]}
- Total drifted features: {monitoring_summary["total_drifted_features"]}
- High-priority alert count: {monitoring_summary["high_priority_alert_count"]}
- Drifted features: {drifted_features}

## Risk Band Distribution Summaries

- AML: {prediction_summary.get("aml", {}).get("aml_risk_band_counts", {})}
- Anomaly: {prediction_summary.get("anomaly", {}).get("anomaly_band_counts", {})}
- Network: {prediction_summary.get("network", {}).get("network_risk_band_counts", {})}
- NLP: {prediction_summary.get("nlp", {}).get("nlp_triage_band_counts", {})}

## Alert Volume Observations

{alert_quality_summary.get("recommended_monitoring_observations", [])}

Top reason codes: {alert_quality_summary.get("top_reason_codes", {})}

## Operational Recommendations

- Review drifted feature list before model interpretation or release decisions.
- Investigate concentration of high and critical alert bands.
- Track recurring reason codes as potential rule tuning or data quality signals.
- Use this local report as a template for production monitoring requirements.

## Limitations

This milestone does not implement live monitoring, GCP services, dashboards, APIs, model
registry, retraining automation, agentic AI, or real customer data monitoring.

## Synthetic Data Caveat

All inputs are synthetic. Monitoring findings demonstrate engineering workflow design and
should not be interpreted as production model performance or operational risk evidence.

## Human Review Requirement

Monitoring outputs require analyst, model risk, and control-owner review before any real-world
action could be taken in a financial services environment.

## GCP Alignment Note

This local approach maps conceptually to Vertex AI Model Monitoring for drift signals, Cloud
Logging for operational events, BigQuery for monitoring tables, and Looker Studio for reporting.
No live GCP integration is implemented in this milestone.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def run_monitoring_workflow(config: MonitoringConfig | None = None) -> dict[str, Any]:
    """Run local monitoring and write all monitoring artefacts."""
    resolved_config = config or load_monitoring_config()
    feature_path = resolved_config.optional_input_paths["transaction_features"]
    feature_table = load_feature_table(feature_path)

    drift_summary = run_data_drift_checks(feature_table, resolved_config)
    prediction_summary = monitor_prediction_and_risk_distributions(
        resolved_config.optional_input_paths
    )
    alert_quality_summary = monitor_alert_quality(
        resolved_config.optional_input_paths,
        resolved_config.high_priority_bands,
    )
    monitoring_summary = create_monitoring_summary(
        resolved_config,
        drift_summary,
        prediction_summary,
        alert_quality_summary,
    )

    output_paths = resolved_config.output_paths
    for path in output_paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    drift_summary.to_csv(output_paths["data_drift_summary"], index=False)
    output_paths["prediction_monitoring_summary"].write_text(
        json.dumps(prediction_summary, indent=2),
        encoding="utf-8",
    )
    output_paths["alert_quality_summary"].write_text(
        json.dumps(alert_quality_summary, indent=2),
        encoding="utf-8",
    )
    output_paths["monitoring_summary"].write_text(
        json.dumps(monitoring_summary, indent=2),
        encoding="utf-8",
    )
    report_path = generate_monitoring_report(
        monitoring_summary,
        drift_summary,
        prediction_summary,
        alert_quality_summary,
        output_paths["monitoring_report"],
    )

    return {
        "monitoring_summary": monitoring_summary,
        "data_drift_summary_path": output_paths["data_drift_summary"],
        "prediction_monitoring_summary_path": output_paths["prediction_monitoring_summary"],
        "alert_quality_summary_path": output_paths["alert_quality_summary"],
        "monitoring_summary_path": output_paths["monitoring_summary"],
        "monitoring_report_path": report_path,
    }
