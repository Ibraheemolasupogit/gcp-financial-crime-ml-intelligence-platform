"""Lightweight rule-based NLP typology classification."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from financial_crime_ml.models.model_utils import (
    DEFAULT_MODEL_CONFIG_PATH,
    load_yaml_config,
    resolve_repo_path,
)

VALID_TYPOLOGIES = {
    "mule_account",
    "account_takeover",
    "high_risk_jurisdiction",
    "structuring",
    "rapid_movement",
    "shared_device",
    "shared_beneficiary",
    "low_risk",
    "unknown",
}

ORIGINAL_TYPOLOGY_MAP = {
    "mule_account_style_behaviour": "mule_account",
    "account_takeover_style_behaviour": "account_takeover",
    "high_risk_jurisdiction_exposure": "high_risk_jurisdiction",
    "round_number_payments": "structuring",
    "rapid_movement_of_funds": "rapid_movement",
    "high_transaction_velocity": "rapid_movement",
    "shared_device_behaviour": "shared_device",
    "new_beneficiary_risk": "shared_beneficiary",
    "unusual_amount_spike": "unknown",
}


@dataclass(frozen=True)
class NLPConfig:
    """Configuration for NLP alert triage."""

    alerts_input_path: Path
    case_notes_input_path: Path
    case_note_classifications_output_path: Path
    alert_triage_output_path: Path
    nlp_summary_output_path: Path
    nlp_report_output_path: Path
    typology_confidence_defaults: dict[str, float]
    typology_keywords: dict[str, list[str]]


def load_nlp_config(config_path: str | Path = DEFAULT_MODEL_CONFIG_PATH) -> NLPConfig:
    """Load NLP triage settings."""
    raw_config: dict[str, Any] = load_yaml_config(config_path).get("nlp_alert_triage", {})
    return NLPConfig(
        alerts_input_path=resolve_repo_path(
            raw_config.get("alerts_input_path", "data/sample/alerts.csv")
        ),
        case_notes_input_path=resolve_repo_path(
            raw_config.get("case_notes_input_path", "data/sample/case_notes.csv")
        ),
        case_note_classifications_output_path=resolve_repo_path(
            raw_config.get(
                "case_note_classifications_output_path",
                "outputs/sample/nlp_case_note_classifications.csv",
            )
        ),
        alert_triage_output_path=resolve_repo_path(
            raw_config.get("alert_triage_output_path", "outputs/sample/nlp_alert_triage.csv")
        ),
        nlp_summary_output_path=resolve_repo_path(
            raw_config.get("nlp_summary_output_path", "outputs/sample/nlp_summary.json")
        ),
        nlp_report_output_path=resolve_repo_path(
            raw_config.get("nlp_report_output_path", "reports/sample/nlp_alert_triage_report.md")
        ),
        typology_confidence_defaults=raw_config.get("typology_confidence_defaults", {}),
        typology_keywords=raw_config.get("typology_keywords", {}),
    )


def preprocess_text(text: object) -> str:
    """Lowercase text, normalise whitespace, and handle missing text safely."""
    if text is None or pd.isna(text):
        return ""
    normalised = str(text).lower()
    normalised = re.sub(r"\s+", " ", normalised).strip()
    return normalised


def classify_typology(text: object, config: NLPConfig) -> tuple[str, float, str]:
    """Classify text into a transparent typology label."""
    clean_text = preprocess_text(text)
    if not clean_text:
        return "unknown", config.typology_confidence_defaults.get("unknown", 0.35), "NO_TEXT"

    for typology, keywords in config.typology_keywords.items():
        matched_keywords = [keyword for keyword in keywords if keyword.lower() in clean_text]
        if matched_keywords:
            confidence = config.typology_confidence_defaults.get("matched_rule", 0.9)
            reasons = ", ".join(f"KEYWORD:{keyword}" for keyword in matched_keywords[:3])
            return typology, confidence, reasons

    return "unknown", config.typology_confidence_defaults.get("unknown", 0.35), "NO_RULE_MATCH"


def classify_case_notes(case_notes: pd.DataFrame, config: NLPConfig) -> pd.DataFrame:
    """Classify synthetic case-note typologies."""
    rows: list[dict[str, object]] = []
    for _, row in case_notes.iterrows():
        predicted, confidence, reasons = classify_typology(row.get("note_text"), config)
        original_label = row.get("typology_label")
        if predicted == "unknown" and original_label in ORIGINAL_TYPOLOGY_MAP:
            predicted = ORIGINAL_TYPOLOGY_MAP[str(original_label)]
            confidence = max(confidence, 0.75)
            reasons = f"ORIGINAL_LABEL_HINT:{original_label}"
        rows.append(
            {
                "case_note_id": row["case_note_id"],
                "alert_id": row["alert_id"],
                "note_text": row.get("note_text", ""),
                "predicted_typology": predicted,
                "typology_confidence": round(float(confidence), 4),
                "typology_reasons": reasons,
                "original_typology_label": original_label,
            }
        )
    return pd.DataFrame(rows)
