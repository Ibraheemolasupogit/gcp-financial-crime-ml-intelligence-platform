"""Generate synthetic case note narratives for alerts."""

from __future__ import annotations

import numpy as np
import pandas as pd

TYPOLOGY_BY_ALERT_TYPE = {
    "velocity_rule": "high_transaction_velocity",
    "structuring_indicator": "round_number_payments",
    "amount_spike": "unusual_amount_spike",
    "new_beneficiary": "new_beneficiary_risk",
    "jurisdiction_risk": "high_risk_jurisdiction_exposure",
    "rapid_movement": "rapid_movement_of_funds",
    "shared_device": "shared_device_behaviour",
    "mule_activity": "mule_account_style_behaviour",
    "account_takeover": "account_takeover_style_behaviour",
}

NARRATIVE_TEMPLATES = {
    "high_transaction_velocity": (
        "Synthetic review notes repeated transfers in a short time window."
    ),
    "round_number_payments": (
        "Synthetic review notes repeated round-number payments requiring review."
    ),
    "unusual_amount_spike": (
        "Synthetic review notes a material increase against expected account activity."
    ),
    "new_beneficiary_risk": "Synthetic review notes payment to a recently observed beneficiary.",
    "high_risk_jurisdiction_exposure": (
        "Synthetic review notes exposure to a higher-risk destination country."
    ),
    "rapid_movement_of_funds": (
        "Synthetic review notes rapid inbound and outbound movement of funds."
    ),
    "shared_device_behaviour": (
        "Synthetic review notes device reuse across multiple account relationships."
    ),
    "mule_account_style_behaviour": (
        "Synthetic review notes behaviour consistent with mule-account typologies."
    ),
    "account_takeover_style_behaviour": (
        "Synthetic review notes unusual access pattern and payment behaviour."
    ),
}


def generate_case_notes(alerts: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Create synthetic analyst-style case notes for generated alerts."""
    if alerts.empty:
        return pd.DataFrame(
            columns=["case_note_id", "alert_id", "note_timestamp", "note_text", "typology_label"]
        )

    typologies = alerts["alert_type"].map(TYPOLOGY_BY_ALERT_TYPE)
    note_timestamps = pd.to_datetime(alerts["alert_timestamp"]) + pd.to_timedelta(
        rng.integers(10, 240, size=len(alerts)),
        unit="m",
    )

    return pd.DataFrame(
        {
            "case_note_id": [f"NOTE{i:06d}" for i in range(1, len(alerts) + 1)],
            "alert_id": alerts["alert_id"],
            "note_timestamp": [
                timestamp.to_pydatetime().replace(microsecond=0).isoformat()
                for timestamp in note_timestamps
            ],
            "note_text": [NARRATIVE_TEMPLATES[typology] for typology in typologies],
            "typology_label": typologies,
        }
    )
