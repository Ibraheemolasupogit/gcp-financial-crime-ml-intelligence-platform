"""Deterministic network risk scoring."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from financial_crime_ml.models.model_utils import load_yaml_config, resolve_repo_path
from financial_crime_ml.scoring.risk_scorer import band_from_score

DEFAULT_RISK_CONFIG_PATH = Path("configs/risk_scoring.yaml")


@dataclass(frozen=True)
class NetworkRiskConfig:
    """Network risk scoring configuration."""

    output_path: Path
    high_risk_networks_output_path: Path
    network_summary_output_path: Path
    network_report_output_path: Path
    max_high_risk_networks: int
    thresholds: dict[str, float]
    scoring_weights: dict[str, int]


def load_network_risk_config(
    config_path: str | Path = DEFAULT_RISK_CONFIG_PATH,
) -> NetworkRiskConfig:
    """Load network risk scoring settings."""
    raw_config = load_yaml_config(config_path).get("network_risk_scoring", {})
    return NetworkRiskConfig(
        output_path=resolve_repo_path(
            raw_config.get("output_path", "outputs/sample/network_risk_scores.csv")
        ),
        high_risk_networks_output_path=resolve_repo_path(
            raw_config.get(
                "high_risk_networks_output_path",
                "outputs/sample/high_risk_networks.csv",
            )
        ),
        network_summary_output_path=resolve_repo_path(
            raw_config.get("network_summary_output_path", "outputs/sample/network_summary.json")
        ),
        network_report_output_path=resolve_repo_path(
            raw_config.get("network_report_output_path", "reports/sample/network_risk_report.md")
        ),
        max_high_risk_networks=int(raw_config.get("max_high_risk_networks", 100)),
        thresholds=raw_config.get("thresholds", {}),
        scoring_weights=raw_config.get("scoring_weights", {}),
    )


def _reason_codes(row: pd.Series) -> list[str]:
    reasons: list[str] = []
    if int(row.get("shared_device_flag", 0)) == 1:
        reasons.extend(["SHARED_DEVICE", "DEVICE_USED_BY_MULTIPLE_ACCOUNTS"])
    if int(row.get("device_suspicious_transaction_count", 0)) > 0:
        reasons.append("DEVICE_LINKED_TO_SUSPICIOUS_ACTIVITY")
    if int(row.get("shared_beneficiary_flag", 0)) == 1:
        reasons.extend(["SHARED_BENEFICIARY", "BENEFICIARY_PAID_BY_MULTIPLE_ACCOUNTS"])
    if int(row.get("beneficiary_suspicious_transaction_count", 0)) > 0:
        reasons.append("BENEFICIARY_LINKED_TO_HIGH_RISK_ACTIVITY")
    if int(row.get("beneficiary_high_value_account_count", 0)) >= 2:
        reasons.append("BENEFICIARY_LINKED_TO_HIGH_VALUE_ACTIVITY")
    if int(row.get("suspicious_cluster_flag", 0)) == 1:
        reasons.append("SUSPICIOUS_CLUSTER")
    if int(row.get("mule_network_indicator", 0)) == 1:
        reasons.append("MULE_NETWORK_INDICATOR")
    return reasons


def score_network_risk(
    graph_features: pd.DataFrame,
    config: NetworkRiskConfig,
    optional_context: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Create transaction-level network risk scores."""
    features = graph_features.copy()
    if optional_context is not None:
        features = features.merge(optional_context, on="transaction_id", how="left")

    rows: list[dict[str, Any]] = []
    severity_bands = {
        "Critical": {"min": 90, "max": 100},
        "High": {"min": 70, "max": 89},
        "Medium": {"min": 40, "max": 69},
        "Low": {"min": 10, "max": 39},
        "Info": {"min": 0, "max": 9},
    }
    for _, row in features.iterrows():
        reasons = _reason_codes(row)
        score = 0
        weights = config.scoring_weights
        if int(row.get("shared_device_flag", 0)) == 1:
            score += weights.get("shared_device", 0)
        if int(row.get("shared_beneficiary_flag", 0)) == 1:
            score += weights.get("shared_beneficiary", 0)
        if int(row.get("suspicious_cluster_flag", 0)) == 1:
            score += weights.get("suspicious_cluster", 0)
        if row.get("network_cluster_size", 0) >= config.thresholds.get(
            "large_component_threshold",
            25,
        ):
            score += weights.get("large_component", 0)
        if int(row.get("mule_network_indicator", 0)) == 1:
            score += weights.get("mule_network", 0)
        if int(row.get("high_risk_network_flag", 0)) == 1:
            score += weights.get("high_risk_network", 0)
        if str(row.get("aml_risk_band", "")) in {"Critical", "High"}:
            score += weights.get("aml_high_or_critical", 0)
        if bool(row.get("is_anomaly", False)):
            score += weights.get("anomaly_flag", 0)

        score = min(int(score), 100)
        output = {
            "transaction_id": row["transaction_id"],
            "account_id": row["account_id"],
            "customer_id": row.get("customer_id"),
            "beneficiary_id": row["beneficiary_id"],
            "device_id": row["device_id"],
            "network_cluster_id": int(row["network_cluster_id"]),
            "network_cluster_size": int(row["network_cluster_size"]),
            "account_degree": int(row["account_degree"]),
            "shared_device_count": int(row["shared_device_count"]),
            "shared_beneficiary_count": int(row["shared_beneficiary_count"]),
            "device_account_count": int(row["device_account_count"]),
            "beneficiary_account_count": int(row["beneficiary_account_count"]),
            "account_centrality": float(row["account_centrality"]),
            "network_risk_score": score,
            "network_risk_band": band_from_score(score, severity_bands),
            "network_risk_reasons": "; ".join(reasons) if reasons else "No network risk indicators",
        }
        rows.append(output)

    return pd.DataFrame(rows)
