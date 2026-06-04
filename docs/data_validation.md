# Data Validation

Milestone 3 adds a local ingestion and validation layer for the synthetic financial crime datasets generated in Milestone 2. The validation layer is designed to prepare the project for later feature engineering, modelling, monitoring, and governance evidence without implementing those later stages.

## Ingestion Design

The ingestion package loads CSV files from `data/sample/` using pandas. The default dataset keys are:

- `customers`
- `accounts`
- `transactions`
- `beneficiaries`
- `devices`
- `alerts`
- `case_notes`

The loader supports a configurable input path and raises readable errors when required files are missing.

## Schema Validation Checks

Each dataset has an explicit schema defining required columns, broad type categories, primary key uniqueness, and allowed categorical values where appropriate.

Validation checks include:

- Required columns
- Missing required values
- Duplicate primary keys
- Invalid numeric values
- Invalid datetime parsing
- Invalid boolean values
- Invalid categorical values
- Negative transaction amounts

## Relationship Checks

The validation layer checks foreign-key style relationships across the synthetic datasets:

- `accounts.customer_id` exists in `customers.customer_id`
- `transactions.account_id` exists in `accounts.account_id`
- `transactions.beneficiary_id` exists in `beneficiaries.beneficiary_id`
- `transactions.device_id` exists in `devices.device_id`
- `alerts.transaction_id` exists in `transactions.transaction_id`
- `alerts.account_id` exists in `accounts.account_id`
- `case_notes.alert_id` exists in `alerts.alert_id`

## Data Quality Report

The validation script writes a JSON report to:

```text
outputs/sample/data_quality_report.json
```

The report includes row counts, column counts, missing value counts, duplicate primary key counts, schema validation status, relationship validation status, validation issues, and an overall status.

## Run Locally

Generate sample data first if needed:

```bash
python scripts/generate_demo_data.py
```

Run validation:

```bash
python scripts/validate_demo_data.py
```

Or use the package CLI:

```bash
python -m financial_crime_ml.cli validate-data
```

## Limitations

This validation layer is intentionally local-first and schema-focused. It does not perform feature engineering, model validation, statistical drift analysis, cloud data quality checks, or production monitoring. Those capabilities belong to later milestones.
