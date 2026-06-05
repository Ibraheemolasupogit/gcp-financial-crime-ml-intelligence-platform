"""Local data drift checks for engineered transaction features."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from financial_crime_ml.models.model_utils import load_yaml_config, resolve_repo_path

DEFAULT_MONITORING_CONFIG_PATH = Path("configs/monitoring_config.yaml")


@dataclass(frozen=True)
class MonitoringConfig:
    """Configuration for local monitoring outputs."""

    baseline_fraction: float
    drift_percent_change_threshold: float
    missing_rate_change_threshold: float
    drift_score_threshold: float
    high_priority_bands: tuple[str, ...]
    optional_input_paths: dict[str, Path]
    output_paths: dict[str, Path]


def load_monitoring_config(
    config_path: str | Path = DEFAULT_MONITORING_CONFIG_PATH,
) -> MonitoringConfig:
    """Load local monitoring settings."""
    raw = load_yaml_config(config_path).get("model_monitoring", {})
    return MonitoringConfig(
        baseline_fraction=float(raw.get("baseline_fraction", 0.7)),
        drift_percent_change_threshold=float(raw.get("drift_percent_change_threshold", 0.25)),
        missing_rate_change_threshold=float(raw.get("missing_rate_change_threshold", 0.05)),
        drift_score_threshold=float(raw.get("drift_score_threshold", 0.1)),
        high_priority_bands=tuple(raw.get("high_priority_bands", ["Critical", "High"])),
        optional_input_paths={
            name: resolve_repo_path(path)
            for name, path in raw.get("optional_input_paths", {}).items()
        },
        output_paths={
            name: resolve_repo_path(path) for name, path in raw.get("output_paths", {}).items()
        },
    )


def split_baseline_current(
    feature_table: pd.DataFrame,
    baseline_fraction: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split features into baseline/current windows."""
    data = feature_table.copy()
    if "transaction_timestamp" in data.columns:
        data = data.sort_values("transaction_timestamp")
    split_index = max(1, min(len(data) - 1, int(len(data) * baseline_fraction)))
    return data.iloc[:split_index].copy(), data.iloc[split_index:].copy()


def _psi_score(baseline: pd.Series, current: pd.Series, bins: int = 10) -> float:
    baseline_values = pd.to_numeric(baseline, errors="coerce").astype(float).dropna()
    current_values = pd.to_numeric(current, errors="coerce").astype(float).dropna()
    if baseline_values.empty or current_values.empty:
        return 0.0
    quantiles = np.linspace(0, 1, bins + 1)
    edges = np.unique(np.quantile(baseline_values, quantiles))
    if len(edges) < 3:
        return 0.0
    baseline_counts, _ = np.histogram(baseline_values, bins=edges)
    current_counts, _ = np.histogram(current_values, bins=edges)
    baseline_dist = np.clip(baseline_counts / max(baseline_counts.sum(), 1), 0.0001, None)
    current_dist = np.clip(current_counts / max(current_counts.sum(), 1), 0.0001, None)
    return float(np.sum((current_dist - baseline_dist) * np.log(current_dist / baseline_dist)))


def run_data_drift_checks(
    feature_table: pd.DataFrame,
    config: MonitoringConfig,
) -> pd.DataFrame:
    """Run simple numeric/boolean drift checks."""
    baseline, current = split_baseline_current(feature_table, config.baseline_fraction)
    excluded_columns = {
        "transaction_id",
        "account_id",
        "customer_id",
        "beneficiary_id",
        "device_id",
        "suspicious_pattern",
        "transaction_timestamp",
        "currency",
        "transaction_type",
        "merchant_category",
        "origin_country",
        "destination_country",
        "channel",
    }
    feature_columns = [
        column
        for column in feature_table.columns
        if column not in excluded_columns
        and (
            pd.api.types.is_numeric_dtype(feature_table[column])
            or pd.api.types.is_bool_dtype(feature_table[column])
        )
    ]
    rows: list[dict[str, Any]] = []
    for column in feature_columns:
        baseline_values = pd.to_numeric(baseline[column], errors="coerce")
        current_values = pd.to_numeric(current[column], errors="coerce")
        baseline_mean = float(baseline_values.mean()) if not baseline_values.empty else 0.0
        current_mean = float(current_values.mean()) if not current_values.empty else 0.0
        mean_difference = current_mean - baseline_mean
        denominator = abs(baseline_mean) if abs(baseline_mean) > 1e-9 else 1.0
        percent_change = mean_difference / denominator
        baseline_missing_rate = float(baseline[column].isna().mean())
        current_missing_rate = float(current[column].isna().mean())
        drift_score = _psi_score(baseline_values, current_values)
        drift_flag = (
            abs(percent_change) >= config.drift_percent_change_threshold
            or abs(current_missing_rate - baseline_missing_rate)
            >= config.missing_rate_change_threshold
            or drift_score >= config.drift_score_threshold
        )
        rows.append(
            {
                "feature_name": column,
                "baseline_mean": baseline_mean,
                "current_mean": current_mean,
                "mean_difference": mean_difference,
                "percent_change": percent_change,
                "baseline_missing_rate": baseline_missing_rate,
                "current_missing_rate": current_missing_rate,
                "drift_score": drift_score,
                "drift_flag": bool(drift_flag),
            }
        )
    return pd.DataFrame(rows)
