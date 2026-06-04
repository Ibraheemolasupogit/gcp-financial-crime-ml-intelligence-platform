"""Unsupervised anomaly detection for engineered transaction features."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from financial_crime_ml.models.model_utils import (
    DEFAULT_MODEL_CONFIG_PATH,
    load_feature_table,
    load_yaml_config,
    resolve_repo_path,
)


@dataclass(frozen=True)
class AnomalyDetectionConfig:
    """Configuration for the IsolationForest anomaly workflow."""

    anomaly_model_type: str
    contamination: float
    random_seed: int
    input_path: Path
    anomaly_scores_output_path: Path
    high_risk_anomalies_output_path: Path
    anomaly_summary_output_path: Path
    anomaly_report_output_path: Path
    max_high_risk_anomalies: int
    excluded_columns: tuple[str, ...]


def load_anomaly_detection_config(
    config_path: str | Path = DEFAULT_MODEL_CONFIG_PATH,
) -> AnomalyDetectionConfig:
    """Load anomaly detection settings."""
    raw_config = load_yaml_config(config_path).get("anomaly_detection", {})
    return AnomalyDetectionConfig(
        anomaly_model_type=str(raw_config.get("anomaly_model_type", "isolation_forest")),
        contamination=float(raw_config.get("contamination", 0.08)),
        random_seed=int(raw_config.get("random_seed", 42)),
        input_path=resolve_repo_path(
            raw_config.get("input_path", "data/processed/transaction_features.csv")
        ),
        anomaly_scores_output_path=resolve_repo_path(
            raw_config.get("anomaly_scores_output_path", "outputs/sample/anomaly_scores.csv")
        ),
        high_risk_anomalies_output_path=resolve_repo_path(
            raw_config.get(
                "high_risk_anomalies_output_path",
                "outputs/sample/high_risk_anomalies.csv",
            )
        ),
        anomaly_summary_output_path=resolve_repo_path(
            raw_config.get("anomaly_summary_output_path", "outputs/sample/anomaly_summary.json")
        ),
        anomaly_report_output_path=resolve_repo_path(
            raw_config.get(
                "anomaly_report_output_path",
                "reports/sample/anomaly_detection_report.md",
            )
        ),
        max_high_risk_anomalies=int(raw_config.get("max_high_risk_anomalies", 100)),
        excluded_columns=tuple(raw_config.get("excluded_columns", [])),
    )


def select_anomaly_features(
    feature_table: pd.DataFrame,
    config: AnomalyDetectionConfig,
) -> list[str]:
    """Select numeric and boolean features, excluding labels and identifiers."""
    excluded = set(config.excluded_columns)
    candidates = feature_table.drop(
        columns=[column for column in excluded if column in feature_table]
    )
    return [
        column
        for column in candidates.columns
        if pd.api.types.is_numeric_dtype(candidates[column])
        or pd.api.types.is_bool_dtype(candidates[column])
    ]


def _band_anomaly_scores(scores: pd.Series) -> pd.Series:
    thresholds = {
        "Critical": scores.quantile(0.99),
        "High": scores.quantile(0.95),
        "Medium": scores.quantile(0.85),
        "Low": scores.quantile(0.70),
    }

    def _band(score: float) -> str:
        if score >= thresholds["Critical"]:
            return "Critical"
        if score >= thresholds["High"]:
            return "High"
        if score >= thresholds["Medium"]:
            return "Medium"
        if score >= thresholds["Low"]:
            return "Low"
        return "Info"

    return scores.map(_band)


def _reason_codes(row: pd.Series) -> str:
    reason_map = {
        "is_high_value_transaction": "HIGH_VALUE_TRANSACTION",
        "high_velocity_flag": "HIGH_VELOCITY",
        "high_risk_jurisdiction_flag": "HIGH_RISK_JURISDICTION",
        "round_amount_repetition_flag": "ROUND_AMOUNT_PATTERN",
        "new_beneficiary_high_value_flag": "NEW_BENEFICIARY_HIGH_VALUE",
        "rapid_movement_flag": "RAPID_MOVEMENT",
        "account_takeover_indicator": "ACCOUNT_TAKEOVER_SIGNAL",
        "mule_activity_indicator": "MULE_ACTIVITY_SIGNAL",
        "device_risk_band_encoded": "DEVICE_RISK_SIGNAL",
        "is_cross_border_transaction": "CROSS_BORDER_TRANSACTION",
    }
    reasons: list[str] = []
    for column, code in reason_map.items():
        value = row.get(column, 0)
        if column == "device_risk_band_encoded":
            if float(value) >= 3:
                reasons.append(code)
        elif int(value) == 1:
            reasons.append(code)
    return "; ".join(reasons[:5]) if reasons else "NO_DOMINANT_REASON"


def run_anomaly_detector(
    config: AnomalyDetectionConfig | None = None,
) -> tuple[pd.DataFrame, list[str]]:
    """Train IsolationForest and return transaction-level anomaly scores."""
    resolved_config = config or load_anomaly_detection_config()
    if resolved_config.anomaly_model_type != "isolation_forest":
        raise ValueError("Milestone 6 supports only isolation_forest anomaly detection.")

    feature_table = load_feature_table(resolved_config.input_path)
    feature_columns = select_anomaly_features(feature_table, resolved_config)
    if "is_suspicious" in feature_columns:
        raise ValueError("is_suspicious must not be used as an anomaly training feature.")
    if not feature_columns:
        raise ValueError(
            "No numeric or boolean feature columns were available for anomaly detection."
        )

    x = feature_table[feature_columns].fillna(0)
    scaled_x = StandardScaler().fit_transform(x)
    model = IsolationForest(
        contamination=resolved_config.contamination,
        random_state=resolved_config.random_seed,
        n_estimators=100,
    )
    model.fit(scaled_x)

    raw_scores = -model.score_samples(scaled_x)
    anomaly_score = pd.Series(raw_scores, index=feature_table.index)
    anomaly_score = 100 * (anomaly_score - anomaly_score.min()) / np.ptp(anomaly_score)
    is_anomaly = model.predict(scaled_x) == -1

    output_columns = [
        column
        for column in [
            "transaction_id",
            "account_id",
            "customer_id",
            "is_suspicious",
            "suspicious_pattern",
        ]
        if column in feature_table.columns
    ]
    output = feature_table[output_columns].copy()
    output["anomaly_score"] = anomaly_score.round(4)
    output["is_anomaly"] = is_anomaly
    output["anomaly_rank"] = (
        output["anomaly_score"].rank(ascending=False, method="first").astype(int)
    )
    output["anomaly_band"] = _band_anomaly_scores(output["anomaly_score"])
    output["top_anomaly_reasons"] = feature_table.apply(_reason_codes, axis=1)
    output = output.sort_values("anomaly_rank").reset_index(drop=True)

    return output, feature_columns
