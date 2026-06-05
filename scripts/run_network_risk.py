"""Run Milestone 7 graph/network risk outputs."""

from financial_crime_ml.monitoring import run_network_risk_workflow


def main() -> None:
    """Run network risk modelling and print a concise summary."""
    result = run_network_risk_workflow()
    summary = result["summary"]
    print("Network risk workflow completed.")
    print(f"Nodes: {summary['node_count']}")
    print(f"Edges: {summary['edge_count']}")
    print(f"Connected components: {summary['connected_component_count']}")
    print(f"High-risk network rows: {summary['high_risk_network_count']}")
    print(f"Network scores written to: {result['network_risk_scores_path']}")
    print(f"High-risk networks written to: {result['high_risk_networks_path']}")
    print(f"Summary written to: {result['network_summary_path']}")
    print(f"Report written to: {result['network_report_path']}")


if __name__ == "__main__":
    main()
