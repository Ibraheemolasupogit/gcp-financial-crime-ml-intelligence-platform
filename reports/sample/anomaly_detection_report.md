# Anomaly Detection Report

## Purpose

This report summarises the Milestone 6 unsupervised anomaly detection layer for synthetic
financial crime transactions.

## Model Used

- IsolationForest
- Local scikit-learn implementation
- Synthetic engineered transaction features only

## Features Used

Feature count: 45

Features: amount, transaction_amount_log, is_round_amount, is_high_value_transaction, is_cross_border_transaction, is_high_risk_destination, is_unusual_channel, transaction_hour, transaction_day_of_week, transaction_month, is_night_transaction, amount_zscore_by_account, transaction_count_by_account, average_amount_by_account, amount_vs_account_average_ratio, transactions_last_1h, transactions_last_24h, transaction_amount_last_24h, hours_since_previous_transaction, high_velocity_flag, rapid_sequence_flag, customer_risk_band_encoded, account_age_days, customer_tenure_days, account_transaction_count, account_total_transaction_amount, account_average_transaction_amount, account_suspicious_transaction_rate, beneficiary_risk_band_encoded, is_new_beneficiary, beneficiary_country_risk_flag, beneficiary_transaction_count, beneficiary_total_amount, device_risk_band_encoded, device_country_mismatch_flag, device_transaction_count, shared_device_flag, round_amount_count_by_account, structuring_pattern_flag, rapid_movement_flag, high_risk_jurisdiction_flag, mule_activity_indicator, account_takeover_indicator, new_beneficiary_high_value_flag, round_amount_repetition_flag

## Excluded Columns

Identifiers, raw timestamp/text fields, helper labels, and `is_suspicious` are excluded from
anomaly model training. The synthetic suspicious label is used only for overlap analysis.

## Results

- Row count: 5000
- Anomaly count: 400
- Anomaly rate: 0.0800
- Band distribution: {'Critical': 50, 'High': 200, 'Info': 3500, 'Low': 750, 'Medium': 500}
- Top reason codes: {'CROSS_BORDER_TRANSACTION': 327, 'HIGH_VALUE_TRANSACTION': 155, 'HIGH_RISK_JURISDICTION': 145, 'ROUND_AMOUNT_PATTERN': 113, 'RAPID_MOVEMENT': 108, 'ACCOUNT_TAKEOVER_SIGNAL': 49, 'DEVICE_RISK_SIGNAL': 43, 'MULE_ACTIVITY_SIGNAL': 12, 'NEW_BENEFICIARY_HIGH_VALUE': 5}
- Suspicious label overlap count: 293
- Suspicious label overlap rate: 0.7325
- AML high/critical overlap count: 9

## Limitations

This is a lightweight local anomaly discovery layer. It is not a production transaction
monitoring system, graph model, NLP model, model registry, serving API, or cloud deployment.

## Human Review Requirement

Anomaly outputs are triage aids only. Real financial crime workflows require investigator
review, escalation controls, governance approval, and validation before operational use.

## Synthetic Data Caveat

All data is synthetic and safe for public demonstration. Results should not be interpreted as
evidence of real-world financial crime detection performance.
