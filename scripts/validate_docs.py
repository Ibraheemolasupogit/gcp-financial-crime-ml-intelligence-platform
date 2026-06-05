"""Validate GCP architecture documentation artifacts."""

from __future__ import annotations

from pathlib import Path

from financial_crime_ml.docs_validation import validate_architecture_docs

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Run documentation validation and print a concise summary."""
    result = validate_architecture_docs(PROJECT_ROOT)
    print(f"Documentation validation status: {result.status}")
    print(f"Documents checked: {result.docs_checked}")
    print(f"Mermaid diagrams checked: {result.diagrams_checked}")
    print(f"Issues: {len(result.issues)}")
    for issue in result.issues:
        print(f"- {issue}")
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
