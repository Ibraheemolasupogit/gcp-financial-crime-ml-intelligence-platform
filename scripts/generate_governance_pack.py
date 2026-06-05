"""Generate Milestone 10 governance evidence pack outputs."""

from financial_crime_ml.governance import run_governance_pack_workflow


def main() -> None:
    """Run governance pack generation and print a concise summary."""
    result = run_governance_pack_workflow()
    print("Governance evidence pack generated.")
    print(f"Controls: {result['control_count']}")
    print(f"Risk assessments: {result['assessment_count']}")
    print(f"Evidence items: {result['evidence_item_count']}")
    print(f"Checklist written to: {result['control_checklist_path']}")
    print(f"Risk assessment written to: {result['model_risk_assessment_path']}")
    print(f"Evidence inventory written to: {result['evidence_inventory_path']}")
    print(f"Audit log written to: {result['audit_log_path']}")
    print(f"Traceability written to: {result['lifecycle_traceability_path']}")
    print(f"Evidence pack written to: {result['governance_evidence_pack_path']}")
    print(f"Model risk report written to: {result['model_risk_management_report_path']}")


if __name__ == "__main__":
    main()
