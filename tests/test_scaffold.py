from pathlib import Path

import financial_crime_ml
from financial_crime_ml.cli import get_status_message


def test_package_imports() -> None:
    assert financial_crime_ml.__version__ == "0.1.0"


def test_cli_status_message() -> None:
    assert (
        get_status_message()
        == "GCP Financial Crime ML Intelligence Platform scaffold is ready."
    )


def test_key_project_folders_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    expected_folders = [
        "configs",
        "data/raw",
        "data/processed",
        "data/sample",
        "docs",
        "diagrams",
        "outputs/sample",
        "reports/sample",
        "scripts",
        "src/financial_crime_ml",
        ".github/workflows",
    ]

    for folder in expected_folders:
        assert (root / folder).is_dir()

