"""Documentation validation utilities for architecture blueprint artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REQUIRED_DOCS = [
    Path("docs/gcp_reference_architecture.md"),
    Path("docs/distributed_systems_design.md"),
    Path("docs/deployment_blueprint.md"),
    Path("docs/security_and_governance_mapping.md"),
    Path("docs/operations_runbook.md"),
    Path("docs/gcp_service_mapping.md"),
]

REQUIRED_DIAGRAMS = [
    Path("diagrams/gcp_reference_architecture.mmd"),
    Path("diagrams/ml_lifecycle.mmd"),
    Path("diagrams/governance_workflow.mmd"),
    Path("diagrams/distributed_dataflow.mmd"),
    Path("diagrams/deployment_phases.mmd"),
]

REQUIRED_PHRASES = [
    "Vertex AI",
    "BigQuery",
    "Pub/Sub",
    "Dataflow",
    "Cloud Storage",
    "Cloud Logging",
    "human-in-the-loop",
    "synthetic data",
    "not production deployment",
]


@dataclass(frozen=True)
class DocumentationValidationResult:
    """Simple validation result for architecture documentation."""

    status: str
    docs_checked: int
    diagrams_checked: int
    issues: list[str]

    @property
    def passed(self) -> bool:
        """Return whether validation passed."""
        return self.status == "passed"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_architecture_docs(repo_root: Path | str = ".") -> DocumentationValidationResult:
    """Validate required GCP architecture documentation and Mermaid diagrams."""
    root = Path(repo_root)
    issues: list[str] = []

    for doc_path in REQUIRED_DOCS:
        full_path = root / doc_path
        if not full_path.exists():
            issues.append(f"Missing required document: {doc_path}")
            continue
        if not _read_text(full_path).strip():
            issues.append(f"Required document is empty: {doc_path}")

    for diagram_path in REQUIRED_DIAGRAMS:
        full_path = root / diagram_path
        if not full_path.exists():
            issues.append(f"Missing required Mermaid diagram: {diagram_path}")
            continue
        content = _read_text(full_path).strip()
        if not content:
            issues.append(f"Required Mermaid diagram is empty: {diagram_path}")
        if not content.startswith(("flowchart", "graph", "sequenceDiagram")):
            issues.append(
                f"Mermaid diagram does not start with a supported diagram type: {diagram_path}"
            )

    combined_doc_text = "\n".join(
        _read_text(root / doc_path) for doc_path in REQUIRED_DOCS if (root / doc_path).exists()
    )
    combined_lower = combined_doc_text.lower()
    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in combined_lower:
            issues.append(f"Missing required phrase across architecture docs: {phrase}")

    status = "passed" if not issues else "failed"
    return DocumentationValidationResult(
        status=status,
        docs_checked=len(REQUIRED_DOCS),
        diagrams_checked=len(REQUIRED_DIAGRAMS),
        issues=issues,
    )
