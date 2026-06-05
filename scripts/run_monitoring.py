"""Run Milestone 9 local model monitoring outputs."""

from financial_crime_ml.monitoring import run_monitoring_workflow


def main() -> None:
    """Run monitoring and print a concise summary."""
    result = run_monitoring_workflow()
    summary = result["monitoring_summary"]
    print("Monitoring workflow completed.")
    print(f"Overall status: {summary['overall_status']}")
    print(f"Total drifted features: {summary['total_drifted_features']}")
    print(f"High-priority alert count: {summary['high_priority_alert_count']}")
    print(f"Data drift summary written to: {result['data_drift_summary_path']}")
    print(f"Prediction monitoring written to: {result['prediction_monitoring_summary_path']}")
    print(f"Alert quality summary written to: {result['alert_quality_summary_path']}")
    print(f"Monitoring summary written to: {result['monitoring_summary_path']}")
    print(f"Report written to: {result['monitoring_report_path']}")


if __name__ == "__main__":
    main()
