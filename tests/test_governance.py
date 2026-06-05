import json
from pathlib import Path

from financial_crime_ml.governance.control_checklist import VALID_CONTROL_STATUSES
from financial_crime_ml.governance.governance_workflow import run_governance_pack_workflow
from financial_crime_ml.governance.model_risk_assessment import VALID_READINESS_STATUSES

REQUIRED_CONTROL_KEYS = {
    "control_id",
    "control_name",
    "control_category",
    "control_description",
    "evidence_source",
    "status",
    "owner_role",
    "review_frequency",
    "notes",
}
REQUIRED_ASSESSMENT_KEYS = {
    "model_or_component_name",
    "component_type",
    "purpose",
    "inherent_risk_level",
    "residual_risk_level",
    "key_risks",
    "mitigating_controls",
    "evidence_sources",
    "human_review_required",
    "production_readiness_status",
    "limitations",
}
REQUIRED_STAGES = {
    "data_generation",
    "data_validation",
    "feature_engineering",
    "supervised_fraud_model",
    "aml_risk_scoring",
    "anomaly_detection",
    "network_risk_modelling",
    "nlp_alert_triage",
    "monitoring",
    "governance",
}


def test_governance_pack_workflow_runs_successfully() -> None:
    result = run_governance_pack_workflow()

    assert result["control_count"] >= 10
    assert result["assessment_count"] >= 9


def test_governance_outputs_are_created() -> None:
    result = run_governance_pack_workflow()

    assert result["control_checklist_path"].exists()
    assert result["model_risk_assessment_path"].exists()
    assert result["evidence_inventory_path"].exists()
    assert result["audit_log_path"].exists()
    assert result["lifecycle_traceability_path"].exists()
    assert result["governance_evidence_pack_path"].exists()
    assert result["model_risk_management_report_path"].exists()


def test_required_keys_exist_in_json_outputs() -> None:
    result = run_governance_pack_workflow()
    controls = json.loads(result["control_checklist_path"].read_text(encoding="utf-8"))
    assessments = json.loads(result["model_risk_assessment_path"].read_text(encoding="utf-8"))

    assert REQUIRED_CONTROL_KEYS.issubset(controls[0])
    assert REQUIRED_ASSESSMENT_KEYS.issubset(assessments[0])


def test_control_statuses_are_valid() -> None:
    result = run_governance_pack_workflow()
    controls = json.loads(result["control_checklist_path"].read_text(encoding="utf-8"))

    assert {control["status"] for control in controls}.issubset(VALID_CONTROL_STATUSES)


def test_production_readiness_statuses_are_valid() -> None:
    result = run_governance_pack_workflow()
    assessments = json.loads(result["model_risk_assessment_path"].read_text(encoding="utf-8"))

    assert {assessment["production_readiness_status"] for assessment in assessments}.issubset(
        VALID_READINESS_STATUSES
    )


def test_evidence_inventory_includes_important_artifacts() -> None:
    result = run_governance_pack_workflow()
    inventory = json.loads(result["evidence_inventory_path"].read_text(encoding="utf-8"))
    artifact_paths = {item["artifact_path"] for item in inventory}

    assert "outputs/sample/model_metrics.json" in artifact_paths
    assert "outputs/sample/monitoring_summary.json" in artifact_paths
    assert "reports/sample/model_card.md" in artifact_paths


def test_lifecycle_traceability_includes_all_major_stages() -> None:
    result = run_governance_pack_workflow()
    traceability = json.loads(result["lifecycle_traceability_path"].read_text(encoding="utf-8"))

    assert REQUIRED_STAGES.issubset(traceability)


def test_audit_log_contains_jsonl_records() -> None:
    result = run_governance_pack_workflow()
    lines = result["audit_log_path"].read_text(encoding="utf-8").strip().splitlines()
    first_record = json.loads(lines[0])

    assert lines
    assert first_record["actor"] == "local_demo_pipeline"
    assert first_record["status"] == "completed"


def test_cli_underlying_governance_workflow_can_run() -> None:
    result = run_governance_pack_workflow()

    assert Path(result["governance_evidence_pack_path"]).exists()
