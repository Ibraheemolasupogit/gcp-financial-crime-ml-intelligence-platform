# Network Risk Modelling

Milestone 7 adds a local graph/network risk layer for synthetic financial crime relationships.

## Purpose

Financial crime often appears through relationships rather than isolated transactions. Shared devices, shared beneficiaries, account clusters, and connected transaction patterns can indicate mule-account behaviour, account takeover patterns, or coordinated movement of funds.

## Graph Design

The graph is a heterogeneous NetworkX graph with customers, accounts, transactions, beneficiaries, and devices.

Edges include:

- Customer `OWNS` account
- Account `SENDS` transaction
- Transaction `TO` beneficiary
- Transaction `USED` device
- Account `USES` device
- Account `PAYS` beneficiary

## Shared-Device Risk

The feature layer detects devices used by multiple accounts and devices linked to suspicious activity. Reason codes include `SHARED_DEVICE`, `DEVICE_USED_BY_MULTIPLE_ACCOUNTS`, and `DEVICE_LINKED_TO_SUSPICIOUS_ACTIVITY`.

## Shared-Beneficiary Risk

The feature layer detects beneficiaries paid by multiple accounts, beneficiaries linked to suspicious transactions, and beneficiaries receiving high-value activity. Reason codes include `SHARED_BENEFICIARY`, `BENEFICIARY_PAID_BY_MULTIPLE_ACCOUNTS`, and `BENEFICIARY_LINKED_TO_HIGH_RISK_ACTIVITY`.

## Connected Components

Connected components are used as a simple suspicious cluster mechanism. The workflow records cluster IDs, cluster sizes, and suspicious cluster flags based on component size and suspicious transaction concentration.

## Network Risk Scoring

Network scores are deterministic and transparent. They use shared-device indicators, shared-beneficiary indicators, suspicious cluster flags, mule-network indicators, AML overlap, and anomaly overlap where optional outputs are available.

## Outputs

```text
outputs/sample/network_risk_scores.csv
outputs/sample/high_risk_networks.csv
outputs/sample/network_summary.json
reports/sample/network_risk_report.md
```

## Run Locally

```bash
python scripts/run_network_risk.py
```

Or use the CLI:

```bash
python -m financial_crime_ml.cli run-network-risk
```

## Limitations

This milestone does not implement NLP, agents, dashboards, graph databases, entity resolution, cloud deployment, or live APIs. It is a lightweight NetworkX implementation for synthetic portfolio data.
