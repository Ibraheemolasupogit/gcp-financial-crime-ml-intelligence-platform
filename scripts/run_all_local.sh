#!/usr/bin/env bash
set -euo pipefail

echo "Running local synthetic financial crime ML demo..."

python3 scripts/generate_demo_data.py
python3 scripts/validate_demo_data.py
python3 scripts/build_features.py
python3 scripts/train_fraud_model.py
python3 scripts/run_anomaly_detection.py
python3 scripts/run_network_risk.py
python3 scripts/run_nlp_triage.py
python3 scripts/run_monitoring.py
python3 scripts/generate_governance_pack.py
python3 scripts/validate_docs.py

echo "Local demo workflow completed."
