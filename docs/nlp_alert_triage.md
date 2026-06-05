# NLP Alert Triage

Milestone 8 adds lightweight NLP alert triage and case-note typology classification for synthetic financial crime alerts.

## Purpose

Financial crime teams often review alert reasons and case notes to determine whether an alert belongs in an AML, fraud, network risk, or monitoring queue. This milestone demonstrates local text analytics for typology tagging and triage support.

## Input Datasets

```text
data/sample/alerts.csv
data/sample/case_notes.csv
```

Optional enrichment may use prioritised alerts, AML scores, anomaly scores, and network risk scores when those files are available.

## Preprocessing Design

The workflow lowercases text, normalises whitespace, handles missing text safely, and preserves useful financial crime terms for keyword matching.

## Typology Labels

Supported labels:

- `mule_account`
- `account_takeover`
- `high_risk_jurisdiction`
- `structuring`
- `rapid_movement`
- `shared_device`
- `shared_beneficiary`
- `low_risk`
- `unknown`

## Triage Scoring

Alert triage scores combine the predicted typology, keyword confidence, alert severity, and optional enrichment from AML, anomaly, network, and prioritised alert outputs. Bands are `Critical`, `High`, `Medium`, `Low`, and `Info`.

## Outputs

```text
outputs/sample/nlp_case_note_classifications.csv
outputs/sample/nlp_alert_triage.csv
outputs/sample/nlp_summary.json
reports/sample/nlp_alert_triage_report.md
```

## Run Locally

```bash
python scripts/run_nlp_triage.py
```

Or use the CLI:

```bash
python -m financial_crime_ml.cli run-nlp-triage
```

## Limitations

This milestone does not implement LLMs, agents, deep learning, Hugging Face transformers, dashboards, cloud deployment, model registry, or live APIs. It is a lightweight local workflow for synthetic text only.
