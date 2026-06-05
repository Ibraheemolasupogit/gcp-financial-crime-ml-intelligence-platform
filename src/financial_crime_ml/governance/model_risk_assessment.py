"""Model and component risk assessment generation."""

from __future__ import annotations

VALID_READINESS_STATUSES = {
    "portfolio_demo_only",
    "not_production_ready",
    "production_candidate_with_controls",
}


def build_model_risk_assessment() -> list[dict[str, object]]:
    """Build risk assessments for major lifecycle components."""
    components = [
        (
            "synthetic data generator",
            "data_generation",
            "Generate safe synthetic financial crime demonstration data.",
            "Medium",
            "Low",
            ["Synthetic patterns may be over-regular or unrealistic."],
            ["Synthetic data caveat", "No real customer data", "Deterministic seed"],
            ["data/sample/customers.csv", "docs/data_dictionary.md"],
        ),
        (
            "data validation layer",
            "data_validation",
            "Validate schemas, required values, and relationships.",
            "Medium",
            "Low",
            ["Validation is local and file-based only."],
            ["Schema checks", "Relationship checks", "Quality report"],
            ["outputs/sample/data_quality_report.json", "docs/data_validation.md"],
        ),
        (
            "feature engineering layer",
            "feature_engineering",
            "Create transaction, behaviour, typology, and risk features.",
            "Medium",
            "Medium",
            ["Feature logic may encode synthetic assumptions."],
            ["Feature documentation", "Feature summary", "Tests"],
            ["outputs/sample/feature_summary.json", "docs/feature_engineering.md"],
        ),
        (
            "fraud classifier",
            "supervised_model",
            "Baseline supervised suspicious transaction classifier.",
            "High",
            "Medium",
            ["Synthetic labels", "Not calibrated", "Potential overfitting"],
            ["Model card", "Metrics", "Holdout split"],
            ["reports/sample/model_card.md", "outputs/sample/model_metrics.json"],
        ),
        (
            "AML risk scoring",
            "deterministic_scoring",
            "Transparent deterministic AML risk scoring.",
            "High",
            "Medium",
            ["Rule weights are illustrative", "No production tuning"],
            ["Reason codes", "Configurable weights", "Documentation"],
            ["outputs/sample/aml_risk_scores.csv", "docs/aml_risk_scoring.md"],
        ),
        (
            "anomaly detection",
            "unsupervised_model",
            "IsolationForest-based anomaly discovery.",
            "High",
            "Medium",
            ["Unsupervised output may be hard to validate", "Synthetic distribution"],
            ["Reason codes", "Report", "No target leakage"],
            ["outputs/sample/anomaly_scores.csv", "reports/sample/anomaly_detection_report.md"],
        ),
        (
            "network risk scoring",
            "network_model",
            "Graph and shared-relationship risk scoring.",
            "High",
            "Medium",
            ["Synthetic network density", "Simple component logic"],
            ["Network report", "Reason codes", "NetworkX implementation"],
            ["outputs/sample/network_risk_scores.csv", "reports/sample/network_risk_report.md"],
        ),
        (
            "NLP alert triage",
            "nlp_triage",
            "Rule-based case-note typology classification and alert triage.",
            "Medium",
            "Medium",
            ["Keyword rules are limited", "Synthetic text is regular"],
            ["Keyword explainability", "Triage report", "Human review"],
            ["outputs/sample/nlp_alert_triage.csv", "reports/sample/nlp_alert_triage_report.md"],
        ),
        (
            "monitoring and drift reporting",
            "monitoring",
            "Local drift, risk distribution, and alert quality reporting.",
            "Medium",
            "Low",
            ["Static local report only", "No live monitoring service"],
            ["Monitoring report", "Drift summary", "Alert quality summary"],
            ["outputs/sample/monitoring_summary.json", "reports/sample/model_monitoring_report.md"],
        ),
    ]

    assessments = []
    for component in components:
        (
            name,
            component_type,
            purpose,
            inherent_risk,
            residual_risk,
            risks,
            controls,
            evidence,
        ) = component
        assessments.append(
            {
                "model_or_component_name": name,
                "component_type": component_type,
                "purpose": purpose,
                "inherent_risk_level": inherent_risk,
                "residual_risk_level": residual_risk,
                "key_risks": risks,
                "mitigating_controls": controls,
                "evidence_sources": evidence,
                "human_review_required": True,
                "production_readiness_status": "portfolio_demo_only",
                "limitations": [
                    "Synthetic-data-only demonstration.",
                    "Not validated for production financial crime operations.",
                    "Requires formal governance before operational use.",
                ],
            }
        )
    return assessments
