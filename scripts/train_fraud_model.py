"""Train Milestone 5 fraud classifier and AML scoring outputs."""

from financial_crime_ml.models.workflow import run_fraud_model_workflow


def main() -> None:
    """Run the Milestone 5 workflow and print a concise summary."""
    result = run_fraud_model_workflow()
    metrics = result["metrics"]
    print("Fraud model workflow completed.")
    print(f"Model: {metrics['model_name']}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"F1 score: {metrics['f1_score']:.4f}")
    print(f"ROC AUC: {metrics['roc_auc']:.4f}")
    print(f"Metrics written to: {result['model_metrics_path']}")
    print(f"Fraud predictions written to: {result['fraud_predictions_path']}")
    print(f"AML risk scores written to: {result['aml_risk_scores_path']}")
    print(f"Prioritised alerts written to: {result['prioritised_alerts_path']}")
    print(f"Model card written to: {result['model_card_path']}")


if __name__ == "__main__":
    main()
