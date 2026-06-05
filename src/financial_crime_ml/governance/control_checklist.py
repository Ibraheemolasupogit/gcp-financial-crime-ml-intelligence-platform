"""Governance control checklist generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from financial_crime_ml.models.model_utils import resolve_repo_path

DEFAULT_GOVERNANCE_CONFIG_PATH = Path("configs/governance_controls.yaml")
VALID_CONTROL_STATUSES = {"passed", "warning", "failed", "not_applicable"}


def load_governance_config(
    config_path: str | Path = DEFAULT_GOVERNANCE_CONFIG_PATH,
) -> dict[str, Any]:
    """Load governance configuration."""
    resolved_path = resolve_repo_path(config_path)
    return yaml.safe_load(resolved_path.read_text(encoding="utf-8")) or {}


def _exists(path: str) -> bool:
    return resolve_repo_path(path).exists()


def build_control_checklist(config: dict[str, Any]) -> list[dict[str, str]]:
    """Build a structured model governance control checklist."""
    governance = config.get("governance", {})
    owner_roles = governance.get("owner_roles", {})
    frequencies = governance.get("review_frequencies", {})
    evidence = governance.get("required_evidence_paths", {})
    controls = [
        (
            "GOV-001",
            "Synthetic Data Governance",
            "data governance",
            "Confirm all datasets are synthetic and safe for public demonstration.",
            "data/sample/customers.csv",
            "data_governance",
            "per_release",
        ),
        (
            "GOV-002",
            "Synthetic Data Caveat",
            "synthetic data caveat",
            "Document that outputs must not be interpreted as real customer behaviour.",
            "README.md",
            "compliance",
            "per_release",
        ),
        (
            "GOV-003",
            "Data Validation Evidence",
            "data validation",
            "Retain schema and relationship validation evidence.",
            evidence.get("data_quality", "outputs/sample/data_quality_report.json"),
            "data_governance",
            "per_release",
        ),
        (
            "GOV-004",
            "Feature Engineering Documentation",
            "feature engineering documentation",
            "Document engineered features and typology indicators.",
            "docs/feature_engineering.md",
            "model_owner",
            "per_release",
        ),
        (
            "GOV-005",
            "Model Development Evidence",
            "model development",
            "Retain baseline model configuration and training workflow evidence.",
            "configs/model_config.yaml",
            "model_owner",
            "per_release",
        ),
        (
            "GOV-006",
            "Model Performance Evidence",
            "model performance",
            "Retain metrics for the supervised fraud classifier.",
            evidence.get("model_metrics", "outputs/sample/model_metrics.json"),
            "model_risk",
            "per_release",
        ),
        (
            "GOV-007",
            "AML Scoring Transparency",
            "AML risk scoring transparency",
            "Document deterministic AML scoring weights, bands, and reasons.",
            "docs/aml_risk_scoring.md",
            "compliance",
            "quarterly",
        ),
        (
            "GOV-008",
            "Anomaly Explainability",
            "anomaly detection explainability",
            "Retain anomaly reason-code and limitation evidence.",
            evidence.get("anomaly_report", "reports/sample/anomaly_detection_report.md"),
            "model_risk",
            "quarterly",
        ),
        (
            "GOV-009",
            "Network Risk Explainability",
            "graph/network risk explainability",
            "Retain graph design, reason-code, and network risk evidence.",
            evidence.get("network_report", "reports/sample/network_risk_report.md"),
            "model_risk",
            "quarterly",
        ),
        (
            "GOV-010",
            "NLP Triage Explainability",
            "NLP triage explainability",
            "Retain keyword rules, typology labels, and triage reason evidence.",
            evidence.get("nlp_report", "reports/sample/nlp_alert_triage_report.md"),
            "model_risk",
            "quarterly",
        ),
        (
            "GOV-011",
            "Monitoring And Drift Reporting",
            "monitoring and drift reporting",
            "Retain monitoring summary and drift report outputs.",
            evidence.get("monitoring_summary", "outputs/sample/monitoring_summary.json"),
            "model_owner",
            "ongoing",
        ),
        (
            "GOV-012",
            "Human-In-The-Loop Review",
            "human-in-the-loop review",
            "Require human review before any decisioning interpretation.",
            "configs/governance_controls.yaml",
            "compliance",
            "per_release",
        ),
        (
            "GOV-013",
            "Audit Logging",
            "audit logging",
            "Generate static audit log for local workflow traceability.",
            "outputs/sample/audit_log.jsonl",
            "engineering",
            "per_release",
        ),
        (
            "GOV-014",
            "Limitations And Exclusions",
            "limitations and exclusions",
            "Document non-goals and excluded production capabilities.",
            "docs/limitations.md",
            "model_risk",
            "per_release",
        ),
        (
            "GOV-015",
            "Responsible AI Controls",
            "responsible AI controls",
            "Confirm no autonomous final decisioning and explainable local workflows.",
            "configs/governance_controls.yaml",
            "model_risk",
            "quarterly",
        ),
        (
            "GOV-016",
            "No Autonomous Final Decisioning",
            "no autonomous final decisioning",
            "Confirm outputs are triage support and not final decisions.",
            "reports/sample/governance_evidence_pack.md",
            "compliance",
            "per_release",
        ),
        (
            "GOV-017",
            "Security And Secrets Hygiene",
            "security and secrets hygiene",
            "Confirm no secrets, real credentials, or live integrations are required.",
            ".gitignore",
            "security",
            "per_release",
        ),
        (
            "GOV-018",
            "Reproducibility",
            "reproducibility",
            "Retain deterministic seeds and local script entry points.",
            "configs/pipeline_config.yaml",
            "engineering",
            "per_release",
        ),
        (
            "GOV-019",
            "Regulatory And Model Risk Awareness",
            "regulatory/model risk awareness",
            "Document financial services model risk assumptions and controls.",
            "docs/model_risk_management.md",
            "model_risk",
            "annually",
        ),
    ]

    checklist = []
    for control in controls:
        control_id, name, category, description, source, owner_key, frequency_key = control
        exists = _exists(source)
        checklist.append(
            {
                "control_id": control_id,
                "control_name": name,
                "control_category": category,
                "control_description": description,
                "evidence_source": source,
                "status": "passed" if exists else "warning",
                "owner_role": owner_roles.get(owner_key, owner_key),
                "review_frequency": frequencies.get(frequency_key, frequency_key),
                "notes": "Evidence available."
                if exists
                else "Evidence should be reviewed or generated.",
            }
        )
    return checklist
