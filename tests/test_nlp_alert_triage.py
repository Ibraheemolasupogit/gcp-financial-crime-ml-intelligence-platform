from pathlib import Path

import pandas as pd

from financial_crime_ml.models.nlp_alert_classifier import (
    VALID_TYPOLOGIES,
    classify_case_notes,
    classify_typology,
    load_nlp_config,
    preprocess_text,
)
from financial_crime_ml.monitoring.nlp_summary import run_nlp_triage_workflow
from financial_crime_ml.scoring.alert_triage import (
    NLPTriageConfig,
    load_nlp_triage_config,
    load_optional_enrichments,
)

VALID_BANDS = {"Critical", "High", "Medium", "Low", "Info"}
VALID_QUEUES = {
    "Financial crime investigation",
    "AML review",
    "Fraud review",
    "Network risk review",
    "Monitoring queue",
    "No immediate action",
}
REQUIRED_CASE_COLUMNS = {
    "case_note_id",
    "alert_id",
    "note_text",
    "predicted_typology",
    "typology_confidence",
    "typology_reasons",
    "original_typology_label",
}
REQUIRED_TRIAGE_COLUMNS = {
    "alert_id",
    "transaction_id",
    "account_id",
    "alert_type",
    "alert_severity",
    "alert_reason",
    "predicted_typology",
    "typology_confidence",
    "nlp_triage_score",
    "nlp_triage_band",
    "nlp_triage_reasons",
    "suggested_review_queue",
}


def test_text_preprocessing_handles_normal_and_missing_text() -> None:
    assert preprocess_text("  Mule   Account  ") == "mule account"
    assert preprocess_text(None) == ""


def test_typology_classification_returns_valid_labels() -> None:
    config = load_nlp_config()
    label, confidence, reasons = classify_typology("rapid movement of funds", config)

    assert label in VALID_TYPOLOGIES
    assert confidence > 0
    assert reasons


def test_known_case_typology_examples_classify_correctly() -> None:
    config = load_nlp_config()

    assert (
        classify_typology("behaviour consistent with mule-account typologies", config)[0]
        == "mule_account"
    )
    assert (
        classify_typology("unusual access pattern suggests account takeover", config)[0]
        == "account_takeover"
    )
    assert (
        classify_typology("repeated round-number payments indicate structuring", config)[0]
        == "structuring"
    )
    assert (
        classify_typology("exposure to a higher-risk destination country", config)[0]
        == "high_risk_jurisdiction"
    )


def test_case_note_classification_output_columns_exist() -> None:
    config = load_nlp_config()
    case_notes = pd.read_csv(config.case_notes_input_path).head(10)

    classifications = classify_case_notes(case_notes, config)

    assert REQUIRED_CASE_COLUMNS.issubset(classifications.columns)
    assert set(classifications["predicted_typology"]).issubset(VALID_TYPOLOGIES)


def test_nlp_workflow_runs_and_creates_outputs(tmp_path: Path) -> None:
    config = load_nlp_config()
    test_config = type(config)(
        alerts_input_path=config.alerts_input_path,
        case_notes_input_path=config.case_notes_input_path,
        case_note_classifications_output_path=tmp_path / "case_notes.csv",
        alert_triage_output_path=tmp_path / "triage.csv",
        nlp_summary_output_path=tmp_path / "summary.json",
        nlp_report_output_path=tmp_path / "report.md",
        typology_confidence_defaults=config.typology_confidence_defaults,
        typology_keywords=config.typology_keywords,
    )

    result = run_nlp_triage_workflow(test_config)

    assert result["case_note_classifications_path"].exists()
    assert result["alert_triage_path"].exists()
    assert result["nlp_summary_path"].exists()
    assert result["nlp_report_path"].exists()


def test_nlp_output_schema_bands_and_queues(tmp_path: Path) -> None:
    config = load_nlp_config()
    test_config = type(config)(
        alerts_input_path=config.alerts_input_path,
        case_notes_input_path=config.case_notes_input_path,
        case_note_classifications_output_path=tmp_path / "case_notes.csv",
        alert_triage_output_path=tmp_path / "triage.csv",
        nlp_summary_output_path=tmp_path / "summary.json",
        nlp_report_output_path=tmp_path / "report.md",
        typology_confidence_defaults=config.typology_confidence_defaults,
        typology_keywords=config.typology_keywords,
    )

    result = run_nlp_triage_workflow(test_config)
    triage = pd.read_csv(result["alert_triage_path"])

    assert REQUIRED_TRIAGE_COLUMNS.issubset(triage.columns)
    assert set(triage["nlp_triage_band"]).issubset(VALID_BANDS)
    assert set(triage["suggested_review_queue"]).issubset(VALID_QUEUES)


def test_optional_enrichment_files_are_handled_gracefully(tmp_path: Path) -> None:
    config = NLPTriageConfig(
        band_thresholds={"Critical": 90, "High": 70, "Medium": 40, "Low": 10, "Info": 0},
        typology_base_scores={"unknown": 20},
        enrichment_weights={},
        suggested_review_queue_mapping={"unknown": "Monitoring queue"},
        optional_enrichment_paths={"missing": tmp_path / "missing.csv"},
    )

    context, sources = load_optional_enrichments(config)

    assert context.empty
    assert sources == []


def test_cli_underlying_workflow_can_run(tmp_path: Path) -> None:
    config = load_nlp_config()
    test_config = type(config)(
        alerts_input_path=config.alerts_input_path,
        case_notes_input_path=config.case_notes_input_path,
        case_note_classifications_output_path=tmp_path / "case_notes.csv",
        alert_triage_output_path=tmp_path / "triage.csv",
        nlp_summary_output_path=tmp_path / "summary.json",
        nlp_report_output_path=tmp_path / "report.md",
        typology_confidence_defaults=config.typology_confidence_defaults,
        typology_keywords=config.typology_keywords,
    )

    result = run_nlp_triage_workflow(test_config)

    assert result["summary"]["alert_count"] > 0


def test_triage_config_can_be_loaded() -> None:
    config = load_nlp_triage_config()

    assert config.band_thresholds["High"] == 70
    assert config.suggested_review_queue_mapping["account_takeover"] == "Fraud review"
