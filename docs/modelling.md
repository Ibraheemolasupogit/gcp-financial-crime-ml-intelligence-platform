# Modelling

Milestone 5 introduces a first supervised fraud classification baseline using the engineered transaction feature table.

## Purpose

The fraud classifier estimates the probability that a synthetic transaction is suspicious. It demonstrates practical ML engineering using a local, transparent, reproducible baseline model.

## Feature Selection Approach

The model uses numeric and boolean engineered features from `data/processed/transaction_features.csv`. Identifier columns, raw timestamp strings, categorical text fields, helper labels, and free-text fields are excluded from model training.

Excluded examples include transaction IDs, account IDs, customer IDs, device IDs, beneficiary IDs, `suspicious_pattern`, raw timestamps, currency, transaction type, country text fields, channel, and merchant category.

## Train/Test Split

The workflow uses a deterministic train/test split from `configs/model_config.yaml`:

- `random_seed`: controls reproducibility
- `test_size`: controls holdout size
- stratification is used when the target has more than one class

## Model

The baseline model is scikit-learn `LogisticRegression` with standard scaling and balanced class weights. This keeps the first supervised model transparent and lightweight.

## Metrics

The workflow writes `outputs/sample/model_metrics.json` with precision, recall, F1 score, ROC AUC when available, confusion matrix, class rate, train/test row counts, feature count, threshold, and notes.

## Limitations

This is not a production deployment. The model is trained only on synthetic data, uses synthetic labels, is not calibrated for live operations, and has no model registry, serving API, monitoring integration, or formal validation package.

Future milestones may add deeper validation, monitoring, anomaly detection, or graph methods. Those are intentionally outside Milestone 5.
