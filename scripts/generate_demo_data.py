"""Generate Milestone 2 synthetic demo datasets."""

from financial_crime_ml.data_generation import generate_all_datasets


def main() -> None:
    """Generate all configured sample datasets."""
    written_files = generate_all_datasets()
    for dataset_name, file_path in written_files.items():
        print(f"Generated {dataset_name}: {file_path}")


if __name__ == "__main__":
    main()
