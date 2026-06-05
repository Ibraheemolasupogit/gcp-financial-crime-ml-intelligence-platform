# Model Monitoring Report

## Purpose

This report summarises Milestone 9 local monitoring and drift reporting across synthetic
financial crime model, scoring, anomaly, network, and NLP outputs.

## Monitoring Scope

Sources used: ['transaction_features', 'fraud_predictions', 'aml_risk_scores', 'prioritised_alerts', 'anomaly_scores', 'high_risk_anomalies', 'network_risk_scores', 'high_risk_networks', 'nlp_alert_triage']

## Data Drift Methodology

The transaction feature table is split into baseline and current periods using a deterministic
70/30 split, sorted by transaction timestamp when available. Numeric and boolean engineered
features are monitored using mean change, missing-rate change, and a simple PSI-style score.

## Prediction And Risk Monitoring Methodology

The workflow summarises fraud probability, fraud prediction rate, AML risk scores, anomaly
scores, network risk scores, NLP triage scores, and associated band distributions where
outputs are available.

## Alert Quality Monitoring Methodology

The workflow monitors prioritised alert volume, high/critical counts across AML, anomaly,
network, and NLP outputs, duplicate transaction coverage, and recurring reason codes.

## Key Findings

- Overall status: passed
- Total drifted features: 4
- High-priority alert count: 26
- Drifted features: ['transaction_month', 'amount_zscore_by_account', 'hours_since_previous_transaction', 'is_new_beneficiary']

## Risk Band Distribution Summaries

- AML: {'Info': 3451, 'Low': 1299, 'Medium': 241, 'High': 9}
- Anomaly: {'Info': 3500, 'Low': 750, 'Medium': 500, 'High': 200, 'Critical': 50}
- Network: {'Medium': 3995, 'High': 996, 'Critical': 9}
- NLP: {'High': 525, 'Critical': 210, 'Low': 104, 'Medium': 61}

## Alert Volume Observations

['Review concentration of high and critical alert bands.', 'Compare duplicate transaction coverage across alert-like outputs.', 'Use reason-code distribution to identify recurring operational drivers.', 'Multiple monitoring outputs reference the same transactions.']

Top reason codes: {'SHARED_DEVICE': 4997, 'DEVICE_USED_BY_MULTIPLE_ACCOUNTS': 4997, 'SHARED_BENEFICIARY': 4992, 'BENEFICIARY_PAID_BY_MULTIPLE_ACCOUNTS': 4992, 'CROSS_BORDER_TRANSACTION': 4253, 'DEVICE_LINKED_TO_SUSPICIOUS_ACTIVITY': 3912, 'BENEFICIARY_LINKED_TO_HIGH_RISK_ACTIVITY': 3658, 'HIGH_RISK_JURISDICTION': 907, 'MULE_NETWORK_INDICATOR': 898, 'NETWORK_HIGH_OR_CRITICAL': 898, 'No immediate priority indicators': 696, 'NO_DOMINANT_REASON': 593, 'DEVICE_RISK_SIGNAL': 409, 'HIGH_ALERT_SEVERITY': 385, 'ANOMALY_OVERLAP': 293}

## Operational Recommendations

- Review drifted feature list before model interpretation or release decisions.
- Investigate concentration of high and critical alert bands.
- Track recurring reason codes as potential rule tuning or data quality signals.
- Use this local report as a template for production monitoring requirements.

## Limitations

This milestone does not implement live monitoring, GCP services, dashboards, APIs, model
registry, retraining automation, agentic AI, or real customer data monitoring.

## Synthetic Data Caveat

All inputs are synthetic. Monitoring findings demonstrate engineering workflow design and
should not be interpreted as production model performance or operational risk evidence.

## Human Review Requirement

Monitoring outputs require analyst, model risk, and control-owner review before any real-world
action could be taken in a financial services environment.

## GCP Alignment Note

This local approach maps conceptually to Vertex AI Model Monitoring for drift signals, Cloud
Logging for operational events, BigQuery for monitoring tables, and Looker Studio for reporting.
No live GCP integration is implemented in this milestone.
