# NLP Alert Triage Report

## Purpose

This report summarises Milestone 8 lightweight NLP alert triage and case-note typology
classification for synthetic financial crime alerts.

## Input Datasets

- `data/sample/alerts.csv`
- `data/sample/case_notes.csv`

## Preprocessing Approach

Text is lowercased, whitespace-normalised, and handled safely when missing. Financial crime
terms are preserved for transparent keyword matching.

## Typology Labels

Labels include mule account, account takeover, high-risk jurisdiction, structuring, rapid
movement, shared device, shared beneficiary, low risk, and unknown.

## Classification Approach

The classifier is deterministic and rule-based using configured keyword patterns. Synthetic
case-note labels may be used as helper context when no keyword rule matches.

## Results

- Alerts triaged: 900
- Case notes classified: 900
- Typology distribution: {'rapid_movement': 212, 'structuring': 113, 'unknown': 109, 'account_takeover': 101, 'shared_device': 99, 'high_risk_jurisdiction': 95, 'mule_account': 88, 'shared_beneficiary': 83}
- Triage band distribution: {'High': 525, 'Critical': 210, 'Low': 104, 'Medium': 61}
- Top reason codes: {'NETWORK_HIGH_OR_CRITICAL': 898, 'HIGH_ALERT_SEVERITY': 385, 'ANOMALY_OVERLAP': 293, 'TYPOLOGY:rapid_movement': 212, 'TYPOLOGY:structuring': 113, 'KEYWORD:round-number, KEYWORD:repeated round': 113, 'TYPOLOGY:unknown': 109, 'ORIGINAL_LABEL_HINT:unusual_amount_spike': 109, 'KEYWORD:rapid inbound, KEYWORD:outbound movement': 108, 'KEYWORD:short time window': 104}
- Enrichment sources used: ['prioritised_alerts', 'aml_risk_scores', 'anomaly_scores', 'network_risk_scores']

## Limitations

This milestone does not implement LLMs, agentic AI, deep learning, transformers, dashboards,
cloud deployment, model registry, or live APIs. It is a lightweight synthetic-data workflow.

## Human Review Requirement

NLP triage outputs are investigation support only. Real financial crime workflows require
human review, escalation controls, validation, and governance approval before operational use.

## Synthetic Data Caveat

All alerts and notes are synthetic. Results should not be interpreted as production financial
crime NLP performance.
