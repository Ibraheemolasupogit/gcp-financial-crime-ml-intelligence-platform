# Deployment Blueprint

This blueprint describes a phased path from the local demo repository to a controlled GCP-aligned implementation. It is not production deployment and does not create Terraform, Cloud Build pipelines, BigQuery tables, Pub/Sub topics, Dataflow jobs, Vertex AI resources, service accounts, secrets, APIs, or dashboards.

## Phase 0: Local Demo Repository

| Area | Description |
| --- | --- |
| Objective | Demonstrate the synthetic ML lifecycle locally. |
| GCP services involved | None; conceptually aligned to Cloud Storage, BigQuery, Vertex AI, Cloud Logging, and Dataflow. |
| Inputs | Synthetic CSVs, local configs, local scripts. |
| Outputs | Local features, model metrics, scores, reports, monitoring summaries, governance evidence. |
| Controls | Synthetic data caveat, tests, governance evidence pack, documentation. |
| Validation gates | Ruff, pytest, data validation report, governance checklist. |
| Rollback considerations | Git revert or regenerate deterministic local artifacts. |

## Phase 1: GCP Storage and BigQuery Foundation

| Area | Description |
| --- | --- |
| Objective | Establish governed landing and analytics storage. |
| GCP services involved | Cloud Storage, BigQuery, Dataplex-style governance, Cloud Logging. |
| Inputs | Approved non-production files or synthetic extracts. |
| Outputs | Curated BigQuery tables and data quality logs. |
| Controls | IAM least privilege, encryption, retention, schema validation, audit logging. |
| Validation gates | Table schema checks, row counts, missing value checks, access review. |
| Rollback considerations | Revert table migrations, restore prior partitions, retain rejected records. |

## Phase 2: Batch Feature Engineering

| Area | Description |
| --- | --- |
| Objective | Generate governed transaction, account, beneficiary, device, and typology features. |
| GCP services involved | BigQuery, Dataflow, Cloud Run jobs, Cloud Scheduler. |
| Inputs | Curated BigQuery source tables. |
| Outputs | BigQuery feature tables / Vertex AI Feature Store concept. |
| Controls | Config versioning, lineage capture, deterministic transforms, quality checks. |
| Validation gates | Feature row counts, null checks, range checks, schema compatibility. |
| Rollback considerations | Restore previous feature table partitions or rerun with prior config. |

## Phase 3: Vertex AI Training and Evaluation

| Area | Description |
| --- | --- |
| Objective | Train and evaluate the fraud classifier using governed features. |
| GCP services involved | Vertex AI Training, Vertex AI Experiments, Model Registry metadata concept, Cloud Storage. |
| Inputs | Feature tables, model config, training container. |
| Outputs | Model artifact, metrics, model card, validation evidence. |
| Controls | Train/test split documentation, excluded columns, metric thresholds, model approval gate. |
| Validation gates | Model metrics, bias and limitation notes, model risk assessment. |
| Rollback considerations | Retain previous approved model and block promotion. |

## Phase 4: Batch Scoring and Alert Prioritisation

| Area | Description |
| --- | --- |
| Objective | Produce fraud predictions, AML scores, anomaly scores, network scores, NLP triage, and prioritised alerts. |
| GCP services involved | Vertex AI batch prediction, BigQuery scheduled queries, Dataflow, Cloud Run jobs. |
| Inputs | Feature tables, approved model artifact, risk scoring config. |
| Outputs | Risk score tables, reason codes, investigator queue tables. |
| Controls | Human-in-the-loop review, reason-code transparency, no autonomous final decisioning. |
| Validation gates | Score distribution checks, high-priority alert review, reconciliation counts. |
| Rollback considerations | Disable latest scoring run, restore previous scoring partitions. |

## Phase 5: Monitoring and Governance Evidence

| Area | Description |
| --- | --- |
| Objective | Monitor data drift, prediction drift, alert quality, and governance evidence completeness. |
| GCP services involved | Vertex AI Model Monitoring concept, Cloud Logging, BigQuery monitoring tables, Cloud Storage. |
| Inputs | Feature tables, predictions, risk scores, alerts, monitoring config. |
| Outputs | Monitoring reports, audit logs, evidence inventory. |
| Controls | Review frequencies, control checklist, evidence retention, incident escalation. |
| Validation gates | Drift thresholds, missing evidence checks, monitoring status. |
| Rollback considerations | Pause model promotion or scoring until monitoring exceptions are reviewed. |

## Phase 6: Controlled Dashboard and Investigator Review

| Area | Description |
| --- | --- |
| Objective | Present prioritised alerts and evidence to authorised investigators. |
| GCP services involved | BigQuery, Looker Studio source layer concept, Cloud Logging, IAM. |
| Inputs | Prioritised alert tables, reason codes, evidence links. |
| Outputs | Reviewed cases, analyst decisions, feedback labels. |
| Controls | Role-based access, separation of duties, audit logging, human review requirement. |
| Validation gates | Access review, workflow testing, evidence capture checks. |
| Rollback considerations | Disable dashboard access or revert to previous alert table version. |

## Phase 7: Optional Streaming Extension

| Area | Description |
| --- | --- |
| Objective | Add near-real-time ingestion and risk scoring where latency requirements justify it. |
| GCP services involved | Pub/Sub, Dataflow streaming, BigQuery, Cloud Run, Cloud Logging. |
| Inputs | Transaction and alert events. |
| Outputs | Streaming features, risk events, operational logs. |
| Controls | Dead-letter queues, replayability, idempotency, monitoring alerts. |
| Validation gates | Latency, throughput, schema compatibility, failure recovery tests. |
| Rollback considerations | Route traffic back to batch scoring and pause streaming consumers. |

## Deployment Caveat

This repository documents a phased blueprint only. It intentionally avoids live infrastructure, credentials, service accounts, Terraform, deployment automation, and production data.
