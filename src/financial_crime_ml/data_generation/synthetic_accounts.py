"""Generate synthetic account records."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd


def _random_dates(rng: np.random.Generator, count: int) -> list[str]:
    start = date(2020, 1, 1)
    offsets = rng.integers(0, (date(2026, 1, 1) - start).days, size=count)
    return [(start + timedelta(days=int(offset))).isoformat() for offset in offsets]


def generate_accounts(
    count: int,
    customers: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Create synthetic accounts linked to generated customers."""
    return pd.DataFrame(
        {
            "account_id": [f"ACCT{i:06d}" for i in range(1, count + 1)],
            "customer_id": rng.choice(customers["customer_id"].to_numpy(), size=count),
            "account_type": rng.choice(
                ["current", "savings", "business_current", "wallet"],
                size=count,
                p=[0.48, 0.25, 0.17, 0.10],
            ),
            "open_date": _random_dates(rng, count),
            "account_status": rng.choice(
                ["active", "dormant", "restricted", "closed"],
                size=count,
                p=[0.86, 0.06, 0.05, 0.03],
            ),
            "base_currency": rng.choice(
                ["GBP", "USD", "EUR", "SGD", "AED"],
                size=count,
                p=[0.45, 0.25, 0.2, 0.06, 0.04],
            ),
            "branch_region": rng.choice(
                ["London", "South East", "Midlands", "North West", "Scotland", "Digital"],
                size=count,
            ),
        }
    )
