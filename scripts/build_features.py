"""Build Milestone 4 transaction-level feature outputs."""

from financial_crime_ml.features import load_feature_config, run_feature_pipeline


def main() -> None:
    """Run the feature pipeline and print a concise summary."""
    config = load_feature_config()
    feature_table, summary = run_feature_pipeline(config=config)
    print("Feature build completed.")
    print(f"Rows: {summary['number_of_rows']}")
    print(f"Columns: {summary['number_of_columns']}")
    print(f"Suspicious transaction rate: {summary['suspicious_transaction_rate']:.4f}")
    print(f"Feature table written to: {config.transaction_features_path}")
    print(f"Feature summary written to: {config.feature_summary_path}")


if __name__ == "__main__":
    main()
