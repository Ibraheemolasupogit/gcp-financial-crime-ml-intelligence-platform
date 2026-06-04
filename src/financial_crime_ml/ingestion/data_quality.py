"""Build data quality reports for synthetic datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from financial_crime_ml.ingestion.load_data import DEFAULT_INPUT_PATH, REPO_ROOT, load_all_datasets
from financial_crime_ml.ingestion.schemas import SCHEMAS
from financial_crime_ml.ingestion.validate_schema import (
    ValidationIssue,
    validate_all_schemas,
    validate_relationships,
)

DEFAULT_REPORT_PATH = REPO_ROOT / "outputs" / "sample" / "data_quality_report.json"


def _duplicate_primary_key_counts(datasets: dict[str, pd.DataFrame]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for dataset_name, dataset in datasets.items():
        schema = SCHEMAS.get(dataset_name)
        if schema is None or schema.primary_key not in dataset.columns:
            counts[dataset_name] = 0
            continue
        counts[dataset_name] = int(dataset[schema.primary_key].duplicated().sum())
    return counts


def _issue_dicts(issues: list[ValidationIssue]) -> list[dict[str, str | None]]:
    return [issue.to_dict() for issue in issues]


def generate_data_quality_report(
    datasets: dict[str, pd.DataFrame],
    report_path: str | Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    """Validate datasets and write a JSON data quality report."""
    schema_issues = validate_all_schemas(datasets)
    relationship_issues = validate_relationships(datasets)
    validation_issues = [*schema_issues, *relationship_issues]

    report = {
        "overall_status": "passed" if not validation_issues else "failed",
        "schema_validation_status": "passed" if not schema_issues else "failed",
        "relationship_validation_status": "passed" if not relationship_issues else "failed",
        "row_counts": {name: int(dataset.shape[0]) for name, dataset in datasets.items()},
        "column_counts": {name: int(dataset.shape[1]) for name, dataset in datasets.items()},
        "missing_value_counts": {
            name: {column: int(count) for column, count in dataset.isna().sum().items()}
            for name, dataset in datasets.items()
        },
        "duplicate_primary_key_counts": _duplicate_primary_key_counts(datasets),
        "validation_issues": _issue_dicts(validation_issues),
    }

    output_path = Path(report_path)
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


def run_data_validation(
    input_path: str | Path = DEFAULT_INPUT_PATH,
    report_path: str | Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    """Load all datasets, validate them, and write the quality report."""
    datasets = load_all_datasets(input_path)
    return generate_data_quality_report(datasets, report_path)
