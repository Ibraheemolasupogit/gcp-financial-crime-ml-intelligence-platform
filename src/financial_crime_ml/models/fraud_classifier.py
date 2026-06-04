"""Train a simple supervised fraud classifier."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from financial_crime_ml.models.model_utils import (
    DEFAULT_MODEL_CONFIG_PATH,
    load_feature_table,
    load_yaml_config,
    resolve_repo_path,
)


@dataclass(frozen=True)
class FraudModelConfig:
    """Configuration for the baseline fraud classifier."""

    random_seed: int
    test_size: float
    target_column: str
    model_type: str
    prediction_threshold: float
    input_path: Path
    metrics_output_path: Path
    predictions_output_path: Path
    model_card_output_path: Path
    excluded_columns: tuple[str, ...]


def load_fraud_model_config(
    config_path: str | Path = DEFAULT_MODEL_CONFIG_PATH,
) -> FraudModelConfig:
    """Load fraud classifier settings."""
    raw_config = load_yaml_config(config_path).get("fraud_classifier", {})
    return FraudModelConfig(
        random_seed=int(raw_config.get("random_seed", 42)),
        test_size=float(raw_config.get("test_size", 0.2)),
        target_column=str(raw_config.get("target_column", "is_suspicious")),
        model_type=str(raw_config.get("model_type", "logistic_regression")),
        prediction_threshold=float(raw_config.get("prediction_threshold", 0.5)),
        input_path=resolve_repo_path(
            raw_config.get("input_path", "data/processed/transaction_features.csv")
        ),
        metrics_output_path=resolve_repo_path(
            raw_config.get("metrics_output_path", "outputs/sample/model_metrics.json")
        ),
        predictions_output_path=resolve_repo_path(
            raw_config.get("predictions_output_path", "outputs/sample/fraud_predictions.csv")
        ),
        model_card_output_path=resolve_repo_path(
            raw_config.get("model_card_output_path", "reports/sample/model_card.md")
        ),
        excluded_columns=tuple(raw_config.get("excluded_columns", [])),
    )


def select_model_features(feature_table: pd.DataFrame, config: FraudModelConfig) -> list[str]:
    """Select numeric and boolean columns for model training."""
    excluded = set(config.excluded_columns) | {config.target_column}
    candidates = feature_table.drop(
        columns=[column for column in excluded if column in feature_table]
    )
    return [
        column
        for column in candidates.columns
        if pd.api.types.is_numeric_dtype(candidates[column])
        or pd.api.types.is_bool_dtype(candidates[column])
    ]


def _build_model(config: FraudModelConfig) -> Pipeline:
    if config.model_type != "logistic_regression":
        raise ValueError("Milestone 5 supports only logistic_regression.")
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=config.random_seed,
                ),
            ),
        ]
    )


def _metric_payload(
    y_test: pd.Series,
    probabilities: pd.Series,
    predictions: pd.Series,
    config: FraudModelConfig,
    feature_columns: list[str],
    training_row_count: int,
) -> dict[str, Any]:
    try:
        roc_auc = float(roc_auc_score(y_test, probabilities))
    except ValueError:
        roc_auc = None

    return {
        "model_name": "LogisticRegression",
        "target_column": config.target_column,
        "feature_count": len(feature_columns),
        "training_row_count": int(training_row_count),
        "test_row_count": int(len(y_test)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1_score": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": roc_auc,
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
        "positive_class_rate": float(y_test.mean()),
        "threshold_used": config.prediction_threshold,
        "notes": [
            "Baseline supervised classifier trained on synthetic engineered features.",
            "Synthetic labels are for portfolio demonstration only.",
            "This is not a production deployment or live financial crime control.",
        ],
    }


def train_fraud_classifier(
    config: FraudModelConfig | None = None,
) -> tuple[pd.DataFrame, dict[str, Any], list[str]]:
    """Train the baseline classifier and write metrics/prediction outputs."""
    resolved_config = config or load_fraud_model_config()
    feature_table = load_feature_table(resolved_config.input_path)
    feature_columns = select_model_features(feature_table, resolved_config)
    if not feature_columns:
        raise ValueError("No numeric or boolean feature columns were available for training.")

    x = feature_table[feature_columns].fillna(0)
    y = feature_table[resolved_config.target_column].astype(int)
    stratify = y if y.nunique() > 1 else None
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=resolved_config.test_size,
        random_state=resolved_config.random_seed,
        stratify=stratify,
    )

    model = _build_model(resolved_config)
    model.fit(x_train, y_train)

    probabilities = pd.Series(model.predict_proba(x_test)[:, 1], index=x_test.index)
    predictions = (probabilities >= resolved_config.prediction_threshold).astype(int)
    metrics = _metric_payload(
        y_test,
        probabilities,
        predictions,
        resolved_config,
        feature_columns,
        training_row_count=len(x_train),
    )

    prediction_columns = [
        column
        for column in [
            "transaction_id",
            "account_id",
            "customer_id",
            "suspicious_pattern",
            resolved_config.target_column,
        ]
        if column in feature_table.columns
    ]
    prediction_output = feature_table.loc[x_test.index, prediction_columns].copy()
    prediction_output["fraud_probability"] = probabilities
    prediction_output["fraud_prediction"] = predictions
    prediction_output = prediction_output.sort_values("fraud_probability", ascending=False)

    resolved_config.metrics_output_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_config.predictions_output_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_config.metrics_output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    prediction_output.to_csv(resolved_config.predictions_output_path, index=False)

    return prediction_output, metrics, feature_columns
