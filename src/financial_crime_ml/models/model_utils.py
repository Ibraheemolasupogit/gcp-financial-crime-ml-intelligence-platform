"""Shared model workflow helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from financial_crime_ml.ingestion.load_data import REPO_ROOT

DEFAULT_MODEL_CONFIG_PATH = REPO_ROOT / "configs" / "model_config.yaml"


def resolve_repo_path(path_value: str | Path) -> Path:
    """Resolve a path relative to the repository root when needed."""
    path = Path(path_value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def load_yaml_config(config_path: str | Path) -> dict[str, Any]:
    """Load a YAML configuration file."""
    resolved_path = resolve_repo_path(config_path)
    return yaml.safe_load(resolved_path.read_text(encoding="utf-8")) or {}


def load_feature_table(input_path: str | Path) -> pd.DataFrame:
    """Load the transaction-level feature table."""
    resolved_path = resolve_repo_path(input_path)
    if not resolved_path.exists():
        raise FileNotFoundError(
            f"Feature table is missing: {resolved_path}. "
            "Run `python scripts/build_features.py` first."
        )
    return pd.read_csv(resolved_path)
