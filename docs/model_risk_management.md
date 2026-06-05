# Model Risk Management

Milestone 10 adds model risk management evidence across the full synthetic financial crime ML lifecycle.

## Purpose

Model risk management provides structure for documenting purpose, scope, assumptions, limitations, controls, evidence, monitoring, and human review requirements. In financial crime ML, this discipline helps prevent misuse of model outputs and supports auditability.

## Governance Controls

The repository uses controls covering data governance, synthetic data caveats, validation, feature engineering, model performance, AML scoring transparency, anomaly explainability, network explainability, NLP explainability, monitoring, audit logging, responsible AI, reproducibility, and security hygiene.

## Human Review Requirement

All outputs are triage or decision-support artefacts. Autonomous final decisioning is not allowed. A real workflow would require financial crime investigator review, governance approval, and formal model validation.

## Responsible AI Controls

Controls include synthetic-data-only development, transparent reason codes, documented limitations, no real credentials, no real customer data, and no autonomous final decisions.

## Limitations

This milestone does not implement live governance tooling, model registry integration, dashboards, APIs, retraining automation, or GCP deployment.

## Evidence Outputs

```text
outputs/sample/governance_control_checklist.json
outputs/sample/model_risk_assessment.json
outputs/sample/evidence_inventory.json
outputs/sample/audit_log.jsonl
outputs/sample/lifecycle_traceability.json
reports/sample/governance_evidence_pack.md
reports/sample/model_risk_management_report.md
```
