"""Orchestrate synthetic financial crime dataset generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from financial_crime_ml.data_generation.synthetic_accounts import generate_accounts
from financial_crime_ml.data_generation.synthetic_alerts import generate_alerts
from financial_crime_ml.data_generation.synthetic_beneficiaries import generate_beneficiaries
from financial_crime_ml.data_generation.synthetic_case_notes import generate_case_notes
from financial_crime_ml.data_generation.synthetic_customers import generate_customers
from financial_crime_ml.data_generation.synthetic_devices import generate_devices
from financial_crime_ml.data_generation.synthetic_transactions import generate_transactions

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "pipeline_config.yaml"


@dataclass(frozen=True)
class DataGenerationConfig:
    """Configuration for generating sample synthetic datasets."""

    random_seed: int = 42
    number_of_customers: int = 500
    number_of_accounts: int = 700
    number_of_transactions: int = 5000
    number_of_beneficiaries: int = 800
    number_of_devices: int = 600
    output_path: Path = REPO_ROOT / "data" / "sample"


def load_generation_config(config_path: Path = DEFAULT_CONFIG_PATH) -> DataGenerationConfig:
    """Load generation settings from the pipeline configuration file."""
    with config_path.open("r", encoding="utf-8") as config_file:
        raw_config: dict[str, Any] = yaml.safe_load(config_file) or {}

    generation_config = raw_config.get("data_generation", {})
    output_path = Path(generation_config.get("output_path", DataGenerationConfig.output_path))
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path

    return DataGenerationConfig(
        random_seed=int(generation_config.get("random_seed", 42)),
        number_of_customers=int(generation_config.get("number_of_customers", 500)),
        number_of_accounts=int(generation_config.get("number_of_accounts", 700)),
        number_of_transactions=int(generation_config.get("number_of_transactions", 5000)),
        number_of_beneficiaries=int(generation_config.get("number_of_beneficiaries", 800)),
        number_of_devices=int(generation_config.get("number_of_devices", 600)),
        output_path=output_path,
    )


def generate_datasets(config: DataGenerationConfig) -> dict[str, pd.DataFrame]:
    """Generate all synthetic datasets in memory."""
    rng = np.random.default_rng(config.random_seed)

    customers = generate_customers(config.number_of_customers, rng)
    accounts = generate_accounts(config.number_of_accounts, customers, rng)
    beneficiaries = generate_beneficiaries(config.number_of_beneficiaries, rng)
    devices = generate_devices(config.number_of_devices, rng)
    transactions = generate_transactions(
        config.number_of_transactions,
        accounts,
        beneficiaries,
        devices,
        rng,
    )
    alerts = generate_alerts(transactions, rng)
    case_notes = generate_case_notes(alerts, rng)

    return {
        "customers": customers,
        "accounts": accounts,
        "beneficiaries": beneficiaries,
        "devices": devices,
        "transactions": transactions,
        "alerts": alerts,
        "case_notes": case_notes,
    }


def write_datasets(datasets: dict[str, pd.DataFrame], output_path: Path) -> dict[str, Path]:
    """Write generated datasets to CSV files."""
    output_path.mkdir(parents=True, exist_ok=True)
    written_files: dict[str, Path] = {}

    for dataset_name, dataset in datasets.items():
        file_path = output_path / f"{dataset_name}.csv"
        dataset.to_csv(file_path, index=False)
        written_files[dataset_name] = file_path

    return written_files


def generate_all_datasets(config: DataGenerationConfig | None = None) -> dict[str, Path]:
    """Generate and write all synthetic datasets."""
    resolved_config = config or load_generation_config()
    datasets = generate_datasets(resolved_config)
    return write_datasets(datasets, resolved_config.output_path)
