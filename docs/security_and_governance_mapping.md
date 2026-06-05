# Security and Governance Mapping

## Purpose

This document maps the financial crime ML platform to cloud security, governance, and model risk controls that would be expected in a future productionised GCP implementation. It is documentation only and not production deployment.

## IAM and Least Privilege

Each pipeline component should run with the minimum permissions needed. Data ingestion, feature engineering, model training, scoring, monitoring, and governance evidence generation should use separate service accounts with clearly scoped IAM roles.

## Service Accounts

Service accounts should be named by workload and environment. Key creation should be avoided where possible. Workload identity and managed service identity patterns should be preferred over static credentials.

## Separation of Duties

Data engineers, ML engineers, model validators, investigators, and governance reviewers should have distinct responsibilities. Model developers should not be able to unilaterally approve production promotion.

## Secret Management

Secret Manager should hold any production secrets. This repository must not contain credentials, real secrets, private keys, or real customer data.

## Encryption

Cloud Storage, BigQuery, Vertex AI, Pub/Sub, and Dataflow support encryption at rest and in transit. Production designs should document encryption posture and any customer-managed encryption key requirements.

## Audit Logging

Cloud Logging, BigQuery audit logs, and application audit records should capture access, pipeline runs, scoring jobs, model approvals, monitoring reviews, evidence generation, and investigator actions.

## VPC and Service Perimeter Concepts

Sensitive workloads may require private networking, VPC Service Controls, restricted egress, Private Service Connect, and environment-specific perimeter design. This repository does not implement network controls.

## Data Classification

Financial crime data should be classified by sensitivity and retention requirements. The current repository uses synthetic data only, but a future production version would require privacy, compliance, and data handling review.

## Model Governance

Model governance should include model purpose, intended use, validation evidence, metric thresholds, limitations, monitoring obligations, and approval gates. The local model card, governance evidence pack, and model risk report demonstrate this pattern.

## Human-in-the-Loop Controls

High-risk outputs must route to a human-in-the-loop review workflow. The platform should provide risk scores, reason codes, and evidence, but should not make autonomous final decisions.

## Monitoring and Alerting

Monitoring should cover data drift, prediction drift, operational failures, missing evidence, alert volumes, and risk distribution changes. Cloud Monitoring and Cloud Logging can support operational alerting, while BigQuery can support analytical monitoring.

## Evidence Retention

Evidence should be retained in governed Cloud Storage buckets and BigQuery audit tables according to policy. Evidence should include configs, validation outputs, model metrics, score outputs, monitoring reports, and approval records.

## Non-Production Caveat

This project is a local-first synthetic data portfolio project. It is not a production financial crime system and does not deploy any live GCP resources.
