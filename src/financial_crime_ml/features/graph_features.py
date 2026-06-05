"""NetworkX graph construction and graph feature generation."""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx
import pandas as pd


@dataclass(frozen=True)
class GraphFeatureResult:
    """Graph plus transaction-level graph feature table."""

    graph: nx.Graph
    features: pd.DataFrame


def _node_id(node_type: str, raw_id: str) -> str:
    return f"{node_type}:{raw_id}"


def build_financial_crime_graph(datasets: dict[str, pd.DataFrame]) -> nx.Graph:
    """Build a simple heterogeneous financial crime graph."""
    graph = nx.Graph()
    customers = datasets["customers"]
    accounts = datasets["accounts"]
    transactions = datasets["transactions"]
    beneficiaries = datasets["beneficiaries"]
    devices = datasets["devices"]

    for _, row in customers.iterrows():
        graph.add_node(_node_id("customer", row["customer_id"]), node_type="customer")
    for _, row in accounts.iterrows():
        graph.add_node(_node_id("account", row["account_id"]), node_type="account")
        graph.add_edge(
            _node_id("customer", row["customer_id"]),
            _node_id("account", row["account_id"]),
            edge_type="OWNS",
        )
    for _, row in beneficiaries.iterrows():
        graph.add_node(_node_id("beneficiary", row["beneficiary_id"]), node_type="beneficiary")
    for _, row in devices.iterrows():
        graph.add_node(_node_id("device", row["device_id"]), node_type="device")

    for _, row in transactions.iterrows():
        account_node = _node_id("account", row["account_id"])
        transaction_node = _node_id("transaction", row["transaction_id"])
        beneficiary_node = _node_id("beneficiary", row["beneficiary_id"])
        device_node = _node_id("device", row["device_id"])
        graph.add_node(transaction_node, node_type="transaction")
        graph.add_edge(account_node, transaction_node, edge_type="SENDS")
        graph.add_edge(transaction_node, beneficiary_node, edge_type="TO")
        graph.add_edge(transaction_node, device_node, edge_type="USED")
        graph.add_edge(account_node, device_node, edge_type="USES")
        graph.add_edge(account_node, beneficiary_node, edge_type="PAYS")

    return graph


def _component_lookup(graph: nx.Graph) -> dict[str, tuple[int, int]]:
    lookup: dict[str, tuple[int, int]] = {}
    for cluster_number, component in enumerate(nx.connected_components(graph), start=1):
        component_size = len(component)
        for node in component:
            lookup[node] = (cluster_number, component_size)
    return lookup


