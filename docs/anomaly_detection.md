# Anomaly Detection

Milestone 6 adds an unsupervised anomaly detection layer for the engineered synthetic transaction feature table.

## Purpose

Anomaly detection helps surface unusual transaction behaviour that may not be fully captured by supervised fraud labels or deterministic AML rules. In financial crime analytics, unsupervised methods can support risk discovery, analyst triage, and monitoring of unexpected behavioural patterns.

## Why Unsupervised Detection Is Useful

Supervised fraud models depend on labelled outcomes. Financial crime typologies evolve, and labels can be incomplete or delayed. An unsupervised anomaly layer provides an additional perspective by identifying transactions that look unusual relative to the broader engineered feature distribution.

## Model Used

The milestone uses scikit-learn `IsolationForest`. It is lightweight, local-first, and appropriate as a first unsupervised baseline for tabular engineered features.

## Feature Selection

The model uses numeric and boolean engineered features from:

```text
data/processed/transaction_features.csv
```

Identifier columns, raw text/categorical fields, raw timestamps, helper labels, and `is_suspicious` are excluded from training. The synthetic suspicious label may be used only for overlap analysis in reports.

## Reason Codes

Reason codes are deterministic and interpretable. Examples include:

- `HIGH_VALUE_TRANSACTION`
- `HIGH_VELOCITY`
- `HIGH_RISK_JURISDICTION`
- `ROUND_AMOUNT_PATTERN`
- `NEW_BENEFICIARY_HIGH_VALUE`
- `RAPID_MOVEMENT`
- `ACCOUNT_TAKEOVER_SIGNAL`
- `MULE_ACTIVITY_SIGNAL`
- `DEVICE_RISK_SIGNAL`
- `CROSS_BORDER_TRANSACTION`

## Outputs

```text
outputs/sample/anomaly_scores.csv
outputs/sample/high_risk_anomalies.csv
outputs/sample/anomaly_summary.json
reports/sample/anomaly_detection_report.md
```

The high-risk ranking optionally joins fraud predictions, AML risk scores, and prioritised alert outputs when those files are available. The workflow still runs if those optional files are missing.

## Run Locally

```bash
python scripts/run_anomaly_detection.py
```

Or use the CLI:

```bash
python -m financial_crime_ml.cli run-anomaly-detection
```

## Limitations

This is not graph modelling, NLP classification, production monitoring, live serving, or cloud deployment. It is a lightweight local anomaly discovery layer using synthetic data only.
