"""Validate Milestone 2 synthetic demo datasets."""

from financial_crime_ml.ingestion import DEFAULT_REPORT_PATH, run_data_validation


def main() -> None:
    """Run ingestion validation and print a concise summary."""
    report = run_data_validation()
    issue_count = len(report["validation_issues"])
    print(f"Data validation overall status: {report['overall_status']}")
    print(f"Schema validation status: {report['schema_validation_status']}")
    print(f"Relationship validation status: {report['relationship_validation_status']}")
    print(f"Validation issues: {issue_count}")
    print(f"Report written to: {DEFAULT_REPORT_PATH}")


if __name__ == "__main__":
    main()
