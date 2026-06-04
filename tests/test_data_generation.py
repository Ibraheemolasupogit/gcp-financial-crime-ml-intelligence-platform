from pathlib import Path

import pandas as pd

from financial_crime_ml.data_generation.generator import (
    DataGenerationConfig,
    generate_all_datasets,
    generate_datasets,
)

EXPECTED_COLUMNS = {
    "customers": {
        "customer_id",
        "customer_type",
        "age_band_or_business_type",
        "country",
        "risk_band",
        "onboarding_date",
        "kyc_status",
    },
    "accounts": {
        "account_id",
        "customer_id",
        "account_type",
        "open_date",
        "account_status",
        "base_currency",
        "branch_region",
    },
    "transactions": {
        "transaction_id",
        "account_id",
        "beneficiary_id",
        "device_id",
        "transaction_timestamp",
        "amount",
        "currency",
        "transaction_type",
        "merchant_category",
        "origin_country",
        "destination_country",
        "channel",
        "is_suspicious",
        "suspicious_pattern",
    },
    "beneficiaries": {
        "beneficiary_id",
        "beneficiary_country",
        "beneficiary_type",
        "first_seen_date",
        "risk_band",
    },
    "devices": {
        "device_id",
        "device_type",
        "ip_country",
        "first_seen_date",
        "device_risk_band",
    },
    "alerts": {
        "alert_id",
        "transaction_id",
        "account_id",
        "alert_type",
        "alert_severity",
        "alert_status",
        "alert_timestamp",
        "alert_reason",
    },
    "case_notes": {
        "case_note_id",
        "alert_id",
        "note_timestamp",
        "note_text",
        "typology_label",
    },
}


def _small_config(output_path: Path) -> DataGenerationConfig:
    return DataGenerationConfig(
        random_seed=7,
        number_of_customers=50,
        number_of_accounts=70,
        number_of_transactions=500,
        number_of_beneficiaries=80,
        number_of_devices=60,
        output_path=output_path,
    )


def test_all_expected_csv_files_are_generated(tmp_path: Path) -> None:
    written_files = generate_all_datasets(_small_config(tmp_path))

    assert set(written_files) == set(EXPECTED_COLUMNS)
    for file_path in written_files.values():
        assert file_path.exists()


def test_required_columns_exist(tmp_path: Path) -> None:
    written_files = generate_all_datasets(_small_config(tmp_path))

    for dataset_name, required_columns in EXPECTED_COLUMNS.items():
        dataset = pd.read_csv(written_files[dataset_name])
        assert required_columns.issubset(dataset.columns)


def test_unique_ids_and_valid_relationships(tmp_path: Path) -> None:
    datasets = generate_datasets(_small_config(tmp_path))

    assert datasets["customers"]["customer_id"].is_unique
    assert datasets["accounts"]["account_id"].is_unique
    assert datasets["transactions"]["transaction_id"].is_unique
    assert datasets["beneficiaries"]["beneficiary_id"].is_unique
    assert datasets["devices"]["device_id"].is_unique
    assert datasets["alerts"]["alert_id"].is_unique
    assert datasets["case_notes"]["case_note_id"].is_unique

    assert set(datasets["accounts"]["customer_id"]).issubset(datasets["customers"]["customer_id"])
    assert set(datasets["transactions"]["account_id"]).issubset(datasets["accounts"]["account_id"])
    assert set(datasets["transactions"]["beneficiary_id"]).issubset(
        datasets["beneficiaries"]["beneficiary_id"]
    )
    assert set(datasets["transactions"]["device_id"]).issubset(datasets["devices"]["device_id"])


def test_suspicious_transactions_alerts_and_case_notes_link_correctly(tmp_path: Path) -> None:
    datasets = generate_datasets(_small_config(tmp_path))

    assert datasets["transactions"]["is_suspicious"].any()
    assert set(datasets["alerts"]["transaction_id"]).issubset(
        datasets["transactions"]["transaction_id"]
    )
    assert set(datasets["alerts"]["account_id"]).issubset(datasets["accounts"]["account_id"])
    assert set(datasets["case_notes"]["alert_id"]).issubset(datasets["alerts"]["alert_id"])


def test_same_seed_produces_stable_output_shape(tmp_path: Path) -> None:
    first = generate_datasets(_small_config(tmp_path / "first"))
    second = generate_datasets(_small_config(tmp_path / "second"))

    assert {name: dataset.shape for name, dataset in first.items()} == {
        name: dataset.shape for name, dataset in second.items()
    }
