"""Generate synthetic device records."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd


def _random_dates(rng: np.random.Generator, count: int) -> list[str]:
    start = date(2021, 1, 1)
    offsets = rng.integers(0, (date(2026, 1, 1) - start).days, size=count)
    return [(start + timedelta(days=int(offset))).isoformat() for offset in offsets]


def generate_devices(count: int, rng: np.random.Generator) -> pd.DataFrame:
    """Create synthetic device records."""
    return pd.DataFrame(
        {
            "device_id": [f"DEV{i:06d}" for i in range(1, count + 1)],
            "device_type": rng.choice(
                ["mobile_ios", "mobile_android", "desktop", "tablet", "api_client"],
                size=count,
                p=[0.32, 0.31, 0.25, 0.08, 0.04],
            ),
            "ip_country": rng.choice(
                ["GB", "US", "DE", "FR", "NL", "SG", "AE", "NG", "ZA", "BR", "TR"],
                size=count,
                p=[0.34, 0.18, 0.09, 0.07, 0.07, 0.06, 0.04, 0.05, 0.04, 0.03, 0.03],
            ),
            "first_seen_date": _random_dates(rng, count),
            "device_risk_band": rng.choice(
                ["low", "medium", "high"],
                size=count,
                p=[0.7, 0.22, 0.08],
            ),
        }
    )
