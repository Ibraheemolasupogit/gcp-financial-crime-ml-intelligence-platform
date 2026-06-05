# Monitoring Strategy

Milestone 9 adds local model monitoring and drift reporting across the synthetic financial crime platform outputs.

## Purpose

Monitoring is essential in financial crime ML because data distributions, typologies, alert volumes, and risk-score behaviour can change over time. This local monitoring layer demonstrates production-style thinking without deploying live services.

## Data Drift Checks

The workflow uses `data/processed/transaction_features.csv` and creates a deterministic baseline/current split. When timestamps are available, rows are sorted by transaction timestamp first. The baseline period is the first 70 percent of rows and the current period is the final 30 percent.

Numeric and boolean engineered features are monitored with:

- Baseline mean
- Current mean
- Mean difference
- Percent change
- Missing value rate change
- Simple PSI-style drift score
- Drift flag based on configured thresholds

## Prediction And Risk Monitoring

The workflow summarises available outputs for:

- Fraud probabilities and fraud prediction rate
- AML risk score and band distribution
- Anomaly score, anomaly rate, and anomaly band distribution
- Network risk score and band distribution
- NLP triage score, band distribution, and typology distribution

Optional files are handled gracefully and reported when missing.

## Alert Quality Monitoring

Alert quality monitoring checks alert-like outputs for volume and concentration:

- Prioritised alert counts and band distribution
- AML high/critical count
- Anomaly high/critical count
- Network high/critical count
- NLP high/critical count
- Duplicate transaction coverage across alert outputs
- Top reason codes across available outputs

## Output Files

```text
outputs/sample/data_drift_summary.csv
outputs/sample/prediction_monitoring_summary.json
outputs/sample/alert_quality_summary.json
outputs/sample/monitoring_summary.json
reports/sample/model_monitoring_report.md
```

## Run Locally

```bash
python scripts/run_monitoring.py
```

Or use the CLI:

```bash
python -m financial_crime_ml.cli run-monitoring
```

## GCP Conceptual Mapping

This local approach maps conceptually to Vertex AI Model Monitoring for drift signals, Cloud Logging for operational events, BigQuery for monitoring tables, and Looker Studio for reporting. No live GCP integration is implemented in this milestone.

## Limitations

This milestone does not implement live cloud monitoring, dashboards, APIs, model registry, retraining automation, agentic AI, or real customer monitoring. It is a lightweight synthetic-data monitoring workflow.
