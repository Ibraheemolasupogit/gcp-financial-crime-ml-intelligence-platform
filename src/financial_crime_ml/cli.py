"""Command-line entry point for the project."""

from __future__ import annotations

import sys

from financial_crime_ml.data_generation import generate_all_datasets
from financial_crime_ml.ingestion import DEFAULT_REPORT_PATH, run_data_validation

STATUS_MESSAGE = "GCP Financial Crime ML Intelligence Platform scaffold is ready."


def get_status_message() -> str:
    """Return the current scaffold status message."""
    return STATUS_MESSAGE


def main(argv: list[str] | None = None) -> None:
    """Run a simple project command."""
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["generate-data"]:
        written_files = generate_all_datasets()
        for dataset_name, file_path in written_files.items():
            print(f"Generated {dataset_name}: {file_path}")
        return

    if args == ["validate-data"]:
        report = run_data_validation()
        print(f"Data validation overall status: {report['overall_status']}")
        print(f"Validation issues: {len(report['validation_issues'])}")
        print(f"Report written to: {DEFAULT_REPORT_PATH}")
        return

    print(get_status_message())


if __name__ == "__main__":
    main()