def generate_graph_features(
    datasets: dict[str, pd.DataFrame],
    shared_device_account_threshold: int = 2,
    shared_beneficiary_account_threshold: int = 2,
    large_component_threshold: int = 25,
    suspicious_cluster_rate_threshold: float = 0.2,
) -> GraphFeatureResult:
    """Generate transaction-level graph/network features."""
    graph = build_financial_crime_graph(datasets)
    transactions = datasets["transactions"]
    accounts = datasets["accounts"][["account_id", "customer_id"]]
    tx = transactions.merge(accounts, on="account_id", how="left")

    account_beneficiary_count = tx.groupby("account_id")["beneficiary_id"].nunique()
    account_device_count = tx.groupby("account_id")["device_id"].nunique()
    device_account_count = tx.groupby("device_id")["account_id"].nunique()
    beneficiary_account_count = tx.groupby("beneficiary_id")["account_id"].nunique()
    suspicious_by_device = tx.groupby("device_id")["is_suspicious"].sum()
    suspicious_by_beneficiary = tx.groupby("beneficiary_id")["is_suspicious"].sum()
    high_value_by_beneficiary = (
        tx.loc[tx["amount"].ge(5000)].groupby("beneficiary_id")["account_id"].nunique()
    )

    centrality = nx.degree_centrality(graph)
    components = _component_lookup(graph)
    cluster_by_account = {
        account_id: components.get(_node_id("account", account_id), (0, 0))[0]
        for account_id in tx["account_id"].unique()
    }
    cluster_size_by_account = {
        account_id: components.get(_node_id("account", account_id), (0, 0))[1]
        for account_id in tx["account_id"].unique()
    }
    cluster_suspicious_rate = (
        tx.assign(network_cluster_id=tx["account_id"].map(cluster_by_account))
        .groupby("network_cluster_id")["is_suspicious"]
        .mean()
    )

    feature_base_columns = [
        "transaction_id",
        "account_id",
        "customer_id",
        "beneficiary_id",
        "device_id",
        "is_suspicious",
    ]
    features = tx[feature_base_columns].copy()
    features["network_cluster_id"] = features["account_id"].map(cluster_by_account)
    features["network_cluster_size"] = features["account_id"].map(cluster_size_by_account)
    features["account_degree"] = features["account_id"].map(
        lambda account_id: graph.degree(_node_id("account", account_id))
    )
    features["account_beneficiary_count"] = features["account_id"].map(account_beneficiary_count)
    features["account_device_count"] = features["account_id"].map(account_device_count)
    features["device_account_count"] = features["device_id"].map(device_account_count)
    features["beneficiary_account_count"] = features["beneficiary_id"].map(
        beneficiary_account_count
    )
    features["shared_device_count"] = features["device_account_count"].sub(1).clip(lower=0)
    features["shared_beneficiary_count"] = (
        features["beneficiary_account_count"].sub(1).clip(lower=0)
    )
    features["account_centrality"] = features["account_id"].map(
        lambda account_id: centrality.get(_node_id("account", account_id), 0.0)
    )
    features["cluster_suspicious_rate"] = features["network_cluster_id"].map(
        cluster_suspicious_rate
    )
    features["device_suspicious_transaction_count"] = features["device_id"].map(
        suspicious_by_device
    )
    features["beneficiary_suspicious_transaction_count"] = features["beneficiary_id"].map(
        suspicious_by_beneficiary
    )
    features["beneficiary_high_value_account_count"] = (
        features["beneficiary_id"].map(high_value_by_beneficiary).fillna(0)
    )
    features = features.fillna(0)

    features["shared_device_flag"] = (
        features["device_account_count"].ge(shared_device_account_threshold)
    ).astype(int)
    features["shared_beneficiary_flag"] = (
        features["beneficiary_account_count"].ge(shared_beneficiary_account_threshold)
    ).astype(int)
    features["suspicious_cluster_flag"] = (
        features["network_cluster_size"].ge(large_component_threshold)
        & features["cluster_suspicious_rate"].ge(suspicious_cluster_rate_threshold)
    ).astype(int)
    features["high_risk_network_flag"] = (
        features["shared_device_flag"].eq(1)
        | features["shared_beneficiary_flag"].eq(1)
        | features["suspicious_cluster_flag"].eq(1)
    ).astype(int)
    features["mule_network_indicator"] = (
        features["shared_device_flag"].eq(1)
        & features["shared_beneficiary_flag"].eq(1)
        & features["is_suspicious"].astype(bool)
    ).astype(int)

    return GraphFeatureResult(graph=graph, features=features)


def edge_type_counts(graph: nx.Graph) -> dict[str, int]:
    """Count graph edges by edge type."""
    counts: dict[str, int] = {}
    for _, _, data in graph.edges(data=True):
        edge_type = str(data.get("edge_type", "UNKNOWN"))
        counts[edge_type] = counts.get(edge_type, 0) + 1
    return counts


def node_type_counts(graph: nx.Graph) -> dict[str, int]:
    """Count graph nodes by node type."""
    counts: dict[str, int] = {}
    for _, data in graph.nodes(data=True):
        node_type = str(data.get("node_type", "unknown"))
        counts[node_type] = counts.get(node_type, 0) + 1
    return counts
