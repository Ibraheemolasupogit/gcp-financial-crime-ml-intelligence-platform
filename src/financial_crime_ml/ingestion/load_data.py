"""Load synthetic financial crime datasets from CSV files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT_PATH = REPO_ROOT / "data" / "sample"

DATASET_FILES = {
    "customers": "customers.csv",
    "accounts": "accounts.csv",
    "transactions": "transactions.csv",
    "beneficiaries": "beneficiaries.csv",
    "devices": "devices.csv",
    "alerts": "alerts.csv",
    "case_notes": "case_notes.csv",
}


def resolve_input_path(input_path: str | Path = DEFAULT_INPUT_PATH) -> Path:
    """Resolve an input path relative to the repository root when needed."""
    resolved_path = Path(input_path)
    if not resolved_path.is_absolute():
        resolved_path = REPO_ROOT / resolved_path
    return resolved_path


def load_dataset(dataset_name: str, input_path: str | Path = DEFAULT_INPUT_PATH) -> pd.DataFrame:
    """Load one required dataset by name."""
    if dataset_name not in DATASET_FILES:
        valid_names = ", ".join(sorted(DATASET_FILES))
        raise ValueError(f"Unknown dataset '{dataset_name}'. Expected one of: {valid_names}.")

    base_path = resolve_input_path(input_path)
    file_path = base_path / DATASET_FILES[dataset_name]
    if not file_path.exists():
        raise FileNotFoundError(
            f"Required dataset file is missing: {file_path}. "
            "Run `python scripts/generate_demo_data.py` to create sample data."
        )

    return pd.read_csv(file_path)


def load_all_datasets(input_path: str | Path = DEFAULT_INPUT_PATH) -> dict[str, pd.DataFrame]:
    """Load all required synthetic datasets."""
    base_path = resolve_input_path(input_path)
    missing_files = [
        filename for filename in DATASET_FILES.values() if not (base_path / filename).exists()
    ]
    if missing_files:
        missing_list = ", ".join(missing_files)
        raise FileNotFoundError(
            f"Missing required dataset files in {base_path}: {missing_list}. "
            "Run `python scripts/generate_demo_data.py` to create sample data."
        )

    return {
        dataset_name: pd.read_csv(base_path / filename)
        for dataset_name, filename in DATASET_FILES.items()
    }
