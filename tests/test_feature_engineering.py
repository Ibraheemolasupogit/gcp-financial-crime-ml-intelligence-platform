import json
from pathlib import Path

import pandas as pd

from financial_crime_ml.data_generation.generator import DataGenerationConfig, generate_all_datasets
from financial_crime_ml.features.feature_pipeline import (
    TYPOLOGY_FLAG_COLUMNS,
    FeatureConfig,
    build_feature_table,
    load_feature_config,
    run_feature_pipeline,
)
from financial_crime_ml.features.transaction_features import add_transaction_features
from financial_crime_ml.ingestion.load_data import load_all_datasets

REQUIRED_IDENTIFIER_COLUMNS = {
    "transaction_id",
    "account_id",
    "customer_id",
    "beneficiary_id",
    "device_id",
}

REQUIRED_ENGINEERED_COLUMNS = {
    "transaction_amount_log",
    "is_round_amount",
    "is_high_value_transaction",
    "is_cross_border_transaction",
    "is_high_risk_destination",
    "is_unusual_channel",
    "is_night_transaction",
    "transaction_hour",
    "transaction_day_of_week",
    "transaction_month",
    "amount_zscore_by_account",
    "transaction_count_by_account",
    "average_amount_by_account",
    "amount_vs_account_average_ratio",
    "transactions_last_1h",
    "transactions_last_24h",
    "transaction_amount_last_24h",
    "high_velocity_flag",
    "rapid_sequence_flag",
    "customer_risk_band_encoded",
    "account_age_days",
    "customer_tenure_days",
    "account_transaction_count",
    "account_total_transaction_amount",
    "account_average_transaction_amount",
    "account_suspicious_transaction_rate",
    "beneficiary_risk_band_encoded",
    "is_new_beneficiary",
    "beneficiary_country_risk_flag",
    "beneficiary_transaction_count",
    "beneficiary_total_amount",
    "device_risk_band_encoded",
    "device_country_mismatch_flag",
    "device_transaction_count",
    "shared_device_flag",
}


def _generate_test_datasets(output_path: Path) -> dict[str, pd.DataFrame]:
    generate_all_datasets(
        DataGenerationConfig(
            random_seed=19,
            number_of_customers=50,
            number_of_accounts=70,
            number_of_transactions=500,
            number_of_beneficiaries=80,
            number_of_devices=60,
            output_path=output_path,
        )
    )
    return load_all_datasets(output_path)


def _test_feature_config(tmp_path: Path) -> FeatureConfig:
    return FeatureConfig(
        transaction_features_path=tmp_path / "processed" / "transaction_features.csv",
        feature_summary_path=tmp_path / "outputs" / "feature_summary.json",
    )


def test_feature_pipeline_runs_successfully(tmp_path: Path) -> None:
    datasets = _generate_test_datasets(tmp_path / "data")

    feature_table = build_feature_table(datasets, _test_feature_config(tmp_path))

    assert not feature_table.empty


def test_transaction_features_csv_and_summary_are_created(tmp_path: Path) -> None:
    data_path = tmp_path / "data"
    _generate_test_datasets(data_path)
    config = _test_feature_config(tmp_path)

    _, summary = run_feature_pipeline(input_path=data_path, config=config)

    assert config.transaction_features_path.exists()
    assert config.feature_summary_path.exists()
    assert summary["number_of_rows"] == 500
    saved_summary = json.loads(config.feature_summary_path.read_text(encoding="utf-8"))
    assert saved_summary["number_of_rows"] == 500


def test_required_columns_and_typology_flags_exist(tmp_path: Path) -> None:
    datasets = _generate_test_datasets(tmp_path / "data")

    feature_table = build_feature_table(datasets, _test_feature_config(tmp_path))

    assert REQUIRED_IDENTIFIER_COLUMNS.issubset(feature_table.columns)
    assert REQUIRED_ENGINEERED_COLUMNS.issubset(feature_table.columns)
    assert set(TYPOLOGY_FLAG_COLUMNS).issubset(feature_table.columns)
    assert {"is_suspicious", "suspicious_pattern"}.issubset(feature_table.columns)


def test_no_row_count_mismatch_against_transactions(tmp_path: Path) -> None:
    datasets = _generate_test_datasets(tmp_path / "data")

    feature_table = build_feature_table(datasets, _test_feature_config(tmp_path))

    assert len(feature_table) == len(datasets["transactions"])


def test_feature_summary_json_contains_expected_fields(tmp_path: Path) -> None:
    data_path = tmp_path / "data"
    _generate_test_datasets(data_path)
    config = _test_feature_config(tmp_path)

    run_feature_pipeline(input_path=data_path, config=config)
    summary = json.loads(config.feature_summary_path.read_text(encoding="utf-8"))

    assert "feature_column_names" in summary
    assert "typology_flag_counts" in summary
    assert "suspicious_transaction_count" in summary
    assert "suspicious_transaction_rate" in summary


def test_threshold_config_can_be_loaded() -> None:
    config = load_feature_config()

    assert config.high_value_transaction_threshold > 0
    assert config.round_amount_multiple > 0
    assert config.high_risk_countries


def test_known_case_round_amount_and_high_value_flags() -> None:
    transactions = pd.DataFrame(
        {
            "transaction_id": ["TXN_TEST"],
            "account_id": ["ACCT_TEST"],
            "beneficiary_id": ["BEN_TEST"],
            "device_id": ["DEV_TEST"],
            "transaction_timestamp": ["2025-01-01T23:30:00"],
            "amount": [10000],
            "currency": ["GBP"],
            "transaction_type": ["bank_transfer"],
            "merchant_category": ["cash_services"],
            "origin_country": ["GB"],
            "destination_country": ["NG"],
            "channel": ["api"],
            "is_suspicious": [True],
            "suspicious_pattern": ["round_number_payments"],
        }
    )

    features = add_transaction_features(
        transactions,
        high_value_threshold=5000,
        round_amount_multiple=100,
        high_risk_countries={"NG"},
    )

    assert int(features.loc[0, "is_round_amount"]) == 1
    assert int(features.loc[0, "is_high_value_transaction"]) == 1
    assert int(features.loc[0, "is_high_risk_destination"]) == 1
