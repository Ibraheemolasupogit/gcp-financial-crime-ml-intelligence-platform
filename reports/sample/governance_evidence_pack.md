# Governance Evidence Pack

## Executive Summary

This evidence pack consolidates governance artefacts for the local synthetic financial crime ML
intelligence platform. It demonstrates documentation discipline, control evidence,
traceability, limitations, and human review expectations.

## Project Scope

The project covers synthetic data generation, validation, feature engineering, fraud
classification, AML scoring, anomaly detection, network risk modelling, NLP alert triage,
monitoring, and governance evidence. It remains local-first and synthetic-data-only.

## Synthetic Data Statement

No real customer data, credentials, production systems, or confidential financial crime
intelligence are used.

## Lifecycle Overview

Lifecycle stages: ['data_generation', 'data_validation', 'feature_engineering', 'supervised_fraud_model', 'aml_risk_scoring', 'anomaly_detection', 'network_risk_modelling', 'nlp_alert_triage', 'monitoring', 'governance']

## Controls Summary

Control status counts: {'passed': 19}

## Evidence Inventory

Available evidence artefacts: 31 of 31

## Model And Component Risk Assessment Summary

Production readiness counts: {'portfolio_demo_only': 9}

All components require human review and remain portfolio demonstration artefacts.

## Monitoring Evidence Summary

Monitoring evidence is available through model monitoring, drift, prediction, risk, and alert
quality summaries.

## Human Review And Decisioning Policy

No autonomous final decisioning is allowed. Outputs are triage and decision-support artefacts
only and require financial crime investigator review before any operational interpretation.

## Responsible AI Controls

Controls include synthetic data only, explainable reason codes, documented limitations, human
review, no real credentials, and no autonomous decisions.

## Limitations

This is not a production deployment, live monitoring service, model registry, dashboard, API,
agentic workflow, or regulatory reporting tool.

## Exclusions

The project excludes live GCP deployment, real data, live governance workflow, retraining
automation, and production decisioning.

## Auditability Notes

The evidence pack includes a deterministic audit log and lifecycle traceability map linking
inputs, outputs, configs, documentation, risks, and limitations.

## GCP Conceptual Mapping

The local evidence maps conceptually to BigQuery evidence tables, Vertex AI model metadata,
Cloud Logging audit trails, Cloud Storage artefacts, and Looker Studio governance reporting.
No live GCP integration is implemented.

## Next Governance Improvements

- Add formal approval workflow metadata.
- Add independent validation sign-off placeholders.
- Add versioned artefact hashes.
- Add release-level control attestations.
