# AML Risk Scoring

Milestone 5 adds deterministic AML risk scoring using engineered features and rule-based typology indicators.

## Scoring Logic

The score combines configured weights from `configs/risk_scoring.yaml` for transparent indicators such as:

- High-risk jurisdiction exposure
- Structuring pattern indicators
- Rapid movement of funds
- Mule-account style activity
- Account takeover style activity
- New beneficiary high-value payments
- Repeated round-amount activity
- High-value transactions
- Cross-border activity
- High transaction velocity

Synthetic suspicious labels may add small helper-context weight, but they are not the sole driver of the score.

## Risk Bands

AML risk scores are mapped to severity bands:

- Critical: 90-100
- High: 70-89
- Medium: 40-69
- Low: 10-39
- Info: 0-9

## Reason Codes

Each score includes semicolon-separated reason codes explaining which indicators contributed to the score.

## Alert Prioritisation

The prioritised alert output combines fraud probability and AML risk score into a single priority score with recommended actions:

- Immediate investigator review
- Investigator review
- Queue for monitoring
- No immediate action

## Limitations

This scoring layer is deterministic and synthetic-data-only. It is not a production rules engine, sanctions system, transaction monitoring platform, or regulatory reporting control.

## Human Review Requirement

All prioritisation outputs are illustrative. In a real financial institution, investigator review, governance approval, control testing, escalation procedures, and model validation would be required before operational use.
