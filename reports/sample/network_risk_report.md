# Network Risk Report

## Purpose

This report summarises Milestone 7 graph/network risk modelling for synthetic financial
crime transaction data.

## Graph Design

The graph is a simple heterogeneous NetworkX graph connecting customers, accounts,
transactions, beneficiaries, and devices.

## Node Types

{'customer': 500, 'account': 700, 'beneficiary': 800, 'device': 600, 'transaction': 5000}

## Edge Types

Edges include customer OWNS account, account SENDS transaction, transaction TO beneficiary,
transaction USED device, account USES device, and account PAYS beneficiary.

Edge counts: {'OWNS': 700, 'SENDS': 5000, 'USES': 4962, 'PAYS': 4982, 'TO': 5000, 'USED': 5000}

## Graph Size

- Nodes: 7600
- Edges: 25644
- Connected components: 131
- Largest component size: 7470

## Network Risk Results

- Network risk band counts: {'Medium': 3995, 'High': 996, 'Critical': 9}
- High-risk network count: 1005
- Top network risk reasons: {'SHARED_DEVICE': 4997, 'DEVICE_USED_BY_MULTIPLE_ACCOUNTS': 4997, 'SHARED_BENEFICIARY': 4992, 'BENEFICIARY_PAID_BY_MULTIPLE_ACCOUNTS': 4992, 'DEVICE_LINKED_TO_SUSPICIOUS_ACTIVITY': 3912, 'BENEFICIARY_LINKED_TO_HIGH_RISK_ACTIVITY': 3658, 'MULE_NETWORK_INDICATOR': 898, 'BENEFICIARY_LINKED_TO_HIGH_VALUE_ACTIVITY': 74}
- AML high/critical overlap count: 9
- Anomaly overlap count: 100

## Limitations

This is a local, deterministic graph risk layer. It is not a production graph database,
entity resolution system, NLP workflow, agentic AI system, dashboard, API, or cloud deployment.

## Human Review Requirement

Network risk outputs are triage aids only. Real financial crime workflows require investigator
review, governance approval, validation, and operational controls before use.

## Synthetic Data Caveat

All data and relationships are synthetic. Results should not be interpreted as real-world
financial crime detection performance.
