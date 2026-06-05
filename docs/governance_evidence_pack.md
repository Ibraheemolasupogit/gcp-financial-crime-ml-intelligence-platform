# Governance Evidence Pack

The governance evidence pack consolidates controls, model risk assessments, evidence inventory, audit log, lifecycle traceability, and markdown reports for the synthetic financial crime ML platform.

## Evidence Pack Structure

- Governance control checklist
- Model and component risk assessment
- Evidence inventory
- Static audit log
- Lifecycle traceability summary
- Governance evidence markdown report
- Model risk management markdown report

## Audit Log Design

The audit log is a local JSONL artefact with deterministic timestamps. It records major lifecycle events from data generation through governance pack generation.

## Lifecycle Traceability

Traceability maps each stage to input artefacts, output artefacts, config artefacts, documentation artefacts, risk controls, and limitations.

## Human Review Requirement

The pack reinforces that all model, scoring, anomaly, network, and NLP outputs require human review and must not be used for autonomous final decisioning.

## Responsible AI Controls

The project remains synthetic-data-only, local-first, explainable, documented, and bounded by explicit limitations.

## Live Tooling Exclusion

This milestone does not implement live governance workflow tooling, model registry integration, GCP deployment, APIs, dashboards, retraining automation, LLM workflows, or agentic AI.
