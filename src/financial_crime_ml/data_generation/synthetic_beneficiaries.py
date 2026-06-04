"""Generate synthetic beneficiary records."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd


def _random_dates(rng: np.random.Generator, count: int) -> list[str]:
    start = date(2021, 1, 1)
    offsets = rng.integers(0, (date(2026, 1, 1) - start).days, size=count)
    return [(start + timedelta(days=int(offset))).isoformat() for offset in offsets]


def generate_beneficiaries(count: int, rng: np.random.Generator) -> pd.DataFrame:
    """Create synthetic beneficiaries."""
    countries = ["GB", "US", "DE", "FR", "NL", "SG", "AE", "NG", "ZA", "BR", "TR", "PA"]
    return pd.DataFrame(
        {
            "beneficiary_id": [f"BEN{i:06d}" for i in range(1, count + 1)],
            "beneficiary_country": rng.choice(
                countries,
                size=count,
                p=[0.24, 0.18, 0.1, 0.08, 0.08, 0.07, 0.06, 0.06, 0.04, 0.04, 0.03, 0.02],
            ),
            "beneficiary_type": rng.choice(
                ["individual", "business", "exchange", "payment_processor"],
                size=count,
                p=[0.58, 0.28, 0.08, 0.06],
            ),
            "first_seen_date": _random_dates(rng, count),
            "risk_band": rng.choice(["low", "medium", "high"], size=count, p=[0.62, 0.27, 0.11]),
        }
    )
