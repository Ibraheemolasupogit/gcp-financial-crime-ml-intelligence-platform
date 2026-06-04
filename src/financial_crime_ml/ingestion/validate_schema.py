"""Schema and relationship validation for synthetic datasets."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass

import pandas as pd
from pandas.api.types import is_bool_dtype

from financial_crime_ml.ingestion.schemas import SCHEMAS, ColumnSchema


@dataclass(frozen=True)
class ValidationIssue:
    """A single validation issue."""

    dataset: str
    check: str
    message: str
    column: str | None = None
    severity: str = "error"

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


RELATIONSHIPS = [
    ("accounts", "customer_id", "customers", "customer_id"),
    ("transactions", "account_id", "accounts", "account_id"),
    ("transactions", "beneficiary_id", "beneficiaries", "beneficiary_id"),
    ("transactions", "device_id", "devices", "device_id"),
    ("alerts", "transaction_id", "transactions", "transaction_id"),
    ("alerts", "account_id", "accounts", "account_id"),
    ("case_notes", "alert_id", "alerts", "alert_id"),
]


def _required_value_missing(series: pd.Series) -> int:
    missing = series.isna()
    if series.dtype == object:
        missing = missing | series.astype(str).str.strip().eq("")
    return int(missing.sum())


def _invalid_dtype_count(series: pd.Series, column_schema: ColumnSchema) -> int:
    non_missing = series.dropna()
    if column_schema.dtype == "string":
        return 0
    if column_schema.dtype == "numeric":
        return int(pd.to_numeric(non_missing, errors="coerce").isna().sum())
    if column_schema.dtype == "datetime":
        return int(pd.to_datetime(non_missing, errors="coerce").isna().sum())
    if column_schema.dtype == "boolean":
        if is_bool_dtype(series):
            return 0
        normalized = non_missing.astype(str).str.lower()
        return int(~normalized.isin({"true", "false", "1", "0"}).sum())
    return 0


def _invalid_category_values(series: pd.Series, allowed_values: Iterable[object]) -> list[object]:
    observed = set(series.dropna().unique())
    return sorted(observed - set(allowed_values), key=str)


def validate_dataset_schema(dataset_name: str, dataset: pd.DataFrame) -> list[ValidationIssue]:
    """Validate one dataset against its explicit schema."""
    if dataset_name not in SCHEMAS:
        return [
            ValidationIssue(
                dataset=dataset_name,
                check="schema_known",
                message=f"No schema is defined for dataset '{dataset_name}'.",
            )
        ]

    issues: list[ValidationIssue] = []
    schema = SCHEMAS[dataset_name]

    for column_name, column_schema in schema.columns.items():
        if column_name not in dataset.columns:
            issues.append(
                ValidationIssue(
                    dataset=dataset_name,
                    column=column_name,
                    check="required_column",
                    message=f"Required column '{column_name}' is missing.",
                )
            )
            continue

        if column_schema.required:
            missing_count = _required_value_missing(dataset[column_name])
            if missing_count:
                issues.append(
                    ValidationIssue(
                        dataset=dataset_name,
                        column=column_name,
                        check="missing_required_values",
                        message=(
                            f"Column '{column_name}' contains {missing_count} missing "
                            "required values."
                        ),
                    )
                )

        invalid_dtype_count = _invalid_dtype_count(dataset[column_name], column_schema)
        if invalid_dtype_count:
            issues.append(
                ValidationIssue(
                    dataset=dataset_name,
                    column=column_name,
                    check="invalid_dtype",
                    message=(
                        f"Column '{column_name}' contains {invalid_dtype_count} values "
                        f"that are not valid {column_schema.dtype} values."
                    ),
                )
            )

        if column_schema.allowed_values is not None:
            invalid_values = _invalid_category_values(
                dataset[column_name],
                column_schema.allowed_values,
            )
            if invalid_values:
                issues.append(
                    ValidationIssue(
                        dataset=dataset_name,
                        column=column_name,
                        check="invalid_category",
                        message=(
                            f"Column '{column_name}' contains invalid values: {invalid_values}."
                        ),
                    )
                )

        if column_schema.min_value is not None:
            numeric_values = pd.to_numeric(dataset[column_name], errors="coerce")
            invalid_range_count = int((numeric_values < column_schema.min_value).sum())
            if invalid_range_count:
                issues.append(
                    ValidationIssue(
                        dataset=dataset_name,
                        column=column_name,
                        check="invalid_numeric_range",
                        message=(
                            f"Column '{column_name}' contains {invalid_range_count} values "
                            f"below {column_schema.min_value}."
                        ),
                    )
                )

    for column_name in schema.unique_columns:
        if column_name in dataset.columns:
            duplicate_count = int(dataset[column_name].duplicated().sum())
            if duplicate_count:
                issues.append(
                    ValidationIssue(
                        dataset=dataset_name,
                        column=column_name,
                        check="duplicate_primary_key",
                        message=f"Column '{column_name}' contains {duplicate_count} duplicates.",
                    )
                )

    return issues


def validate_all_schemas(datasets: dict[str, pd.DataFrame]) -> list[ValidationIssue]:
    """Validate all loaded datasets against their schemas."""
    issues: list[ValidationIssue] = []
    for dataset_name in SCHEMAS:
        if dataset_name not in datasets:
            issues.append(
                ValidationIssue(
                    dataset=dataset_name,
                    check="dataset_loaded",
                    message=f"Required dataset '{dataset_name}' was not loaded.",
                )
            )
            continue
        issues.extend(validate_dataset_schema(dataset_name, datasets[dataset_name]))

    return issues


def validate_relationships(datasets: dict[str, pd.DataFrame]) -> list[ValidationIssue]:
    """Validate foreign-key style relationships across datasets."""
    issues: list[ValidationIssue] = []
    for child_dataset, child_column, parent_dataset, parent_column in RELATIONSHIPS:
        if child_dataset not in datasets or parent_dataset not in datasets:
            issues.append(
                ValidationIssue(
                    dataset=child_dataset,
                    column=child_column,
                    check="relationship_dataset_available",
                    message=(
                        f"Cannot validate relationship {child_dataset}.{child_column} -> "
                        f"{parent_dataset}.{parent_column} because a dataset is missing."
                    ),
                )
            )
            continue

        child = datasets[child_dataset]
        parent = datasets[parent_dataset]
        if child_column not in child.columns or parent_column not in parent.columns:
            issues.append(
                ValidationIssue(
                    dataset=child_dataset,
                    column=child_column,
                    check="relationship_column_available",
                    message=(
                        f"Cannot validate relationship {child_dataset}.{child_column} -> "
                        f"{parent_dataset}.{parent_column} because a column is missing."
                    ),
                )
            )
            continue

        invalid_mask = ~child[child_column].isin(parent[parent_column])
        invalid_count = int(invalid_mask.sum())
        if invalid_count:
            issues.append(
                ValidationIssue(
                    dataset=child_dataset,
                    column=child_column,
                    check="invalid_foreign_key",
                    message=(
                        f"{invalid_count} values in {child_dataset}.{child_column} do not "
                        f"exist in {parent_dataset}.{parent_column}."
                    ),
                )
            )

    return issues
