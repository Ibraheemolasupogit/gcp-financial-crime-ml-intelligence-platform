"""Run Milestone 8 NLP alert triage outputs."""

from financial_crime_ml.monitoring.nlp_summary import run_nlp_triage_workflow


def main() -> None:
    """Run NLP triage and print a concise summary."""
    result = run_nlp_triage_workflow()
    summary = result["summary"]
    print("NLP alert triage completed.")
    print(f"Alerts triaged: {summary['alert_count']}")
    print(f"Case notes classified: {summary['case_note_count']}")
    print(f"Enrichment sources used: {', '.join(summary['enrichment_sources_used'])}")
    print(f"Case classifications written to: {result['case_note_classifications_path']}")
    print(f"Alert triage written to: {result['alert_triage_path']}")
    print(f"Summary written to: {result['nlp_summary_path']}")
    print(f"Report written to: {result['nlp_report_path']}")


if __name__ == "__main__":
    main()
