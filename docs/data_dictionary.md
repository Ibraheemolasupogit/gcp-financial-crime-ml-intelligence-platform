# Data Dictionary

Milestone 2 introduces fully synthetic sample datasets for financial crime ML engineering workflows. The data is generated locally and does not contain real customer, account, transaction, device, alert, or analyst information.

## customers.csv

Synthetic customer-level profiles for individuals and businesses.

- `customer_id`: Unique synthetic customer identifier.
- `customer_type`: Customer segment, such as individual or business.
- `age_band_or_business_type`: Synthetic age band for individuals or business category for businesses.
- `country`: Synthetic customer country code.
- `risk_band`: Synthetic baseline risk band.
- `onboarding_date`: Synthetic onboarding date.
- `kyc_status`: Synthetic know-your-customer review status.

## accounts.csv

Synthetic accounts linked to generated customers.

- `account_id`: Unique synthetic account identifier.
- `customer_id`: Customer identifier linked to `customers.csv`.
- `account_type`: Synthetic account product type.
- `open_date`: Synthetic account opening date.
- `account_status`: Synthetic account lifecycle status.
- `base_currency`: Primary account currency.
- `branch_region`: Synthetic servicing region or digital channel grouping.

## transactions.csv

Synthetic transaction activity for future fraud, AML, anomaly, graph, and monitoring use cases.

- `transaction_id`: Unique synthetic transaction identifier.
- `account_id`: Account identifier linked to `accounts.csv`.
- `beneficiary_id`: Beneficiary identifier linked to `beneficiaries.csv`.
- `device_id`: Device identifier linked to `devices.csv`.
- `transaction_timestamp`: Synthetic transaction timestamp.
- `amount`: Synthetic transaction amount.
- `currency`: Transaction currency.
- `transaction_type`: Payment or transaction category.
- `merchant_category`: Synthetic merchant or counterparty category.
- `origin_country`: Synthetic origin country, derived from device context.
- `destination_country`: Synthetic destination country, derived from beneficiary context or typology.
- `channel`: Transaction channel.
- `is_suspicious`: Boolean label for synthetic suspicious activity.
- `suspicious_pattern`: Synthetic typology marker or `normal_activity`.

## beneficiaries.csv

Synthetic payment beneficiaries and counterparties.

- `beneficiary_id`: Unique synthetic beneficiary identifier.
- `beneficiary_country`: Synthetic beneficiary country code.
- `beneficiary_type`: Beneficiary category.
- `first_seen_date`: Date the beneficiary first appears in the synthetic history.
- `risk_band`: Synthetic beneficiary risk band.

## devices.csv

Synthetic device records for digital channel and account access patterns.

- `device_id`: Unique synthetic device identifier.
- `device_type`: Device or client type.
- `ip_country`: Synthetic IP geolocation country code.
- `first_seen_date`: Date the device first appears in the synthetic history.
- `device_risk_band`: Synthetic device risk band.

## alerts.csv

Synthetic alert records generated from suspicious transactions.

- `alert_id`: Unique synthetic alert identifier.
- `transaction_id`: Transaction identifier linked to `transactions.csv`.
- `account_id`: Account identifier linked to `accounts.csv`.
- `alert_type`: Alert category derived from the suspicious pattern.
- `alert_severity`: Synthetic alert severity.
- `alert_status`: Synthetic workflow status.
- `alert_timestamp`: Synthetic alert creation timestamp.
- `alert_reason`: Short synthetic reason for alert generation.

## case_notes.csv

Synthetic analyst-style notes linked to generated alerts.

- `case_note_id`: Unique synthetic case note identifier.
- `alert_id`: Alert identifier linked to `alerts.csv`.
- `note_timestamp`: Synthetic note timestamp.
- `note_text`: Synthetic narrative text for future NLP triage experimentation.
- `typology_label`: Synthetic typology label aligned to the alert reason.

## Simulated Suspicious Patterns

The generator includes normal activity and synthetic suspicious examples covering high transaction velocity, round-number payments, unusual amount spikes, new beneficiary risk, high-risk jurisdiction exposure, rapid movement of funds, shared device behaviour, mule-account style behaviour, account takeover style behaviour, and suspicious case-note narratives.
