"""Prediction and risk distribution monitoring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def _read_optional(path: Path) -> pd.DataFrame | None:
    if not path.exists() or not path.is_file():
        return None
    return pd.read_csv(path)


def _numeric_summary(series: pd.Series) -> dict[str, float]:
    values = pd.to_numeric(series, errors="coerce")
    return {
        "count": int(values.count()),
        "mean": float(values.mean()) if values.count() else 0.0,
        "min": float(values.min()) if values.count() else 0.0,
        "p50": float(values.quantile(0.5)) if values.count() else 0.0,
        "p95": float(values.quantile(0.95)) if values.count() else 0.0,
        "max": float(values.max()) if values.count() else 0.0,
    }


def _value_counts(series: pd.Series) -> dict[str, int]:
    return {str(label): int(count) for label, count in series.value_counts().items()}


def monitor_prediction_and_risk_distributions(
    input_paths: dict[str, Path],
) -> dict[str, Any]:
    """Summarise available model/scoring output distributions."""
    missing_sources: list[str] = []
    summary: dict[str, Any] = {}

    fraud = _read_optional(input_paths.get("fraud_predictions", Path("")))
    if fraud is None:
        missing_sources.append("fraud_predictions")
        summary["fraud"] = {"status": "missing"}
    else:
        summary["fraud"] = {
            "status": "available",
            "row_count": int(len(fraud)),
            "fraud_probability": _numeric_summary(fraud["fraud_probability"]),
            "fraud_prediction_rate": float(fraud["fraud_prediction"].mean()),
        }

    aml = _read_optional(input_paths.get("aml_risk_scores", Path("")))
    if aml is None:
        missing_sources.append("aml_risk_scores")
        summary["aml"] = {"status": "missing"}
    else:
        summary["aml"] = {
            "status": "available",
            "row_count": int(len(aml)),
            "aml_risk_score": _numeric_summary(aml["aml_risk_score"]),
            "aml_risk_band_counts": _value_counts(aml["aml_risk_band"]),
        }

    anomaly = _read_optional(input_paths.get("anomaly_scores", Path("")))
    if anomaly is None:
        missing_sources.append("anomaly_scores")
        summary["anomaly"] = {"status": "missing"}
    else:
        summary["anomaly"] = {
            "status": "available",
            "row_count": int(len(anomaly)),
            "anomaly_score": _numeric_summary(anomaly["anomaly_score"]),
            "is_anomaly_rate": float(anomaly["is_anomaly"].astype(bool).mean()),
            "anomaly_band_counts": _value_counts(anomaly["anomaly_band"]),
        }

    network = _read_optional(input_paths.get("network_risk_scores", Path("")))
    if network is None:
        missing_sources.append("network_risk_scores")
        summary["network"] = {"status": "missing"}
    else:
        summary["network"] = {
            "status": "available",
            "row_count": int(len(network)),
            "network_risk_score": _numeric_summary(network["network_risk_score"]),
            "network_risk_band_counts": _value_counts(network["network_risk_band"]),
        }

    nlp = _read_optional(input_paths.get("nlp_alert_triage", Path("")))
    if nlp is None:
        missing_sources.append("nlp_alert_triage")
        summary["nlp"] = {"status": "missing"}
    else:
        summary["nlp"] = {
            "status": "available",
            "row_count": int(len(nlp)),
            "nlp_triage_score": _numeric_summary(nlp["nlp_triage_score"]),
            "nlp_triage_band_counts": _value_counts(nlp["nlp_triage_band"]),
            "predicted_typology_distribution": _value_counts(nlp["predicted_typology"]),
        }

    summary["missing_optional_sources"] = missing_sources
    summary["overall_notes"] = [
        "Prediction and risk monitoring uses local output artefacts only.",
        "Missing optional files are reported but do not fail the workflow.",
    ]
    return summary
