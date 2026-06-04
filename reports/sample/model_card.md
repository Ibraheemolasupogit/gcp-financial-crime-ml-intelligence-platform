# Baseline Fraud Classifier Model Card

## Model Purpose

This model is a local-first baseline supervised fraud classifier for synthetic
transaction-level financial crime data. It estimates fraud probability for synthetic
transactions using engineered numeric and boolean features.

## Intended Use

The model is intended for portfolio demonstration of financial crime ML engineering,
feature selection, supervised classification, metric reporting, and governance
documentation.

## Not Intended Use

This model must not be used for live customer decisions, operational financial crime
controls, regulatory reporting, production alerting, or any real customer investigation.

## Dataset Used

- `data/processed/transaction_features.csv`
- Synthetic data only
- No real customer, account, transaction, alert, or case data

## Target Variable

- `is_suspicious`

## Feature Groups

The model uses numeric and boolean engineered features from transaction, velocity,
account/customer, beneficiary, device, and AML typology indicator groups. Identifier,
timestamp, text, and helper columns are excluded.

Feature count: 45

## Metrics

- Precision: 0.8391
- Recall: 0.8111
- F1 score: 0.8249
- ROC AUC: 0.9542140921409213
- Positive class rate: 0.1800
- Threshold used: 0.5
- Confusion matrix: [[792, 28], [34, 146]]

## Assumptions

- Synthetic suspicious labels are treated as the supervised target.
- A deterministic train/test split is used.
- Logistic regression is used for transparency and simplicity.
- Feature values are generated from local synthetic data.

## Limitations

- Synthetic data does not represent real customer behaviour.
- Metrics are demonstration metrics and should not be interpreted as production performance.
- The model is not calibrated for real financial crime operations.
- No live serving, model registry, drift monitoring, or production control integration is
  implemented.

## Human Review Requirement

Any fraud or AML output from this project is illustrative. A real financial institution
would require trained investigator review, escalation procedures, governance approval,
and formal model validation before operational use.

## Synthetic Data Caveat

All data and labels are generated synthetically for safe public demonstration. The model
card does not evidence performance on real financial crime data.

## Governance Notes

This artefact supports early model risk documentation by recording purpose, scope, data,
features, metrics, assumptions, and limitations. Later milestones may expand monitoring,
validation evidence, and governance controls.

## Model Risk Considerations

Potential risks include overfitting to synthetic typology patterns, false confidence from
synthetic metrics, limited representativeness, and misuse outside the intended portfolio
context.

## Feature Columns

amount, transaction_amount_log, is_round_amount, is_high_value_transaction, is_cross_border_transaction, is_high_risk_destination, is_unusual_channel, transaction_hour, transaction_day_of_week, transaction_month, is_night_transaction, amount_zscore_by_account, transaction_count_by_account, average_amount_by_account, amount_vs_account_average_ratio, transactions_last_1h, transactions_last_24h, transaction_amount_last_24h, hours_since_previous_transaction, high_velocity_flag, rapid_sequence_flag, customer_risk_band_encoded, account_age_days, customer_tenure_days, account_transaction_count, account_total_transaction_amount, account_average_transaction_amount, account_suspicious_transaction_rate, beneficiary_risk_band_encoded, is_new_beneficiary, beneficiary_country_risk_flag, beneficiary_transaction_count, beneficiary_total_amount, device_risk_band_encoded, device_country_mismatch_flag, device_transaction_count, shared_device_flag, round_amount_count_by_account, structuring_pattern_flag, rapid_movement_flag, high_risk_jurisdiction_flag, mule_activity_indicator, account_takeover_indicator, new_beneficiary_high_value_flag, round_amount_repetition_flag
