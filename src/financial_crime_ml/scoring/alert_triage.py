"""NLP alert triage scoring."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from financial_crime_ml.models.model_utils import load_yaml_config, resolve_repo_path
from financial_crime_ml.scoring.risk_scorer import band_from_score

DEFAULT_RISK_CONFIG_PATH = Path("configs/risk_scoring.yaml")
DEFAULT_MONITORING_CONFIG_PATH = Path("configs/monitoring_config.yaml")


@dataclass(frozen=True)
class NLPTriageConfig:
    """NLP alert triage scoring settings."""

    band_thresholds: dict[str, int]
    typology_base_scores: dict[str, int]
    enrichment_weights: dict[str, int]
    suggested_review_queue_mapping: dict[str, str]
    optional_enrichment_paths: dict[str, Path]


def load_nlp_triage_config(
    risk_config_path: str | Path = DEFAULT_RISK_CONFIG_PATH,
    monitoring_config_path: str | Path = DEFAULT_MONITORING_CONFIG_PATH,
) -> NLPTriageConfig:
    """Load NLP scoring and optional enrichment settings."""
    risk_config: dict[str, Any] = load_yaml_config(risk_config_path).get("nlp_alert_triage", {})
    monitoring_config: dict[str, Any] = load_yaml_config(monitoring_config_path).get(
        "nlp_alert_triage",
        {},
    )
    optional_paths = {
        key: resolve_repo_path(path)
        for key, path in monitoring_config.get("optional_enrichment_paths", {}).items()
    }
    return NLPTriageConfig(
        band_thresholds=risk_config.get("band_thresholds", {}),
        typology_base_scores=risk_config.get("typology_base_scores", {}),
        enrichment_weights=risk_config.get("enrichment_weights", {}),
        suggested_review_queue_mapping=risk_config.get("suggested_review_queue_mapping", {}),
        optional_enrichment_paths=optional_paths,
    )


def load_optional_enrichments(config: NLPTriageConfig) -> tuple[pd.DataFrame, list[str]]:
    """Load optional enrichment files when present."""
    context: pd.DataFrame | None = None
    sources_used: list[str] = []
    column_map = {
        "prioritised_alerts": ["transaction_id", "priority_band", "priority_score"],
        "aml_risk_scores": ["transaction_id", "aml_risk_band", "aml_risk_score"],
        "anomaly_scores": ["transaction_id", "is_anomaly", "anomaly_score", "anomaly_band"],
        "network_risk_scores": ["transaction_id", "network_risk_band", "network_risk_score"],
    }
    for source, path in config.optional_enrichment_paths.items():
        if not path.exists():
            continue
        dataset = pd.read_csv(path)
        selected_columns = [
            column for column in column_map.get(source, []) if column in dataset.columns
        ]
        if "transaction_id" not in selected_columns:
            continue
        dataset = dataset[selected_columns].drop_duplicates("transaction_id")
        context = (
            dataset
            if context is None
            else context.merge(dataset, on="transaction_id", how="outer")
        )
        sources_used.append(source)
    return (
        context if context is not None else pd.DataFrame(columns=["transaction_id"]),
        sources_used,
    )


def _severity_bands(config: NLPTriageConfig) -> dict[str, dict[str, int]]:
    return {
        "Critical": {"min": config.band_thresholds.get("Critical", 90), "max": 100},
        "High": {"min": config.band_thresholds.get("High", 70), "max": 89},
        "Medium": {"min": config.band_thresholds.get("Medium", 40), "max": 69},
        "Low": {"min": config.band_thresholds.get("Low", 10), "max": 39},
        "Info": {"min": config.band_thresholds.get("Info", 0), "max": 9},
    }


def score_alert_triage(
    alerts: pd.DataFrame,
    case_note_classifications: pd.DataFrame,
    config: NLPTriageConfig,
    enrichment_context: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Score NLP alert triage rows."""
    latest_case_note = case_note_classifications.sort_values("case_note_id").drop_duplicates(
        "alert_id",
        keep="last",
    )
    triage = alerts.merge(
        latest_case_note[
            ["alert_id", "predicted_typology", "typology_confidence", "typology_reasons"]
        ],
        on="alert_id",
        how="left",
    )
    triage["predicted_typology"] = triage["predicted_typology"].fillna("unknown")
    triage["typology_confidence"] = triage["typology_confidence"].fillna(0.35)
    triage["typology_reasons"] = triage["typology_reasons"].fillna("NO_CASE_NOTE")

    if enrichment_context is not None and not enrichment_context.empty:
        triage = triage.merge(enrichment_context, on="transaction_id", how="left")

    rows: list[dict[str, object]] = []
    for _, row in triage.iterrows():
        typology = str(row["predicted_typology"])
        score = int(config.typology_base_scores.get(typology, 20))
        reasons = [f"TYPOLOGY:{typology}", str(row["typology_reasons"])]
        if row.get("alert_severity") == "high":
            score += config.enrichment_weights.get("severe_alert", 0)
            reasons.append("HIGH_ALERT_SEVERITY")
        if str(row.get("priority_band", "")) in {"Critical", "High"}:
            score += config.enrichment_weights.get("prioritised_alert_high_or_critical", 0)
            reasons.append("PRIORITISED_ALERT_HIGH_OR_CRITICAL")
        if str(row.get("aml_risk_band", "")) in {"Critical", "High"}:
            score += config.enrichment_weights.get("aml_high_or_critical", 0)
            reasons.append("AML_HIGH_OR_CRITICAL")
        if bool(row.get("is_anomaly", False)):
            score += config.enrichment_weights.get("anomaly_flag", 0)
            reasons.append("ANOMALY_OVERLAP")
        if str(row.get("network_risk_band", "")) in {"Critical", "High"}:
            score += config.enrichment_weights.get("network_high_or_critical", 0)
            reasons.append("NETWORK_HIGH_OR_CRITICAL")

        score = min(score, 100)
        band = band_from_score(score, _severity_bands(config))
        queue = config.suggested_review_queue_mapping.get(typology, "Monitoring queue")
        if band == "Critical":
            queue = "Financial crime investigation"
        elif band == "Info":
            queue = "No immediate action"

        rows.append(
            {
                "alert_id": row["alert_id"],
                "transaction_id": row["transaction_id"],
                "account_id": row["account_id"],
                "alert_type": row["alert_type"],
                "alert_severity": row["alert_severity"],
                "alert_reason": row["alert_reason"],
                "predicted_typology": typology,
                "typology_confidence": round(float(row["typology_confidence"]), 4),
                "nlp_triage_score": score,
                "nlp_triage_band": band,
                "nlp_triage_reasons": "; ".join(reason for reason in reasons if reason),
                "suggested_review_queue": queue,
            }
        )
    return pd.DataFrame(rows)
