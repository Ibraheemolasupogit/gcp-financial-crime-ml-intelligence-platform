# Model Risk Management Report

## Purpose

This report summarises model risk management controls for the synthetic financial crime ML
intelligence platform.

## Risk Governance Approach

The approach uses local evidence generation, transparent controls, model/component risk
assessment, deterministic audit logging, lifecycle traceability, and explicit human review
requirements.

## Component Inventory

Components assessed: ['synthetic data generator', 'data validation layer', 'feature engineering layer', 'fraud classifier', 'AML risk scoring', 'anomaly detection', 'network risk scoring', 'NLP alert triage', 'monitoring and drift reporting']

## Model Risk Assessment Summary

Residual risk counts: {'Low': 3, 'Medium': 6}

Production readiness remains portfolio demonstration only.

## Key Risks

['Feature logic may encode synthetic assumptions.', 'Keyword rules are limited', 'No live monitoring service', 'No production tuning', 'Not calibrated', 'Potential overfitting', 'Rule weights are illustrative', 'Simple component logic', 'Static local report only', 'Synthetic distribution', 'Synthetic labels', 'Synthetic network density', 'Synthetic patterns may be over-regular or unrealistic.', 'Synthetic text is regular', 'Unsupervised output may be hard to validate', 'Validation is local and file-based only.']

## Mitigating Controls

Controls include synthetic-data-only constraints, validation reports, model card, reason codes,
monitoring outputs, audit log, traceability, and human review requirements.

## Control Status Summary

{'passed': 19}

## Open Issues

- No live approval workflow.
- No independent model validation sign-off.
- No production monitoring integration.
- No artefact hashing or model registry.

## Human Review Requirement

All outputs require financial crime investigator or control-owner review before any operational
interpretation.

## Responsible AI Notes

The repository uses synthetic data, transparent rules where possible, documented limitations,
no autonomous final decisioning, and no real customer data.

## Financial Services Relevance

The pack demonstrates model risk awareness, auditability, control evidence, lifecycle
traceability, and responsible use expectations relevant to financial crime ML systems.

## GCP Governance Alignment Note

The local artefacts map conceptually to Vertex AI metadata, Cloud Logging audit trails,
BigQuery governance evidence tables, Cloud Storage artefacts, and Looker Studio governance
reporting. No live GCP governance tooling is implemented.
