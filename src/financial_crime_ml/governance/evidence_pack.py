"""Governance evidence inventory and markdown pack generation."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from financial_crime_ml.models.model_utils import resolve_repo_path


def _artifact(
    name: str,
    path: str,
    artifact_type: str,
    stage: str,
    description: str,
    relevance: str,
) -> dict[str, object]:
    resolved_path = resolve_repo_path(path)
    return {
        "artifact_name": name,
        "artifact_path": path,
        "artifact_type": artifact_type,
        "lifecycle_stage": stage,
        "description": description,
        "exists": resolved_path.exists(),
        "evidence_relevance": relevance,
    }


def build_evidence_inventory() -> list[dict[str, object]]:
    """List key project artefacts for governance evidence."""
    artifacts = [
        ("customers dataset", "data/sample/customers.csv", "dataset", "data_generation"),
        ("accounts dataset", "data/sample/accounts.csv", "dataset", "data_generation"),
        ("transactions dataset", "data/sample/transactions.csv", "dataset", "data_generation"),
        (
            "data quality report",
            "outputs/sample/data_quality_report.json",
            "validation_report",
            "data_validation",
        ),
        (
            "feature table",
            "data/processed/transaction_features.csv",
            "dataset",
            "feature_engineering",
        ),
        (
            "feature summary",
            "outputs/sample/feature_summary.json",
            "summary",
            "feature_engineering",
        ),
        ("model metrics", "outputs/sample/model_metrics.json", "metrics", "supervised_fraud_model"),
        (
            "fraud predictions",
            "outputs/sample/fraud_predictions.csv",
            "predictions",
            "supervised_fraud_model",
        ),
        ("AML scores", "outputs/sample/aml_risk_scores.csv", "scores", "aml_risk_scoring"),
        (
            "prioritised alerts",
            "outputs/sample/prioritised_alerts.csv",
            "triage_output",
            "aml_risk_scoring",
        ),
        ("anomaly scores", "outputs/sample/anomaly_scores.csv", "scores", "anomaly_detection"),
        (
            "high risk anomalies",
            "outputs/sample/high_risk_anomalies.csv",
            "ranking",
            "anomaly_detection",
        ),
        (
            "network risk scores",
            "outputs/sample/network_risk_scores.csv",
            "scores",
            "network_risk_modelling",
        ),
        (
            "high risk networks",
            "outputs/sample/high_risk_networks.csv",
            "ranking",
            "network_risk_modelling",
        ),
        (
            "NLP alert triage",
            "outputs/sample/nlp_alert_triage.csv",
            "triage_output",
            "nlp_alert_triage",
        ),
        (
            "case note classifications",
            "outputs/sample/nlp_case_note_classifications.csv",
            "classification_output",
            "nlp_alert_triage",
        ),
        ("monitoring summary", "outputs/sample/monitoring_summary.json", "summary", "monitoring"),
        (
            "prediction monitoring",
            "outputs/sample/prediction_monitoring_summary.json",
            "summary",
            "monitoring",
        ),
        (
            "alert quality summary",
            "outputs/sample/alert_quality_summary.json",
            "summary",
            "monitoring",
        ),
        ("model card", "reports/sample/model_card.md", "markdown_report", "governance"),
        (
            "monitoring report",
            "reports/sample/model_monitoring_report.md",
            "markdown_report",
            "monitoring",
        ),
        (
            "anomaly report",
            "reports/sample/anomaly_detection_report.md",
            "markdown_report",
            "anomaly_detection",
        ),
        (
            "network report",
            "reports/sample/network_risk_report.md",
            "markdown_report",
            "network_risk_modelling",
        ),
        (
            "NLP report",
            "reports/sample/nlp_alert_triage_report.md",
            "markdown_report",
            "nlp_alert_triage",
        ),
        ("model config", "configs/model_config.yaml", "config", "configuration"),
        ("risk scoring config", "configs/risk_scoring.yaml", "config", "configuration"),
        ("monitoring config", "configs/monitoring_config.yaml", "config", "configuration"),
        ("governance config", "configs/governance_controls.yaml", "config", "configuration"),
        ("data dictionary", "docs/data_dictionary.md", "documentation", "documentation"),
        (
            "model risk management docs",
            "docs/model_risk_management.md",
            "documentation",
            "documentation",
        ),
        ("monitoring docs", "docs/monitoring_strategy.md", "documentation", "documentation"),
    ]
    return [
        _artifact(name, path, artifact_type, stage, f"{name} evidence.", "Governance traceability")
        for name, path, artifact_type, stage in artifacts
    ]


def generate_governance_evidence_pack(
    checklist: list[dict[str, Any]],
    assessments: list[dict[str, Any]],
    inventory: list[dict[str, Any]],
    traceability: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Write consolidated governance evidence pack markdown."""
    path = resolve_repo_path(output_path)
    status_counts = Counter(control["status"] for control in checklist)
    readiness_counts = Counter(item["production_readiness_status"] for item in assessments)
    inventory_count = sum(1 for item in inventory if item["exists"])
    content = f"""# Governance Evidence Pack

## Executive Summary

This evidence pack consolidates governance artefacts for the local synthetic financial crime ML
intelligence platform. It demonstrates documentation discipline, control evidence,
traceability, limitations, and human review expectations.

## Project Scope

The project covers synthetic data generation, validation, feature engineering, fraud
classification, AML scoring, anomaly detection, network risk modelling, NLP alert triage,
monitoring, and governance evidence. It remains local-first and synthetic-data-only.

## Synthetic Data Statement

No real customer data, credentials, production systems, or confidential financial crime
intelligence are used.

## Lifecycle Overview

Lifecycle stages: {list(traceability)}

## Controls Summary

Control status counts: {dict(status_counts)}

## Evidence Inventory

Available evidence artefacts: {inventory_count} of {len(inventory)}

## Model And Component Risk Assessment Summary

Production readiness counts: {dict(readiness_counts)}

All components require human review and remain portfolio demonstration artefacts.

## Monitoring Evidence Summary

Monitoring evidence is available through model monitoring, drift, prediction, risk, and alert
quality summaries.

## Human Review And Decisioning Policy

No autonomous final decisioning is allowed. Outputs are triage and decision-support artefacts
only and require financial crime investigator review before any operational interpretation.

## Responsible AI Controls

Controls include synthetic data only, explainable reason codes, documented limitations, human
review, no real credentials, and no autonomous decisions.

## Limitations

This is not a production deployment, live monitoring service, model registry, dashboard, API,
agentic workflow, or regulatory reporting tool.

## Exclusions

The project excludes live GCP deployment, real data, live governance workflow, retraining
automation, and production decisioning.

## Auditability Notes

The evidence pack includes a deterministic audit log and lifecycle traceability map linking
inputs, outputs, configs, documentation, risks, and limitations.

## GCP Conceptual Mapping

The local evidence maps conceptually to BigQuery evidence tables, Vertex AI model metadata,
Cloud Logging audit trails, Cloud Storage artefacts, and Looker Studio governance reporting.
No live GCP integration is implemented.

## Next Governance Improvements

- Add formal approval workflow metadata.
- Add independent validation sign-off placeholders.
- Add versioned artefact hashes.
- Add release-level control attestations.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
