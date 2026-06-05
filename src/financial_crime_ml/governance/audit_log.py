"""Static audit log generation for the local workflow."""

from __future__ import annotations

import json
from pathlib import Path

from financial_crime_ml.models.model_utils import resolve_repo_path

AUDIT_TIMESTAMP = "2026-06-05T00:00:00+00:00"


def build_audit_events() -> list[dict[str, str]]:
    """Build deterministic local pipeline audit events."""
    events = [
        (
            "data_generation",
            "synthetic_data_generator",
            "generated sample datasets",
            "data/sample/transactions.csv",
        ),
        (
            "data_validation",
            "data_validation_layer",
            "validated sample datasets",
            "outputs/sample/data_quality_report.json",
        ),
        (
            "feature_engineering",
            "feature_pipeline",
            "built transaction features",
            "data/processed/transaction_features.csv",
        ),
        (
            "fraud_model_training",
            "fraud_classifier",
            "trained baseline classifier",
            "outputs/sample/model_metrics.json",
        ),
        (
            "aml_scoring",
            "aml_risk_scoring",
            "generated AML scores",
            "outputs/sample/aml_risk_scores.csv",
        ),
        (
            "anomaly_detection",
            "anomaly_detector",
            "generated anomaly scores",
            "outputs/sample/anomaly_scores.csv",
        ),
        (
            "network_risk_scoring",
            "network_risk_model",
            "generated network scores",
            "outputs/sample/network_risk_scores.csv",
        ),
        (
            "nlp_triage",
            "nlp_alert_triage",
            "classified case notes",
            "outputs/sample/nlp_alert_triage.csv",
        ),
        (
            "monitoring",
            "model_monitoring",
            "generated monitoring report",
            "reports/sample/model_monitoring_report.md",
        ),
        (
            "governance_pack_generation",
            "governance",
            "generated governance pack",
            "reports/sample/governance_evidence_pack.md",
        ),
    ]
    return [
        {
            "timestamp": AUDIT_TIMESTAMP,
            "event_type": event_type,
            "component": component,
            "action": action,
            "artifact_path": artifact_path,
            "status": "completed",
            "actor": "local_demo_pipeline",
            "notes": "Synthetic local milestone workflow event.",
        }
        for event_type, component, action, artifact_path in events
    ]


def write_audit_log(events: list[dict[str, str]], output_path: str | Path) -> Path:
    """Write JSONL audit log."""
    path = resolve_repo_path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(event) for event in events]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
