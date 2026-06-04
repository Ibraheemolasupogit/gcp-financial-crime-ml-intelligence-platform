from pathlib import Path

import pandas as pd

from financial_crime_ml.data_generation.generator import DataGenerationConfig, generate_all_datasets
from financial_crime_ml.ingestion.data_quality import generate_data_quality_report
from financial_crime_ml.ingestion.load_data import DATASET_FILES, load_all_datasets
from financial_crime_ml.ingestion.validate_schema import (
    validate_all_schemas,
    validate_dataset_schema,
    validate_relationships,
)


def _generate_test_data(output_path: Path) -> dict[str, pd.DataFrame]:
    generate_all_datasets(
        DataGenerationConfig(
            random_seed=11,
            number_of_customers=50,
            number_of_accounts=70,
            number_of_transactions=500,
            number_of_beneficiaries=80,
            number_of_devices=60,
            output_path=output_path,
        )
    )
    return load_all_datasets(output_path)


def test_all_datasets_can_be_loaded(tmp_path: Path) -> None:
    datasets = _generate_test_data(tmp_path)

    assert set(datasets) == set(DATASET_FILES)
    assert all(not dataset.empty for dataset in datasets.values())


def test_required_schema_checks_pass_for_generated_data(tmp_path: Path) -> None:
    datasets = _generate_test_data(tmp_path)

    assert validate_all_schemas(datasets) == []
    assert validate_relationships(datasets) == []


def test_missing_required_columns_are_detected(tmp_path: Path) -> None:
    datasets = _generate_test_data(tmp_path)
    broken_customers = datasets["customers"].drop(columns=["customer_id"])

    issues = validate_dataset_schema("customers", broken_customers)

    assert any(issue.check == "required_column" for issue in issues)


def test_duplicate_primary_keys_are_detected(tmp_path: Path) -> None:
    datasets = _generate_test_data(tmp_path)
    broken_accounts = datasets["accounts"].copy()
    broken_accounts.loc[1, "account_id"] = broken_accounts.loc[0, "account_id"]

    issues = validate_dataset_schema("accounts", broken_accounts)

    assert any(issue.check == "duplicate_primary_key" for issue in issues)


def test_invalid_foreign_keys_are_detected(tmp_path: Path) -> None:
    datasets = _generate_test_data(tmp_path)
    datasets["transactions"] = datasets["transactions"].copy()
    datasets["transactions"].loc[0, "account_id"] = "ACCT_DOES_NOT_EXIST"

    issues = validate_relationships(datasets)

    assert any(issue.check == "invalid_foreign_key" for issue in issues)


def test_data_quality_report_can_be_generated(tmp_path: Path) -> None:
    datasets = _generate_test_data(tmp_path / "data")
    report_path = tmp_path / "report" / "data_quality_report.json"

    report = generate_data_quality_report(datasets, report_path)

    assert report_path.exists()
    assert report["overall_status"] == "passed"
    assert "row_counts" in report
    assert "validation_issues" in report


def test_validation_output_contains_overall_status(tmp_path: Path) -> None:
    datasets = _generate_test_data(tmp_path)

    report = generate_data_quality_report(datasets, tmp_path / "quality.json")

    assert report["overall_status"] in {"passed", "failed"}
