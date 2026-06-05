"""Alert quality and volume monitoring."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd


def _read_optional(path: Path) -> pd.DataFrame | None:
    if not path.exists() or not path.is_file():
        return None
    return pd.read_csv(path)


def _band_count(
    dataset: pd.DataFrame | None,
    column: str,
    high_priority_bands: tuple[str, ...],
) -> int:
    if dataset is None or column not in dataset.columns:
        return 0
    return int(dataset[column].isin(high_priority_bands).sum())


def _count_reasons(dataset: pd.DataFrame | None, columns: list[str]) -> Counter[str]:
    counter: Counter[str] = Counter()
    if dataset is None:
        return counter
    for column in columns:
        if column not in dataset.columns:
            continue
        for value in dataset[column].dropna():
            for reason in str(value).replace(",", ";").split(";"):
                clean_reason = reason.strip()
                if clean_reason:
                    counter[clean_reason] += 1
    return counter


def monitor_alert_quality(
    input_paths: dict[str, Path],
    high_priority_bands: tuple[str, ...],
) -> dict[str, Any]:
    """Create alert volume and quality summary from available alert-like outputs."""
    prioritised = _read_optional(input_paths.get("prioritised_alerts", Path("")))
    anomaly = _read_optional(input_paths.get("anomaly_scores", Path("")))
    high_risk_anomalies = _read_optional(input_paths.get("high_risk_anomalies", Path("")))
    network = _read_optional(input_paths.get("network_risk_scores", Path("")))
    high_risk_networks = _read_optional(input_paths.get("high_risk_networks", Path("")))
    nlp = _read_optional(input_paths.get("nlp_alert_triage", Path("")))
    aml = _read_optional(input_paths.get("aml_risk_scores", Path("")))

    transaction_sources = [
        dataset[["transaction_id"]]
        for dataset in [prioritised, anomaly, high_risk_anomalies, network, high_risk_networks, nlp]
        if dataset is not None and "transaction_id" in dataset.columns
    ]
    duplicate_transaction_alert_count = 0
    if transaction_sources:
        combined_transactions = pd.concat(transaction_sources, ignore_index=True)
        duplicate_transaction_alert_count = int(combined_transactions.duplicated().sum())

    reason_counter: Counter[str] = Counter()
    reason_counter.update(_count_reasons(prioritised, ["priority_reasons"]))
    reason_counter.update(_count_reasons(anomaly, ["top_anomaly_reasons"]))
    reason_counter.update(_count_reasons(network, ["network_risk_reasons"]))
    reason_counter.update(_count_reasons(nlp, ["nlp_triage_reasons"]))

    priority_band_distribution = (
        {
            str(label): int(count)
            for label, count in prioritised["priority_band"].value_counts().items()
        }
        if prioritised is not None and "priority_band" in prioritised.columns
        else {}
    )
    high_priority_alert_count = (
        int(prioritised["priority_band"].isin(high_priority_bands).sum())
        if prioritised is not None and "priority_band" in prioritised.columns
        else 0
    )

    observations = [
        "Review concentration of high and critical alert bands.",
        "Compare duplicate transaction coverage across alert-like outputs.",
        "Use reason-code distribution to identify recurring operational drivers.",
    ]
    if duplicate_transaction_alert_count > 0:
        observations.append("Multiple monitoring outputs reference the same transactions.")

    return {
        "total_prioritised_alerts": int(len(prioritised)) if prioritised is not None else 0,
        "priority_band_distribution": priority_band_distribution,
        "AML_high_critical_count": _band_count(aml, "aml_risk_band", high_priority_bands),
        "anomaly_high_critical_count": _band_count(anomaly, "anomaly_band", high_priority_bands),
        "network_high_critical_count": _band_count(
            network,
            "network_risk_band",
            high_priority_bands,
        ),
        "NLP_high_critical_count": _band_count(nlp, "nlp_triage_band", high_priority_bands),
        "duplicate_transaction_alert_count": duplicate_transaction_alert_count,
        "top_reason_codes": dict(reason_counter.most_common(15)),
        "recommended_monitoring_observations": observations,
        "high_priority_alert_count": high_priority_alert_count,
    }
