"""Generate synthetic transaction records."""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

NORMAL_PATTERN = "normal_activity"
SUSPICIOUS_PATTERNS = [
    "high_transaction_velocity",
    "round_number_payments",
    "unusual_amount_spike",
    "new_beneficiary_risk",
    "high_risk_jurisdiction_exposure",
    "rapid_movement_of_funds",
    "shared_device_behaviour",
    "mule_account_style_behaviour",
    "account_takeover_style_behaviour",
]
HIGH_RISK_COUNTRIES = ["AE", "NG", "PA", "TR"]


def _random_timestamps(rng: np.random.Generator, count: int) -> list[str]:
    start = datetime(2025, 1, 1)
    minutes = rng.integers(0, 365 * 24 * 60, size=count)
    return [
        (start + timedelta(minutes=int(offset))).isoformat(timespec="seconds")
        for offset in minutes
    ]


def generate_transactions(
    count: int,
    accounts: pd.DataFrame,
    beneficiaries: pd.DataFrame,
    devices: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Create synthetic transactions with labelled suspicious patterns."""
    account_ids = rng.choice(accounts["account_id"].to_numpy(), size=count)
    beneficiary_ids = rng.choice(beneficiaries["beneficiary_id"].to_numpy(), size=count)
    device_ids = rng.choice(devices["device_id"].to_numpy(), size=count)

    pattern_probabilities = [0.82, *([0.02] * len(SUSPICIOUS_PATTERNS))]
    patterns = rng.choice(
        [NORMAL_PATTERN, *SUSPICIOUS_PATTERNS],
        size=count,
        p=pattern_probabilities,
    )
    is_suspicious = patterns != NORMAL_PATTERN

    amounts = rng.lognormal(mean=4.2, sigma=0.9, size=count).round(2)
    amounts = np.where(
        patterns == "round_number_payments",
        rng.choice([1000, 2500, 5000], count),
        amounts,
    )
    amounts = np.where(
        patterns == "unusual_amount_spike",
        amounts * rng.uniform(8, 18, count),
        amounts,
    )
    amounts = np.where(
        patterns == "rapid_movement_of_funds",
        rng.uniform(7000, 25000, count),
        amounts,
    )
    amounts = np.round(amounts, 2)

    beneficiary_country_lookup = beneficiaries.set_index("beneficiary_id")["beneficiary_country"]
    destination_countries = pd.Series(beneficiary_ids).map(beneficiary_country_lookup).to_numpy()
    high_risk_mask = patterns == "high_risk_jurisdiction_exposure"
    destination_countries[high_risk_mask] = rng.choice(
        HIGH_RISK_COUNTRIES,
        size=int(high_risk_mask.sum()),
    )

    device_country_lookup = devices.set_index("device_id")["ip_country"]
    origin_countries = pd.Series(device_ids).map(device_country_lookup).to_numpy()

    shared_device_mask = patterns == "shared_device_behaviour"
    if shared_device_mask.any():
        shared_devices = devices["device_id"].head(max(1, min(10, len(devices)))).to_numpy()
        device_ids[shared_device_mask] = rng.choice(
            shared_devices,
            size=int(shared_device_mask.sum()),
        )

    takeover_mask = patterns == "account_takeover_style_behaviour"
    channels = rng.choice(
        ["mobile", "web", "branch", "api"],
        size=count,
        p=[0.48, 0.34, 0.08, 0.10],
    )
    channels[takeover_mask] = rng.choice(["mobile", "web"], size=int(takeover_mask.sum()))

    return pd.DataFrame(
        {
            "transaction_id": [f"TXN{i:07d}" for i in range(1, count + 1)],
            "account_id": account_ids,
            "beneficiary_id": beneficiary_ids,
            "device_id": device_ids,
            "transaction_timestamp": _random_timestamps(rng, count),
            "amount": amounts,
            "currency": rng.choice(["GBP", "USD", "EUR", "SGD", "AED"], size=count),
            "transaction_type": rng.choice(
                ["card_payment", "bank_transfer", "cash_withdrawal", "international_transfer"],
                size=count,
                p=[0.42, 0.32, 0.11, 0.15],
            ),
            "merchant_category": rng.choice(
                [
                    "grocery",
                    "travel",
                    "electronics",
                    "crypto_exchange",
                    "gambling",
                    "cash_services",
                ],
                size=count,
                p=[0.34, 0.16, 0.18, 0.08, 0.08, 0.16],
            ),
            "origin_country": origin_countries,
            "destination_country": destination_countries,
            "channel": channels,
            "is_suspicious": is_suspicious,
            "suspicious_pattern": patterns,
        }
    )
