"""Tests for GCP reference architecture documentation artifacts."""

from __future__ import annotations

from pathlib import Path

import pytest

from financial_crime_ml.cli import main
from financial_crime_ml.docs_validation import (
    REQUIRED_DIAGRAMS,
    REQUIRED_DOCS,
    REQUIRED_PHRASES,
    validate_architecture_docs,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_required_architecture_docs_exist() -> None:
    """Required architecture documents should be present."""
    for doc_path in REQUIRED_DOCS:
        assert (PROJECT_ROOT / doc_path).exists(), f"Missing document: {doc_path}"


def test_required_mermaid_diagrams_exist_and_are_non_empty() -> None:
    """Required Mermaid diagrams should exist and contain Mermaid text."""
    for diagram_path in REQUIRED_DIAGRAMS:
        content = (PROJECT_ROOT / diagram_path).read_text(encoding="utf-8").strip()
        assert content, f"Diagram is empty: {diagram_path}"
        assert content.startswith(("flowchart", "graph", "sequenceDiagram"))


def test_docs_contain_required_gcp_service_references() -> None:
    """Architecture docs should include required GCP and governance references."""
    combined_text = "\n".join(
        (PROJECT_ROOT / doc_path).read_text(encoding="utf-8") for doc_path in REQUIRED_DOCS
    ).lower()
    for phrase in REQUIRED_PHRASES:
        assert phrase.lower() in combined_text


def test_docs_contain_synthetic_data_and_non_production_caveats() -> None:
    """Docs should make demo boundaries explicit."""
    combined_text = "\n".join(
        (PROJECT_ROOT / doc_path).read_text(encoding="utf-8") for doc_path in REQUIRED_DOCS
    ).lower()
    assert "synthetic data" in combined_text
    assert "not production deployment" in combined_text
    assert "does not create" in combined_text


def test_architecture_docs_validation_passes() -> None:
    """Documentation validation should pass for the repository."""
    result = validate_architecture_docs(PROJECT_ROOT)
    assert result.passed
    assert result.status == "passed"
    assert result.docs_checked == len(REQUIRED_DOCS)
    assert result.diagrams_checked == len(REQUIRED_DIAGRAMS)
    assert result.issues == []


def test_cli_validate_docs_command_runs(capsys: pytest.CaptureFixture[str]) -> None:
    """CLI should expose the documentation validation command."""
    main(["validate-docs"])
    output = capsys.readouterr().out
    assert "Documentation validation status: passed" in output
    assert "Documents checked:" in output
    assert "Mermaid diagrams checked:" in output
