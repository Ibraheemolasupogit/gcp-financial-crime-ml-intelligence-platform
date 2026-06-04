"""Run Milestone 6 anomaly detection outputs."""

from financial_crime_ml.monitoring import run_anomaly_detection_workflow


def main() -> None:
    """Run anomaly detection and print a concise summary."""
    result = run_anomaly_detection_workflow()
    summary = result["summary"]
    print("Anomaly detection completed.")
    print(f"Rows: {summary['row_count']}")
    print(f"Features: {summary['feature_count']}")
    print(f"Anomalies: {summary['anomaly_count']}")
    print(f"Anomaly rate: {summary['anomaly_rate']:.4f}")
    print(f"Anomaly scores written to: {result['anomaly_scores_path']}")
    print(f"High-risk anomalies written to: {result['high_risk_anomalies_path']}")
    print(f"Summary written to: {result['anomaly_summary_path']}")
    print(f"Report written to: {result['anomaly_report_path']}")


if __name__ == "__main__":
    main()
