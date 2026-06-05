# End-to-End Walkthrough

This walkthrough runs the full local synthetic financial crime ML lifecycle. It uses synthetic data only and does not require cloud credentials or live GCP infrastructure.

## 1. Generate Synthetic Data

Command:

```bash
python3 scripts/generate_demo_data.py
```

Purpose: create deterministic synthetic customers, accounts, transactions, beneficiaries, devices, alerts, and case notes.

Key input: `configs/pipeline_config.yaml`

Key output: `data/sample/*.csv`

What to inspect: row counts, suspicious transaction patterns, alert reasons, and synthetic case-note narratives.

## 2. Validate Data

Command:

```bash
python3 scripts/validate_demo_data.py
```

Purpose: load all sample datasets, validate schemas, check required values, and verify foreign-key style relationships.

Key input: `data/sample/*.csv`

Key output: `outputs/sample/data_quality_report.json`

What to inspect: overall status, validation issues, row counts, missing values, duplicate primary keys, and relationship checks.

## 3. Build Features

Command:

```bash
python3 scripts/build_features.py
```

Purpose: create transaction, velocity, customer/account, beneficiary, device, and AML typology indicator features.

Key input: `data/sample/*.csv`

Key outputs:

- `data/processed/transaction_features.csv`
- `outputs/sample/feature_summary.json`

What to inspect: feature columns, typology flag counts, suspicious transaction rate, and preserved identifier columns.

## 4. Train Fraud Model and AML Scoring

Command:

```bash
python3 scripts/train_fraud_model.py
```

Purpose: train a lightweight supervised fraud classifier and generate deterministic AML risk scores and prioritised alerts.

Key input: `data/processed/transaction_features.csv`

Key outputs:

- `outputs/sample/model_metrics.json`
- `outputs/sample/fraud_predictions.csv`
- `outputs/sample/aml_risk_scores.csv`
- `outputs/sample/prioritised_alerts.csv`
- `reports/sample/model_card.md`

What to inspect: precision, recall, F1 score, ROC AUC, AML risk reasons, priority bands, and model card limitations.

## 5. Run Anomaly Detection

Command:

```bash
python3 scripts/run_anomaly_detection.py
```

Purpose: identify unusual transaction behaviour using unsupervised Isolation Forest scoring.

Key input: `data/processed/transaction_features.csv`

Key outputs:

- `outputs/sample/anomaly_scores.csv`
- `outputs/sample/high_risk_anomalies.csv`
- `outputs/sample/anomaly_summary.json`
- `reports/sample/anomaly_detection_report.md`

What to inspect: anomaly bands, reason codes, anomaly rate, and overlap with suspicious synthetic labels.

## 6. Run Network Risk Modelling

Command:

```bash
python3 scripts/run_network_risk.py
```

Purpose: build a NetworkX graph connecting customers, accounts, transactions, beneficiaries, and devices, then score shared-device, shared-beneficiary, and cluster risk.

Key inputs:

- `data/sample/*.csv`
- `outputs/sample/aml_risk_scores.csv`
- `outputs/sample/anomaly_scores.csv`
- `outputs/sample/fraud_predictions.csv`

Key outputs:

- `outputs/sample/network_risk_scores.csv`
- `outputs/sample/high_risk_networks.csv`
- `outputs/sample/network_summary.json`
- `reports/sample/network_risk_report.md`

What to inspect: network risk bands, cluster sizes, shared device counts, shared beneficiary counts, and network risk reasons.

## 7. Run NLP Alert Triage

Command:

```bash
python3 scripts/run_nlp_triage.py
```

Purpose: classify synthetic case-note typologies and generate alert-level NLP triage scores.

Key inputs:

- `data/sample/alerts.csv`
- `data/sample/case_notes.csv`
- Optional risk outputs from earlier stages

Key outputs:

- `outputs/sample/nlp_case_note_classifications.csv`
- `outputs/sample/nlp_alert_triage.csv`
- `outputs/sample/nlp_summary.json`
- `reports/sample/nlp_alert_triage_report.md`

What to inspect: predicted typologies, confidence values, triage bands, review queues, and top triage reasons.

## 8. Run Monitoring

Command:

```bash
python3 scripts/run_monitoring.py
```

Purpose: generate data drift, prediction distribution, risk distribution, and alert quality monitoring summaries.

Key inputs:

- `data/processed/transaction_features.csv`
- Model, AML, anomaly, network, and NLP outputs

Key outputs:

- `outputs/sample/data_drift_summary.csv`
- `outputs/sample/prediction_monitoring_summary.json`
- `outputs/sample/alert_quality_summary.json`
- `outputs/sample/monitoring_summary.json`
- `reports/sample/model_monitoring_report.md`

What to inspect: drifted features, risk band distributions, high-priority alert counts, and operational recommendations.

## 9. Generate Governance Pack

Command:

```bash
python3 scripts/generate_governance_pack.py
```

Purpose: produce governance controls, model risk assessment, evidence inventory, audit log, lifecycle traceability, and governance reports.

Key inputs: configs, docs, reports, and generated outputs from prior stages.

Key outputs:

- `outputs/sample/governance_control_checklist.json`
- `outputs/sample/model_risk_assessment.json`
- `outputs/sample/evidence_inventory.json`
- `outputs/sample/audit_log.jsonl`
- `outputs/sample/lifecycle_traceability.json`
- `reports/sample/governance_evidence_pack.md`
- `reports/sample/model_risk_management_report.md`

What to inspect: control statuses, component risk ratings, production readiness caveats, audit events, and evidence inventory coverage.

## 10. Validate Docs

Command:

```bash
python3 scripts/validate_docs.py
```

Purpose: verify that required GCP architecture docs and Mermaid diagrams are present and contain required cloud and governance references.

Key inputs:

- `docs/*.md`
- `diagrams/*.mmd`

Key output: terminal validation summary.

What to inspect: validation status, checked document count, checked diagram count, and any reported issues.

## One-Command Local Demo

Run the full sequence:

```bash
bash scripts/run_all_local.sh
```

The workflow is local-only, deterministic where configured, and designed for portfolio demonstration rather than production use.
