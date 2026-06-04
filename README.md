# GCP Financial Crime ML Intelligence Platform

A local-first, GCP-aligned machine learning intelligence platform for financial crime analytics. The project is designed as a professional portfolio implementation of fraud detection, AML risk scoring, anomaly detection, graph and network risk modelling, NLP-assisted alert triage, monitoring, governance evidence, and cloud reference architecture.

Milestone 2 adds deterministic synthetic financial crime data generation. It does not include production models, live cloud integrations, dashboards, or real data.

## Problem Context

Financial institutions need to detect suspicious behaviour across large volumes of transactions, customers, accounts, alerts, and network relationships. Traditional rule-based systems can be brittle, noisy, and difficult to adapt as typologies evolve. Machine learning can support financial crime teams by improving risk prioritisation, surfacing anomalous patterns, identifying connected-party exposure, and helping analysts triage alert narratives.

This project is structured around those engineering problems while keeping the implementation synthetic, reproducible, and safe for public demonstration.

## Why GCP

Google Cloud Platform is relevant to this domain because financial crime workloads often require scalable data processing, governed feature pipelines, model training and serving, secure analytics, auditability, and monitoring. This repository is local-first for development, but its architecture and documentation are aligned to GCP services such as BigQuery, Vertex AI, Cloud Composer, Cloud Storage, Pub/Sub, Dataflow, and Cloud Monitoring.

No live GCP resources or credentials are required for the current milestones.

## Intended Platform Capabilities

The planned platform capabilities include:

- Synthetic financial crime data generation and management
- Fraud detection model workflows
- AML customer and entity risk scoring
- Transaction and behavioural anomaly detection
- Graph and network-based risk modelling
- NLP-assisted alert triage and case summarisation
- Model monitoring and drift reporting
- Model risk governance evidence packs
- GCP-aligned reference architecture and deployment design

## Milestone-Based Build Approach

The project will be built incrementally to keep scope controlled and each milestone reviewable. Milestone 1 created the professional project scaffold, package skeleton, configuration placeholders, documentation placeholders, diagram placeholders, CI workflow, and basic tests.

Future milestones will add data generation, feature engineering, modelling, evaluation, monitoring, governance artefacts, and cloud-aligned architecture examples in deliberate stages.

## Milestone 2: Synthetic Data Generation

Milestone 2 generates fully synthetic sample datasets under `data/sample/` for future fraud detection, AML risk scoring, anomaly detection, graph risk modelling, NLP alert triage, monitoring, and governance evidence workflows.

Generated datasets:

- `customers.csv`
- `accounts.csv`
- `transactions.csv`
- `beneficiaries.csv`
- `devices.csv`
- `alerts.csv`
- `case_notes.csv`

The generator is deterministic when a random seed is provided in `configs/pipeline_config.yaml`. It simulates normal activity and suspicious patterns such as high transaction velocity, round-number payments, unusual amount spikes, new beneficiary risk, high-risk jurisdiction exposure, rapid movement of funds, shared device behaviour, mule-account style behaviour, account takeover style behaviour, and synthetic suspicious case-note narratives.

Generate the sample data:

```bash
python scripts/generate_demo_data.py
```

Or use the package CLI:

```bash
python -m financial_crime_ml.cli generate-data
```

The generated files are synthetic demonstration artefacts only. They must not be interpreted as real customer behaviour or real financial crime intelligence.

## Milestone 3: Data Ingestion and Validation

Milestone 3 adds a local ingestion and validation layer for the synthetic datasets. It loads the CSV files from `data/sample/`, validates explicit dataset schemas, checks foreign-key style relationships, and writes a data quality report.

Run validation:

```bash
python scripts/validate_demo_data.py
```

Or use the package CLI:

```bash
python -m financial_crime_ml.cli validate-data
```

The validation report is written to:

```text
outputs/sample/data_quality_report.json
```

This remains synthetic-data-only and local-first. The validation layer does not implement feature engineering, models, monitoring, dashboards, or GCP deployment.

## Milestone 4: Feature Engineering and Typology Indicators

Milestone 4 adds deterministic feature engineering for the synthetic transaction data. It creates transaction, velocity, customer/account, beneficiary, device, and rule-based AML typology indicator features.

Build features:

```bash
python scripts/build_features.py
```

Or use the package CLI:

```bash
python -m financial_crime_ml.cli build-features
```

Outputs:

```text
data/processed/transaction_features.csv
outputs/sample/feature_summary.json
```

No ML models are trained in this milestone. The feature layer remains synthetic-data-only, local-first, and pandas-based.

## Milestone 5: Fraud Classifier and AML Risk Scoring

Milestone 5 adds a first supervised fraud classification baseline and deterministic AML risk scoring. It trains a lightweight scikit-learn logistic regression model on the engineered transaction feature table, writes fraud predictions and model metrics, scores AML risk using transparent typology indicators, and creates prioritised alert output.

Run the workflow:

```bash
python scripts/train_fraud_model.py
```

Or use the package CLI:

```bash
python -m financial_crime_ml.cli train-fraud-model
```

Outputs:

```text
outputs/sample/model_metrics.json
outputs/sample/fraud_predictions.csv
outputs/sample/aml_risk_scores.csv
outputs/sample/prioritised_alerts.csv
reports/sample/model_card.md
```

No live deployment, model registry, serving API, graph model, anomaly detector, or NLP classifier is included in this milestone.

## Synthetic Data Only

This repository uses synthetic data only. It must not contain real customer data, transaction data, alerts, credentials, secrets, or confidential financial crime intelligence.

## Local-First, GCP-Aligned

Development is intended to run locally first using standard Python tooling. GCP alignment is expressed through architecture, configuration design, pipeline boundaries, documentation, and future deployment references rather than live cloud dependencies in the early milestones.

## Portfolio Positioning

This project demonstrates financial crime ML engineering with a focus on scalable ML pipeline design, model governance, monitoring, and GCP-aligned production thinking. It is intended to show practical engineering judgement across fraud detection, AML analytics, anomaly detection, graph risk, NLP triage, MLOps, and regulatory control awareness.

## Current Status

Milestone 5 is an initial modelling and scoring milestone. The repository contains the project scaffold, deterministic synthetic data generation, schema and relationship validation, local data quality reporting, engineered transaction features, a baseline fraud classifier, deterministic AML risk scoring, prioritised alerts, and an initial model card.

## Quick Start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
make test
```

Run the scaffold status command:

```bash
financial-crime-ml
```

Generate synthetic demo data:

```bash
python -m financial_crime_ml.cli generate-data
```

Validate synthetic demo data:

```bash
python -m financial_crime_ml.cli validate-data
```

Build transaction-level features:

```bash
python -m financial_crime_ml.cli build-features
```

Train the fraud model and generate AML risk outputs:

```bash
python -m financial_crime_ml.cli train-fraud-model
```
