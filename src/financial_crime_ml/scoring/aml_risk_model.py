"""Configuration for deterministic AML risk scoring."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from financial_crime_ml.ingestion.load_data import REPO_ROOT
from financial_crime_ml.models.model_utils import load_yaml_config, resolve_repo_path

DEFAULT_RISK_CONFIG_PATH = REPO_ROOT / "configs" / "risk_scoring.yaml"


@dataclass(frozen=True)
class AMLRiskConfig:
    """AML risk scoring configuration."""

    output_path: Path
    prioritised_alerts_output_path: Path
    severity_bands: dict[str, dict[str, int]]
    scoring_weights: dict[str, int]
    recommended_action_thresholds: dict[str, int]


def load_aml_risk_config(config_path: str | Path = DEFAULT_RISK_CONFIG_PATH) -> AMLRiskConfig:
    """Load AML risk scoring settings."""
    raw_config: dict[str, Any] = load_yaml_config(config_path).get("aml_risk_scoring", {})
    return AMLRiskConfig(
        output_path=resolve_repo_path(
            raw_config.get("output_path", "outputs/sample/aml_risk_scores.csv")
        ),
        prioritised_alerts_output_path=resolve_repo_path(
            raw_config.get(
                "prioritised_alerts_output_path",
                "outputs/sample/prioritised_alerts.csv",
            )
        ),
        severity_bands=raw_config.get("severity_bands", {}),
        scoring_weights=raw_config.get("scoring_weights", {}),
        recommended_action_thresholds=raw_config.get("recommended_action_thresholds", {}),
    )
