"""Generate a simple model card for the baseline fraud classifier."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Any


def generate_model_card(
    metrics: dict[str, Any],
    feature_columns: list[str],
    output_path: Path,
) -> Path:
    """Write a professional model card markdown file."""
    content = dedent(
        f"""\
        # Baseline Fraud Classifier Model Card

        ## Model Purpose

        This model is a local-first baseline supervised fraud classifier for synthetic
        transaction-level financial crime data. It estimates fraud probability for synthetic
        transactions using engineered numeric and boolean features.

        ## Intended Use

        The model is intended for portfolio demonstration of financial crime ML engineering,
        feature selection, supervised classification, metric reporting, and governance
        documentation.

        ## Not Intended Use

        This model must not be used for live customer decisions, operational financial crime
        controls, regulatory reporting, production alerting, or any real customer investigation.

        ## Dataset Used

        - `data/processed/transaction_features.csv`
        - Synthetic data only
        - No real customer, account, transaction, alert, or case data

        ## Target Variable

        - `{metrics["target_column"]}`

        ## Feature Groups

        The model uses numeric and boolean engineered features from transaction, velocity,
        account/customer, beneficiary, device, and AML typology indicator groups. Identifier,
        timestamp, text, and helper columns are excluded.

        Feature count: {metrics["feature_count"]}

        ## Metrics

        - Precision: {metrics["precision"]:.4f}
        - Recall: {metrics["recall"]:.4f}
        - F1 score: {metrics["f1_score"]:.4f}
        - ROC AUC: {metrics["roc_auc"] if metrics["roc_auc"] is not None else "not available"}
        - Positive class rate: {metrics["positive_class_rate"]:.4f}
        - Threshold used: {metrics["threshold_used"]}
        - Confusion matrix: {metrics["confusion_matrix"]}

        ## Assumptions

        - Synthetic suspicious labels are treated as the supervised target.
        - A deterministic train/test split is used.
        - Logistic regression is used for transparency and simplicity.
        - Feature values are generated from local synthetic data.

        ## Limitations

        - Synthetic data does not represent real customer behaviour.
        - Metrics are demonstration metrics and should not be interpreted as production performance.
        - The model is not calibrated for real financial crime operations.
        - No live serving, model registry, drift monitoring, or production control integration is
          implemented.

        ## Human Review Requirement

        Any fraud or AML output from this project is illustrative. A real financial institution
        would require trained investigator review, escalation procedures, governance approval,
        and formal model validation before operational use.

        ## Synthetic Data Caveat

        All data and labels are generated synthetically for safe public demonstration. The model
        card does not evidence performance on real financial crime data.

        ## Governance Notes

        This artefact supports early model risk documentation by recording purpose, scope, data,
        features, metrics, assumptions, and limitations. Later milestones may expand monitoring,
        validation evidence, and governance controls.

        ## Model Risk Considerations

        Potential risks include overfitting to synthetic typology patterns, false confidence from
        synthetic metrics, limited representativeness, and misuse outside the intended portfolio
        context.

        ## Feature Columns

        {", ".join(feature_columns)}
        """
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path
