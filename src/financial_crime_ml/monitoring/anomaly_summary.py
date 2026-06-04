"""Anomaly detection summary and report generation."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from financial_crime_ml.models.anomaly_detector import (
    AnomalyDetectionConfig,
    load_anomaly_detection_config,
    run_anomaly_detector,
)
from financial_crime_ml.scoring.anomaly_ranker import rank_high_risk_anomalies


def _reason_counts(anomaly_scores: pd.DataFrame) -> dict[str, int]:
    counter: Counter[str] = Counter()
    anomalous_rows = anomaly_scores.loc[anomaly_scores["is_anomaly"]]
    for reasons in anomalous_rows["top_anomaly_reasons"].fillna(""):
        for reason in str(reasons).split("; "):
            if reason and reason != "NO_DOMINANT_REASON":
                counter[reason] += 1
    return dict(counter.most_common(10))


def create_anomaly_summary(
    anomaly_scores: pd.DataFrame,
    feature_columns: list[str],
    high_risk_anomalies: pd.DataFrame,
) -> dict[str, Any]:
    """Create a JSON-serialisable anomaly detection summary."""
    anomaly_count = int(anomaly_scores["is_anomaly"].sum())
    suspicious_available = "is_suspicious" in anomaly_scores.columns
    suspicious_overlap_count = (
        int((anomaly_scores["is_anomaly"] & anomaly_scores["is_suspicious"].astype(bool)).sum())
        if suspicious_available
        else 0
    )
    aml_overlap_count = (
        int(high_risk_anomalies["aml_risk_band"].isin({"Critical", "High"}).sum())
        if "aml_risk_band" in high_risk_anomalies.columns
        else 0
    )

    return {
        "row_count": int(len(anomaly_scores)),
        "feature_count": int(len(feature_columns)),
        "anomaly_count": anomaly_count,
        "anomaly_rate": float(anomaly_count / len(anomaly_scores)) if len(anomaly_scores) else 0.0,
        "band_counts": {
            band: int(count)
            for band, count in anomaly_scores["anomaly_band"].value_counts().sort_index().items()
        },
        "top_reason_codes": _reason_counts(anomaly_scores),
        "suspicious_overlap_count": suspicious_overlap_count,
        "suspicious_overlap_rate": float(suspicious_overlap_count / anomaly_count)
        if anomaly_count
        else 0.0,
        "aml_high_or_critical_overlap_count": aml_overlap_count,
        "notes": [
            "IsolationForest anomaly detection uses engineered numeric and boolean features.",
            "The supervised target is excluded from anomaly model training.",
            "Outputs are synthetic-data-only and intended for local portfolio demonstration.",
        ],
    }


def generate_anomaly_report(
    summary: dict[str, Any],
    feature_columns: list[str],
    output_path: str | Path,
) -> Path:
    """Write a markdown anomaly detection report."""
    path = Path(output_path)
    content = f"""# Anomaly Detection Report

## Purpose

This report summarises the Milestone 6 unsupervised anomaly detection layer for synthetic
financial crime transactions.

## Model Used

- IsolationForest
- Local scikit-learn implementation
- Synthetic engineered transaction features only

## Features Used

Feature count: {len(feature_columns)}

Features: {", ".join(feature_columns)}

## Excluded Columns

Identifiers, raw timestamp/text fields, helper labels, and `is_suspicious` are excluded from
anomaly model training. The synthetic suspicious label is used only for overlap analysis.

## Results

- Row count: {summary["row_count"]}
- Anomaly count: {summary["anomaly_count"]}
- Anomaly rate: {summary["anomaly_rate"]:.4f}
- Band distribution: {summary["band_counts"]}
- Top reason codes: {summary["top_reason_codes"]}
- Suspicious label overlap count: {summary["suspicious_overlap_count"]}
- Suspicious label overlap rate: {summary["suspicious_overlap_rate"]:.4f}
- AML high/critical overlap count: {summary["aml_high_or_critical_overlap_count"]}

## Limitations

This is a lightweight local anomaly discovery layer. It is not a production transaction
monitoring system, graph model, NLP model, model registry, serving API, or cloud deployment.

## Human Review Requirement

Anomaly outputs are triage aids only. Real financial crime workflows require investigator
review, escalation controls, governance approval, and validation before operational use.

## Synthetic Data Caveat

All data is synthetic and safe for public demonstration. Results should not be interpreted as
evidence of real-world financial crime detection performance.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def run_anomaly_detection_workflow(
    config: AnomalyDetectionConfig | None = None,
) -> dict[str, Any]:
    """Run anomaly detection, ranking, summary, and report generation."""
    resolved_config = config or load_anomaly_detection_config()
    anomaly_scores, feature_columns = run_anomaly_detector(resolved_config)
    high_risk_anomalies = rank_high_risk_anomalies(
        anomaly_scores,
        max_rows=resolved_config.max_high_risk_anomalies,
    )
    summary = create_anomaly_summary(anomaly_scores, feature_columns, high_risk_anomalies)

    resolved_config.anomaly_scores_output_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_config.high_risk_anomalies_output_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_config.anomaly_summary_output_path.parent.mkdir(parents=True, exist_ok=True)

    anomaly_scores.to_csv(resolved_config.anomaly_scores_output_path, index=False)
    high_risk_anomalies.to_csv(resolved_config.high_risk_anomalies_output_path, index=False)
    resolved_config.anomaly_summary_output_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    report_path = generate_anomaly_report(
        summary,
        feature_columns,
        resolved_config.anomaly_report_output_path,
    )

    return {
        "summary": summary,
        "feature_columns": feature_columns,
        "anomaly_scores_path": resolved_config.anomaly_scores_output_path,
        "high_risk_anomalies_path": resolved_config.high_risk_anomalies_output_path,
        "anomaly_summary_path": resolved_config.anomaly_summary_output_path,
        "anomaly_report_path": report_path,
    }
