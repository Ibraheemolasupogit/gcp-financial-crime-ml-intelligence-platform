"""Network risk workflow, summary, and report generation."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import networkx as nx
import pandas as pd

from financial_crime_ml.features.graph_features import (
    edge_type_counts,
    generate_graph_features,
    node_type_counts,
)
from financial_crime_ml.ingestion.load_data import DEFAULT_INPUT_PATH, REPO_ROOT, load_all_datasets
from financial_crime_ml.scoring.network_risk_scorer import (
    NetworkRiskConfig,
    load_network_risk_config,
    score_network_risk,
)

BAND_ORDER = {"Critical": 5, "High": 4, "Medium": 3, "Low": 2, "Info": 1}


def _optional_csv(path: str | Path) -> pd.DataFrame | None:
    resolved_path = Path(path)
    if not resolved_path.is_absolute():
        resolved_path = REPO_ROOT / resolved_path
    if not resolved_path.exists():
        return None
    return pd.read_csv(resolved_path)


def load_optional_network_context() -> pd.DataFrame:
    """Load optional fraud, AML, anomaly, and priority context when available."""
    context: pd.DataFrame | None = None
    optional_files = [
        (
            "outputs/sample/fraud_predictions.csv",
            ["transaction_id", "fraud_probability", "fraud_prediction"],
        ),
        (
            "outputs/sample/aml_risk_scores.csv",
            ["transaction_id", "aml_risk_score", "aml_risk_band", "aml_risk_reasons"],
        ),
        (
            "outputs/sample/anomaly_scores.csv",
            ["transaction_id", "anomaly_score", "is_anomaly", "anomaly_band"],
        ),
        (
            "outputs/sample/prioritised_alerts.csv",
            ["transaction_id", "priority_score", "priority_band", "recommended_action"],
        ),
    ]
    for path, columns in optional_files:
        dataset = _optional_csv(path)
        if dataset is None:
            continue
        selected_columns = [column for column in columns if column in dataset.columns]
        dataset = dataset[selected_columns].drop_duplicates("transaction_id")
        context = (
            dataset
            if context is None
            else context.merge(dataset, on="transaction_id", how="outer")
        )
    return context if context is not None else pd.DataFrame(columns=["transaction_id"])


def rank_high_risk_networks(
    network_risk_scores: pd.DataFrame,
    max_rows: int,
    optional_context: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Rank highest-risk transactions/accounts/clusters with optional context."""
    ranked = network_risk_scores.copy()
    if optional_context is not None and not optional_context.empty:
        ranked = ranked.merge(optional_context, on="transaction_id", how="left")
    if "aml_risk_score" not in ranked.columns:
        ranked["aml_risk_score"] = 0
    if "anomaly_score" not in ranked.columns:
        ranked["anomaly_score"] = 0.0
    if "fraud_probability" not in ranked.columns:
        ranked["fraud_probability"] = 0.0

    ranked["network_band_order"] = ranked["network_risk_band"].map(BAND_ORDER).fillna(0)
    ranked = ranked.sort_values(
        [
            "network_band_order",
            "network_risk_score",
            "aml_risk_score",
            "anomaly_score",
            "fraud_probability",
        ],
        ascending=[False, False, False, False, False],
    ).head(max_rows)
    return ranked.drop(columns=["network_band_order"]).reset_index(drop=True)


def _reason_counts(network_risk_scores: pd.DataFrame) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for reasons in network_risk_scores["network_risk_reasons"].fillna(""):
        for reason in str(reasons).split("; "):
            if reason and reason != "No network risk indicators":
                counter[reason] += 1
    return dict(counter.most_common(10))


def create_network_summary(
    graph: nx.Graph,
    network_risk_scores: pd.DataFrame,
    high_risk_networks: pd.DataFrame,
) -> dict[str, Any]:
    """Create JSON-serialisable network risk summary."""
    components = [len(component) for component in nx.connected_components(graph)]
    high_risk_count = int(network_risk_scores["network_risk_band"].isin({"Critical", "High"}).sum())
    aml_overlap = (
        int(high_risk_networks["aml_risk_band"].isin({"Critical", "High"}).sum())
        if "aml_risk_band" in high_risk_networks.columns
        else 0
    )
    anomaly_overlap = (
        int(high_risk_networks["is_anomaly"].fillna(False).astype(bool).sum())
        if "is_anomaly" in high_risk_networks.columns
        else 0
    )
    return {
        "node_count": int(graph.number_of_nodes()),
        "edge_count": int(graph.number_of_edges()),
        "node_type_counts": node_type_counts(graph),
        "edge_type_counts": edge_type_counts(graph),
        "connected_component_count": int(len(components)),
        "largest_component_size": int(max(components) if components else 0),
        "network_risk_band_counts": {
            band: int(count)
            for band, count in network_risk_scores["network_risk_band"].value_counts().items()
        },
        "top_network_risk_reasons": _reason_counts(network_risk_scores),
        "high_risk_network_count": high_risk_count,
        "aml_high_or_critical_overlap_count": aml_overlap,
        "anomaly_overlap_count": anomaly_overlap,
        "notes": [
            "Network risk uses a simple heterogeneous NetworkX graph.",
            "Shared devices and shared beneficiaries are deterministic network indicators.",
            "Outputs are synthetic-data-only and intended for local portfolio demonstration.",
        ],
    }


