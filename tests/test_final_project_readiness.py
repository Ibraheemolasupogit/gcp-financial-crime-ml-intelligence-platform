"""Tests for final portfolio readiness artifacts."""

from __future__ import annotations

from pathlib import Path

import pytest

from financial_crime_ml.cli import main
from financial_crime_ml.project_readiness import (
    OBVIOUS_CREDENTIAL_FILES,
    README_REQUIRED_SECTIONS,
    REQUIRED_REPORTS,
    REQUIRED_SAMPLE_OUTPUTS,
    run_final_project_check,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_readme_has_required_sections() -> None:
    """README should expose the project clearly to portfolio reviewers."""
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8").lower()
    for section in README_REQUIRED_SECTIONS:
        assert f"## {section}".lower() in readme


def test_required_final_docs_exist() -> None:
    """Final polish documentation should exist."""
    required_docs = [
        "docs/end_to_end_walkthrough.md",
        "docs/architecture_narrative.md",
        "docs/sample_outputs_guide.md",
        "docs/repository_quality_checklist.md",
        "docs/index.md",
    ]
    for doc_path in required_docs:
        assert (PROJECT_ROOT / doc_path).exists()


def test_final_scripts_exist() -> None:
    """Demo runner and final project checker should exist."""
    assert (PROJECT_ROOT / "scripts/run_all_local.sh").exists()
    assert (PROJECT_ROOT / "scripts/final_project_check.py").exists()


def test_no_obvious_credential_files_exist() -> None:
    """Repository should not contain obvious credential files."""
    for credential_path in OBVIOUS_CREDENTIAL_FILES:
        assert not (PROJECT_ROOT / credential_path).exists()


def test_generated_outputs_and_reports_expected_from_prior_milestones_exist() -> None:
    """Sample outputs and reports should be present for portfolio review."""
    for output_path in REQUIRED_SAMPLE_OUTPUTS:
        assert (PROJECT_ROOT / output_path).exists(), f"Missing output: {output_path}"
    for report_path in REQUIRED_REPORTS:
        assert (PROJECT_ROOT / report_path).exists(), f"Missing report: {report_path}"


def test_final_project_check_runs_successfully() -> None:
    """Final project readiness check should pass."""
    result = run_final_project_check(PROJECT_ROOT)
    assert result.passed
    assert result.status == "passed"
    assert result.issues == []


def test_cli_final_check_command_runs(capsys: pytest.CaptureFixture[str]) -> None:
    """CLI should expose the final project check command."""
    main(["final-check"])
    output = capsys.readouterr().out
    assert "Final project check status: passed" in output
    assert "Checks run:" in output
