# Operations Runbook

## Purpose

This runbook outlines operational checks for a future productionised GCP version of the financial crime ML platform. It is a planning document only and not production deployment.

## Daily Checks

- Confirm ingestion jobs completed and wrote expected row counts.
- Review data validation exceptions and dead-letter records.
- Confirm batch scoring jobs completed successfully.
- Review high-priority alert counts and investigator queue volumes.
- Check Cloud Logging and Cloud Monitoring for pipeline errors.

## Weekly Checks

- Review data drift and prediction/risk distribution monitoring.
- Review alert quality trends and duplicate alert counts.
- Confirm governance evidence artifacts were generated and retained.
- Review access logs for unusual activity.
- Confirm model and scoring configuration versions are documented.

## Model Monitoring Review

Model monitoring should cover fraud probability distributions, AML risk bands, anomaly rates, network risk bands, and NLP triage distributions. Material changes should trigger investigation before model or rule changes are promoted.

## Data Drift Review

Feature drift should be reviewed by feature owners and model governance stakeholders. Drift alone should not automatically trigger retraining; it should prompt investigation, impact analysis, and validation planning.

## Alert Quality Review

Alert quality review should inspect priority band distribution, reason code concentration, duplicate transaction alerts, and human investigation feedback where available.

## Governance Evidence Review

Governance reviewers should verify that model cards, monitoring reports, model risk assessments, audit logs, lifecycle traceability, and evidence inventory entries are complete and accessible.

## Failed Pipeline Handling

Failed jobs should be triaged by severity. Operational response should capture the failed component, affected artifacts, retry status, root cause, remediation, and whether investigator queues or reports were affected.

## Incident Escalation

Incidents involving missing data, incomplete scoring, broken monitoring, suspicious access, or evidence gaps should be escalated to engineering, security, governance, and business owners as appropriate.

## Retraining Trigger Considerations

Possible retraining triggers include sustained drift, degraded model performance, typology changes, major data source changes, investigator feedback, or governance review findings. This repository does not implement retraining automation.

## Human Review Workflow

High and Critical alerts should be reviewed by authorised investigators. Outputs should include reason codes and supporting evidence. The platform must not make autonomous final decisions.

## Audit Evidence Review

Audit evidence should include source artifacts, validation results, feature summaries, metrics, score outputs, monitoring reports, governance reports, and approval records. Evidence retention should align with policy.

## Limitations

This runbook is based on synthetic data and a local-first implementation. A production runbook would require service-level objectives, ownership matrices, escalation contacts, change management integration, and validated GCP operational procedures.
