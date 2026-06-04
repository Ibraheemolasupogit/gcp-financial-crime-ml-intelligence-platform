"""Feature engineering pipeline for synthetic financial crime datasets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from financial_crime_ml.features.account_features import add_account_customer_features
from financial_crime_ml.features.aml_typology_features import add_aml_typology_features
from financial_crime_ml.features.beneficiary_features import add_beneficiary_features
from financial_crime_ml.features.device_features import add_device_features
from financial_crime_ml.features.transaction_features import (
    add_transaction_features,
    add_velocity_features,
)
from financial_crime_ml.ingestion.load_data import DEFAULT_INPUT_PATH, REPO_ROOT, load_all_datasets
from financial_crime_ml.ingestion.validate_schema import (
    validate_all_schemas,
    validate_relationships,
)

DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "feature_config.yaml"
DEFAULT_FEATURE_OUTPUT_PATH = REPO_ROOT / "data" / "processed" / "transaction_features.csv"
DEFAULT_SUMMARY_OUTPUT_PATH = REPO_ROOT / "outputs" / "sample" / "feature_summary.json"

TYPOLOGY_FLAG_COLUMNS = [
    "structuring_pattern_flag",
    "rapid_movement_flag",
    "high_risk_jurisdiction_flag",
    "mule_activity_indicator",
    "account_takeover_indicator",
    "new_beneficiary_high_value_flag",
    "round_amount_repetition_flag",
]


@dataclass(frozen=True)
class FeatureConfig:
    """Configuration for deterministic feature engineering."""

    high_value_transaction_threshold: float = 5000
    round_amount_multiple: int = 100
    high_velocity_1h_threshold: int = 3
    high_velocity_24h_threshold: int = 8
    high_risk_countries: tuple[str, ...] = ("AE", "NG", "PA", "TR")
    new_beneficiary_days: int = 30
    rapid_movement_hours: int = 2
    structuring_amount_threshold: float = 10000
    structuring_count_threshold: int = 3
    transaction_features_path: Path = DEFAULT_FEATURE_OUTPUT_PATH
    feature_summary_path: Path = DEFAULT_SUMMARY_OUTPUT_PATH


def _resolve_repo_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def load_feature_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> FeatureConfig:
    """Load feature engineering thresholds from YAML."""
    resolved_path = _resolve_repo_path(config_path)
    raw_config = yaml.safe_load(resolved_path.read_text(encoding="utf-8")) or {}
    thresholds = raw_config.get("thresholds", {})
    outputs = raw_config.get("outputs", {})

    return FeatureConfig(
        high_value_transaction_threshold=float(
            thresholds.get("high_value_transaction_threshold", 5000)
        ),
        round_amount_multiple=int(thresholds.get("round_amount_multiple", 100)),
        high_velocity_1h_threshold=int(thresholds.get("high_velocity_1h_threshold", 3)),
        high_velocity_24h_threshold=int(thresholds.get("high_velocity_24h_threshold", 8)),
        high_risk_countries=tuple(thresholds.get("high_risk_countries", ["AE", "NG", "PA", "TR"])),
        new_beneficiary_days=int(thresholds.get("new_beneficiary_days", 30)),
        rapid_movement_hours=int(thresholds.get("rapid_movement_hours", 2)),
        structuring_amount_threshold=float(thresholds.get("structuring_amount_threshold", 10000)),
        structuring_count_threshold=int(thresholds.get("structuring_count_threshold", 3)),
        transaction_features_path=_resolve_repo_path(
            outputs.get("transaction_features_path", DEFAULT_FEATURE_OUTPUT_PATH)
        ),
        feature_summary_path=_resolve_repo_path(
            outputs.get("feature_summary_path", DEFAULT_SUMMARY_OUTPUT_PATH)
        ),
    )


def _validate_loaded_datasets(datasets: dict[str, pd.DataFrame]) -> None:
    issues = [*validate_all_schemas(datasets), *validate_relationships(datasets)]
    if issues:
        issue_messages = "; ".join(issue.message for issue in issues[:5])
        raise ValueError(
            f"Input datasets failed validation before feature engineering: {issue_messages}"
        )


def build_feature_table(
    datasets: dict[str, pd.DataFrame],
    config: FeatureConfig | None = None,
) -> pd.DataFrame:
    """Build the transaction-level feature table."""
    resolved_config = config or load_feature_config()
    high_risk_countries = set(resolved_config.high_risk_countries)

    features = add_transaction_features(
        datasets["transactions"],
        high_value_threshold=resolved_config.high_value_transaction_threshold,
        round_amount_multiple=resolved_config.round_amount_multiple,
        high_risk_countries=high_risk_countries,
    )
    features = add_velocity_features(
        features,
        high_velocity_1h_threshold=resolved_config.high_velocity_1h_threshold,
        high_velocity_24h_threshold=resolved_config.high_velocity_24h_threshold,
        rapid_movement_hours=resolved_config.rapid_movement_hours,
    )
    features = add_account_customer_features(features, datasets["accounts"], datasets["customers"])
    features = add_beneficiary_features(
        features,
        datasets["beneficiaries"],
        high_risk_countries=high_risk_countries,
        new_beneficiary_days=resolved_config.new_beneficiary_days,
    )
    features = add_device_features(features, datasets["devices"])
    features = add_aml_typology_features(
        features,
        structuring_amount_threshold=resolved_config.structuring_amount_threshold,
        structuring_count_threshold=resolved_config.structuring_count_threshold,
    )

    feature_columns = _ordered_feature_columns(features)
    return features[feature_columns]


def _ordered_feature_columns(features: pd.DataFrame) -> list[str]:
    identifier_columns = [
        "transaction_id",
        "account_id",
        "customer_id",
        "beneficiary_id",
        "device_id",
    ]
    helper_columns = ["is_suspicious", "suspicious_pattern"]
    excluded_raw_context = {
        "customer_type",
        "age_band_or_business_type",
        "customer_country",
        "customer_risk_band",
        "customer_onboarding_date",
        "kyc_status",
        "account_type",
        "open_date",
        "account_status",
        "base_currency",
        "branch_region",
        "beneficiary_country",
        "beneficiary_type",
        "beneficiary_first_seen_date",
        "beneficiary_risk_band",
        "device_type",
        "ip_country",
        "device_first_seen_date",
        "device_risk_band",
    }
    remaining_columns = [
        column
        for column in features.columns
        if column not in identifier_columns
        and column not in helper_columns
        and column not in excluded_raw_context
    ]
    return identifier_columns + helper_columns + remaining_columns


def create_feature_summary(feature_table: pd.DataFrame) -> dict[str, Any]:
    """Create a compact JSON-serialisable feature summary."""
    engineered_columns = [
        column
        for column in feature_table.columns
        if column
        not in {
            "transaction_id",
            "account_id",
            "customer_id",
            "beneficiary_id",
            "device_id",
            "is_suspicious",
            "suspicious_pattern",
        }
    ]
    suspicious_count = int(feature_table["is_suspicious"].sum())

    return {
        "number_of_rows": int(feature_table.shape[0]),
        "number_of_columns": int(feature_table.shape[1]),
        "feature_column_names": engineered_columns,
        "typology_flag_counts": {
            column: int(feature_table[column].sum())
            for column in TYPOLOGY_FLAG_COLUMNS
            if column in feature_table.columns
        },
        "missing_value_counts": {
            column: int(feature_table[column].isna().sum()) for column in engineered_columns
        },
        "suspicious_transaction_count": suspicious_count,
        "suspicious_transaction_rate": float(suspicious_count / len(feature_table))
        if len(feature_table)
        else 0.0,
    }


def write_feature_outputs(
    feature_table: pd.DataFrame,
    config: FeatureConfig,
) -> tuple[Path, Path, dict[str, Any]]:
    """Write feature table and summary outputs."""
    config.transaction_features_path.parent.mkdir(parents=True, exist_ok=True)
    config.feature_summary_path.parent.mkdir(parents=True, exist_ok=True)

    feature_table.to_csv(config.transaction_features_path, index=False)
    summary = create_feature_summary(feature_table)
    config.feature_summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return config.transaction_features_path, config.feature_summary_path, summary


def run_feature_pipeline(
    input_path: str | Path = DEFAULT_INPUT_PATH,
    config: FeatureConfig | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load validated data, build features, and write feature outputs."""
    resolved_config = config or load_feature_config()
    datasets = load_all_datasets(input_path)
    _validate_loaded_datasets(datasets)
    feature_table = build_feature_table(datasets, resolved_config)
    _, _, summary = write_feature_outputs(feature_table, resolved_config)
    return feature_table, summary
