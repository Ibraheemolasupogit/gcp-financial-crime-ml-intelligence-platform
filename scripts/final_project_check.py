"""Run final portfolio readiness checks."""

from __future__ import annotations

from pathlib import Path

from financial_crime_ml.project_readiness import run_final_project_check

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Run final checks and print a concise pass/fail summary."""
    result = run_final_project_check(PROJECT_ROOT)
    print(f"Final project check status: {result.status}")
    print(f"Checks run: {result.checks_run}")
    print(f"Issues: {len(result.issues)}")
    for issue in result.issues:
        print(f"- {issue}")
    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
