# GCP Financial Crime ML Intelligence Platform

A local-first, GCP-aligned machine learning intelligence platform for financial crime analytics. The project is designed as a professional portfolio implementation of fraud detection, AML risk scoring, anomaly detection, graph and network risk modelling, NLP-assisted alert triage, monitoring, governance evidence, and cloud reference architecture.

Milestone 1 establishes the repository scaffold only. It does not yet include production models, pipelines, live cloud integrations, dashboards, or generated datasets.

## Problem Context

Financial institutions need to detect suspicious behaviour across large volumes of transactions, customers, accounts, alerts, and network relationships. Traditional rule-based systems can be brittle, noisy, and difficult to adapt as typologies evolve. Machine learning can support financial crime teams by improving risk prioritisation, surfacing anomalous patterns, identifying connected-party exposure, and helping analysts triage alert narratives.

This project is structured around those engineering problems while keeping the implementation synthetic, reproducible, and safe for public demonstration.

## Why GCP

Google Cloud Platform is relevant to this domain because financial crime workloads often require scalable data processing, governed feature pipelines, model training and serving, secure analytics, auditability, and monitoring. This repository is local-first for development, but its architecture and documentation are aligned to GCP services such as BigQuery, Vertex AI, Cloud Composer, Cloud Storage, Pub/Sub, Dataflow, and Cloud Monitoring.

No live GCP resources or credentials are required for Milestone 1.

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

The project will be built incrementally to keep scope controlled and each milestone reviewable. Milestone 1 creates the professional project scaffold, package skeleton, configuration placeholders, documentation placeholders, diagram placeholders, CI workflow, and basic tests.

Future milestones will add data generation, feature engineering, modelling, evaluation, monitoring, governance artefacts, and cloud-aligned architecture examples in deliberate stages.

## Synthetic Data Only

This repository will use synthetic data only. It must not contain real customer data, transaction data, alerts, credentials, secrets, or confidential financial crime intelligence.

## Local-First, GCP-Aligned

Development is intended to run locally first using standard Python tooling. GCP alignment is expressed through architecture, configuration design, pipeline boundaries, documentation, and future deployment references rather than live cloud dependencies in the early milestones.

## Portfolio Positioning

This project demonstrates financial crime ML engineering with a focus on scalable ML pipeline design, model governance, monitoring, and GCP-aligned production thinking. It is intended to show practical engineering judgement across fraud detection, AML analytics, anomaly detection, graph risk, NLP triage, MLOps, and regulatory control awareness.

## Current Status

Milestone 1 is a scaffold milestone. The repository contains package structure, configuration placeholders, documentation placeholders, diagram placeholders, CI setup, and minimal tests.

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