def generate_network_report(
    summary: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Write the markdown network risk report."""
    path = Path(output_path)
    content = f"""# Network Risk Report

## Purpose

This report summarises Milestone 7 graph/network risk modelling for synthetic financial
crime transaction data.

## Graph Design

The graph is a simple heterogeneous NetworkX graph connecting customers, accounts,
transactions, beneficiaries, and devices.

## Node Types

{summary["node_type_counts"]}

## Edge Types

Edges include customer OWNS account, account SENDS transaction, transaction TO beneficiary,
transaction USED device, account USES device, and account PAYS beneficiary.

Edge counts: {summary["edge_type_counts"]}

## Graph Size

- Nodes: {summary["node_count"]}
- Edges: {summary["edge_count"]}
- Connected components: {summary["connected_component_count"]}
- Largest component size: {summary["largest_component_size"]}

## Network Risk Results

- Network risk band counts: {summary["network_risk_band_counts"]}
- High-risk network count: {summary["high_risk_network_count"]}
- Top network risk reasons: {summary["top_network_risk_reasons"]}
- AML high/critical overlap count: {summary["aml_high_or_critical_overlap_count"]}
- Anomaly overlap count: {summary["anomaly_overlap_count"]}

## Limitations

This is a local, deterministic graph risk layer. It is not a production graph database,
entity resolution system, NLP workflow, agentic AI system, dashboard, API, or cloud deployment.

## Human Review Requirement

Network risk outputs are triage aids only. Real financial crime workflows require investigator
review, governance approval, validation, and operational controls before use.

## Synthetic Data Caveat

All data and relationships are synthetic. Results should not be interpreted as real-world
financial crime detection performance.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def run_network_risk_workflow(
    input_path: str | Path = DEFAULT_INPUT_PATH,
    config: NetworkRiskConfig | None = None,
) -> dict[str, Any]:
    """Run graph construction, network risk scoring, ranking, summary, and report."""
    resolved_config = config or load_network_risk_config()
    datasets = load_all_datasets(input_path)
    thresholds = resolved_config.thresholds
    graph_result = generate_graph_features(
        datasets,
        shared_device_account_threshold=int(thresholds.get("shared_device_account_threshold", 2)),
        shared_beneficiary_account_threshold=int(
            thresholds.get("shared_beneficiary_account_threshold", 2)
        ),
        large_component_threshold=int(thresholds.get("large_component_threshold", 25)),
        suspicious_cluster_rate_threshold=float(
            thresholds.get("suspicious_cluster_rate_threshold", 0.2)
        ),
    )
    optional_context = load_optional_network_context()
    network_risk_scores = score_network_risk(
        graph_result.features,
        resolved_config,
        optional_context=optional_context,
    )
    high_risk_networks = rank_high_risk_networks(
        network_risk_scores,
        max_rows=resolved_config.max_high_risk_networks,
        optional_context=optional_context,
    )
    summary = create_network_summary(graph_result.graph, network_risk_scores, high_risk_networks)

    resolved_config.output_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_config.high_risk_networks_output_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_config.network_summary_output_path.parent.mkdir(parents=True, exist_ok=True)

    network_risk_scores.to_csv(resolved_config.output_path, index=False)
    high_risk_networks.to_csv(resolved_config.high_risk_networks_output_path, index=False)
    resolved_config.network_summary_output_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    report_path = generate_network_report(summary, resolved_config.network_report_output_path)
    return {
        "summary": summary,
        "graph": graph_result.graph,
        "network_risk_scores_path": resolved_config.output_path,
        "high_risk_networks_path": resolved_config.high_risk_networks_output_path,
        "network_summary_path": resolved_config.network_summary_output_path,
        "network_report_path": report_path,
    }
