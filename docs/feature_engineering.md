# Feature Engineering

Milestone 4 adds deterministic feature engineering for the synthetic financial crime datasets. The output is a transaction-level feature table that can later support fraud classification, AML risk scoring, anomaly detection, monitoring, governance evidence, and graph/network modelling.

This milestone does not train machine learning models.

## Transaction Features

Transaction-level features include amount transforms, round-amount indicators, high-value indicators, cross-border flags, high-risk destination flags, unusual channel flags, transaction hour, day of week, month, night-time activity, account-level amount z-scores, account transaction counts, account average amount, and amount-to-account-average ratios.

## Velocity Features

Velocity features use pandas timestamp windows by account:

- `transactions_last_1h`
- `transactions_last_24h`
- `transaction_amount_last_24h`
- `high_velocity_flag`
- `rapid_sequence_flag`

These are deliberately simple local features, not streaming or cloud pipeline implementations.

## Customer And Account Features

Customer and account features join account and customer context onto each transaction. They include customer risk band encoding, account age, customer tenure, account transaction count, account total transaction amount, account average transaction amount, and account suspicious transaction rate.

## Beneficiary Features

Beneficiary features include beneficiary risk band encoding, new beneficiary indicators, beneficiary country risk flags, beneficiary transaction count, and beneficiary total amount.

## Device Features

Device features include device risk band encoding, device country mismatch flags, device transaction count, and a simple shared-device flag based on whether a device appears across more than one account. This is not graph modelling.

## AML Typology Indicators

The feature layer adds deterministic rule-based typology indicators:

- `structuring_pattern_flag`
- `rapid_movement_flag`
- `high_risk_jurisdiction_flag`
- `mule_activity_indicator`
- `account_takeover_indicator`
- `new_beneficiary_high_value_flag`
- `round_amount_repetition_flag`

These indicators are transparent feature logic for later modelling and governance work. They are not production financial crime rules.

## Outputs

The feature pipeline writes:

```text
data/processed/transaction_features.csv
outputs/sample/feature_summary.json
```

The summary JSON includes row counts, column counts, feature column names, typology flag counts, missing value counts, suspicious transaction count, and suspicious transaction rate.

## Run Locally

Generate and validate sample data first if needed:

```bash
python scripts/generate_demo_data.py
python scripts/validate_demo_data.py
```

Build features:

```bash
python scripts/build_features.py
```

Or use the CLI:

```bash
python -m financial_crime_ml.cli build-features
```

## Limitations

This layer is deterministic, local-first, and pandas-based. It does not train models, score customers, build graph/network models, perform NLP classification, run cloud services, or implement production monitoring.
