from pathlib import Path

import pandas as pd

from financial_crime_ml.features.graph_features import (
    build_financial_crime_graph,
    edge_type_counts,
    generate_graph_features,
    node_type_counts,
)
from financial_crime_ml.ingestion.load_data import load_all_datasets
from financial_crime_ml.monitoring import run_network_risk_workflow
from financial_crime_ml.monitoring.network_summary import rank_high_risk_networks
from financial_crime_ml.scoring.network_risk_scorer import (
    NetworkRiskConfig,
    load_network_risk_config,
    score_network_risk,
)

VALID_BANDS = {"Critical", "High", "Medium", "Low", "Info"}
REQUIRED_COLUMNS = {
    "transaction_id",
    "account_id",
    "customer_id",
    "beneficiary_id",
    "device_id",
    "network_cluster_id",
    "network_cluster_size",
    "account_degree",
    "shared_device_count",
    "shared_beneficiary_count",
    "device_account_count",
    "beneficiary_account_count",
    "account_centrality",
    "network_risk_score",
    "network_risk_band",
    "network_risk_reasons",
}


def _config(tmp_path: Path) -> NetworkRiskConfig:
    return NetworkRiskConfig(
        output_path=tmp_path / "network_risk_scores.csv",
        high_risk_networks_output_path=tmp_path / "high_risk_networks.csv",
        network_summary_output_path=tmp_path / "network_summary.json",
        network_report_output_path=tmp_path / "network_risk_report.md",
        max_high_risk_networks=25,
        thresholds={
            "shared_device_account_threshold": 2,
            "shared_beneficiary_account_threshold": 2,
            "large_component_threshold": 5,
            "suspicious_cluster_rate_threshold": 0.2,
            "high_risk_network_score_threshold": 70,
        },
        scoring_weights={
            "shared_device": 20,
            "shared_beneficiary": 18,
            "suspicious_cluster": 20,
            "large_component": 10,
            "mule_network": 18,
            "high_risk_network": 14,
            "aml_high_or_critical": 10,
            "anomaly_flag": 8,
        },
    )


def _simple_datasets() -> dict[str, pd.DataFrame]:
    return {
        "customers": pd.DataFrame({"customer_id": ["C1", "C2"]}),
        "accounts": pd.DataFrame({"account_id": ["A1", "A2"], "customer_id": ["C1", "C2"]}),
        "beneficiaries": pd.DataFrame({"beneficiary_id": ["B1"]}),
        "devices": pd.DataFrame({"device_id": ["D1"]}),
        "transactions": pd.DataFrame(
            {
                "transaction_id": ["T1", "T2"],
                "account_id": ["A1", "A2"],
                "beneficiary_id": ["B1", "B1"],
                "device_id": ["D1", "D1"],
                "amount": [6000, 7000],
                "is_suspicious": [True, False],
            }
        ),
    }


def test_graph_construction_contains_expected_node_types() -> None:
    graph = build_financial_crime_graph(load_all_datasets())

    counts = node_type_counts(graph)
    assert {"customer", "account", "beneficiary", "device", "transaction"}.issubset(counts)


def test_graph_construction_contains_expected_edge_types() -> None:
    graph = build_financial_crime_graph(load_all_datasets())

    counts = edge_type_counts(graph)
    assert {"OWNS", "SENDS", "TO", "USED", "USES", "PAYS"}.issubset(counts)


def test_network_risk_workflow_runs_and_creates_outputs(tmp_path: Path) -> None:
    result = run_network_risk_workflow(config=_config(tmp_path))

    assert result["network_risk_scores_path"].exists()
    assert result["high_risk_networks_path"].exists()
    assert result["network_summary_path"].exists()
    assert result["network_report_path"].exists()


def test_required_output_columns_and_bands_exist(tmp_path: Path) -> None:
    result = run_network_risk_workflow(config=_config(tmp_path))
    scores = pd.read_csv(result["network_risk_scores_path"])

    assert REQUIRED_COLUMNS.issubset(scores.columns)
    assert set(scores["network_risk_band"]).issubset(VALID_BANDS)


def test_network_risk_reasons_are_generated(tmp_path: Path) -> None:
    result = run_network_risk_workflow(config=_config(tmp_path))
    scores = pd.read_csv(result["network_risk_scores_path"])

    assert scores["network_risk_reasons"].notna().all()
    assert (scores["network_risk_reasons"].str.len() > 0).all()


def test_shared_device_logic_on_known_case(tmp_path: Path) -> None:
    graph_features = generate_graph_features(_simple_datasets()).features
    scores = score_network_risk(graph_features, _config(tmp_path))

    assert graph_features["shared_device_flag"].eq(1).all()
    assert scores["network_risk_reasons"].str.contains("SHARED_DEVICE").any()


def test_shared_beneficiary_logic_on_known_case(tmp_path: Path) -> None:
    graph_features = generate_graph_features(_simple_datasets()).features
    scores = score_network_risk(graph_features, _config(tmp_path))

    assert graph_features["shared_beneficiary_flag"].eq(1).all()
    assert scores["network_risk_reasons"].str.contains("SHARED_BENEFICIARY").any()


def test_optional_joins_are_handled_gracefully(tmp_path: Path) -> None:
    graph_features = generate_graph_features(_simple_datasets()).features
    scores = score_network_risk(graph_features, _config(tmp_path))

    ranked = rank_high_risk_networks(scores, max_rows=2, optional_context=pd.DataFrame())

    assert len(ranked) == 2
    assert "aml_risk_score" in ranked.columns
    assert "anomaly_score" in ranked.columns
    assert "fraud_probability" in ranked.columns


def test_cli_underlying_network_workflow_can_run(tmp_path: Path) -> None:
    result = run_network_risk_workflow(config=_config(tmp_path))

    assert result["summary"]["node_count"] > 0


def test_network_config_can_be_loaded() -> None:
    config = load_network_risk_config()

    assert config.max_high_risk_networks > 0
    assert config.thresholds["shared_device_account_threshold"] >= 2
