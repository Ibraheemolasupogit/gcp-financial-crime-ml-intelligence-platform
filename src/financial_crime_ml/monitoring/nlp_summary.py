"""NLP alert triage workflow, summary, and report generation."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from financial_crime_ml.models.nlp_alert_classifier import (
    NLPConfig,
    classify_case_notes,
    load_nlp_config,
)
from financial_crime_ml.scoring.alert_triage import (
    load_nlp_triage_config,
    load_optional_enrichments,
    score_alert_triage,
)


def _reason_counts(triage: pd.DataFrame) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for reasons in triage["nlp_triage_reasons"].fillna(""):
        for reason in str(reasons).split("; "):
            if reason:
                counter[reason] += 1
    return dict(counter.most_common(10))


def create_nlp_summary(
    alerts: pd.DataFrame,
    case_notes: pd.DataFrame,
    classifications: pd.DataFrame,
    triage: pd.DataFrame,
    enrichment_sources_used: list[str],
) -> dict[str, Any]:
    """Create a JSON-serialisable NLP summary."""
    return {
        "alert_count": int(len(alerts)),
        "case_note_count": int(len(case_notes)),
        "typology_distribution": {
            label: int(count)
            for label, count in classifications["predicted_typology"].value_counts().items()
        },
        "triage_band_counts": {
            band: int(count) for band, count in triage["nlp_triage_band"].value_counts().items()
        },
        "top_triage_reasons": _reason_counts(triage),
        "enrichment_sources_used": enrichment_sources_used,
        "notes": [
            "NLP triage is lightweight and rule-based.",
            "No LLMs, transformers, agents, dashboards, or APIs are used.",
            "Outputs are synthetic-data-only and intended for local portfolio demonstration.",
        ],
    }


def generate_nlp_report(summary: dict[str, Any], output_path: str | Path) -> Path:
    """Write the markdown NLP triage report."""
    path = Path(output_path)
    content = f"""# NLP Alert Triage Report

## Purpose

This report summarises Milestone 8 lightweight NLP alert triage and case-note typology
classification for synthetic financial crime alerts.

## Input Datasets

- `data/sample/alerts.csv`
- `data/sample/case_notes.csv`

## Preprocessing Approach

Text is lowercased, whitespace-normalised, and handled safely when missing. Financial crime
terms are preserved for transparent keyword matching.

## Typology Labels

Labels include mule account, account takeover, high-risk jurisdiction, structuring, rapid
movement, shared device, shared beneficiary, low risk, and unknown.

## Classification Approach

The classifier is deterministic and rule-based using configured keyword patterns. Synthetic
case-note labels may be used as helper context when no keyword rule matches.

## Results

- Alerts triaged: {summary["alert_count"]}
- Case notes classified: {summary["case_note_count"]}
- Typology distribution: {summary["typology_distribution"]}
- Triage band distribution: {summary["triage_band_counts"]}
- Top reason codes: {summary["top_triage_reasons"]}
- Enrichment sources used: {summary["enrichment_sources_used"]}

## Limitations

This milestone does not implement LLMs, agentic AI, deep learning, transformers, dashboards,
cloud deployment, model registry, or live APIs. It is a lightweight synthetic-data workflow.

## Human Review Requirement

NLP triage outputs are investigation support only. Real financial crime workflows require
human review, escalation controls, validation, and governance approval before operational use.

## Synthetic Data Caveat

All alerts and notes are synthetic. Results should not be interpreted as production financial
crime NLP performance.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def run_nlp_triage_workflow(config: NLPConfig | None = None) -> dict[str, Any]:
    """Run case-note classification, alert triage, summary, and report generation."""
    resolved_config = config or load_nlp_config()
    triage_config = load_nlp_triage_config()
    alerts = pd.read_csv(resolved_config.alerts_input_path)
    case_notes = pd.read_csv(resolved_config.case_notes_input_path)
    classifications = classify_case_notes(case_notes, resolved_config)
    enrichment_context, sources_used = load_optional_enrichments(triage_config)
    triage = score_alert_triage(alerts, classifications, triage_config, enrichment_context)
    summary = create_nlp_summary(alerts, case_notes, classifications, triage, sources_used)

    resolved_config.case_note_classifications_output_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_config.alert_triage_output_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_config.nlp_summary_output_path.parent.mkdir(parents=True, exist_ok=True)

    classifications.to_csv(resolved_config.case_note_classifications_output_path, index=False)
    triage.to_csv(resolved_config.alert_triage_output_path, index=False)
    resolved_config.nlp_summary_output_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    report_path = generate_nlp_report(summary, resolved_config.nlp_report_output_path)

    return {
        "summary": summary,
        "case_note_classifications_path": resolved_config.case_note_classifications_output_path,
        "alert_triage_path": resolved_config.alert_triage_output_path,
        "nlp_summary_path": resolved_config.nlp_summary_output_path,
        "nlp_report_path": report_path,
    }
