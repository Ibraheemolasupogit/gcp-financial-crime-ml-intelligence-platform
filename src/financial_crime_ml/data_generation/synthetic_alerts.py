"""Generate synthetic financial crime alerts."""

from __future__ import annotations

import numpy as np
import pandas as pd

ALERT_TYPE_BY_PATTERN = {
    "high_transaction_velocity": "velocity_rule",
    "round_number_payments": "structuring_indicator",
    "unusual_amount_spike": "amount_spike",
    "new_beneficiary_risk": "new_beneficiary",
    "high_risk_jurisdiction_exposure": "jurisdiction_risk",
    "rapid_movement_of_funds": "rapid_movement",
    "shared_device_behaviour": "shared_device",
    "mule_account_style_behaviour": "mule_activity",
    "account_takeover_style_behaviour": "account_takeover",
}


def generate_alerts(transactions: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Create alerts for suspicious or materially risky transactions."""
    suspicious_transactions = transactions.loc[transactions["is_suspicious"]].copy()
    if suspicious_transactions.empty:
        return pd.DataFrame(
            columns=[
                "alert_id",
                "transaction_id",
                "account_id",
                "alert_type",
                "alert_severity",
                "alert_status",
                "alert_timestamp",
                "alert_reason",
            ]
        )

    suspicious_transactions = suspicious_transactions.reset_index(drop=True)
    alert_timestamps = pd.to_datetime(
        suspicious_transactions["transaction_timestamp"]
    ) + pd.to_timedelta(rng.integers(5, 180, size=len(suspicious_transactions)), unit="m")
    severity = np.where(
        suspicious_transactions["suspicious_pattern"].isin(
            ["high_risk_jurisdiction_exposure", "account_takeover_style_behaviour"]
        ),
        "high",
        rng.choice(["medium", "high"], size=len(suspicious_transactions), p=[0.72, 0.28]),
    )

    return pd.DataFrame(
        {
            "alert_id": [f"ALERT{i:06d}" for i in range(1, len(suspicious_transactions) + 1)],
            "transaction_id": suspicious_transactions["transaction_id"],
            "account_id": suspicious_transactions["account_id"],
            "alert_type": suspicious_transactions["suspicious_pattern"].map(ALERT_TYPE_BY_PATTERN),
            "alert_severity": severity,
            "alert_status": rng.choice(
                ["open", "in_review", "closed_false_positive", "escalated"],
                size=len(suspicious_transactions),
                p=[0.35, 0.34, 0.18, 0.13],
            ),
            "alert_timestamp": [
                timestamp.to_pydatetime().replace(microsecond=0).isoformat()
                for timestamp in alert_timestamps
            ],
            "alert_reason": [
                f"Synthetic alert generated for {pattern.replace('_', ' ')}."
                for pattern in suspicious_transactions["suspicious_pattern"]
            ],
        }
    )
