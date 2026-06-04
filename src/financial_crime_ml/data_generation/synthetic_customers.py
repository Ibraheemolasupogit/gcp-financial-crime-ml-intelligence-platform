"""Generate synthetic customer records."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd


def _random_dates(
    rng: np.random.Generator,
    count: int,
    start: date = date(2020, 1, 1),
    end: date = date(2025, 12, 31),
) -> list[str]:
    days = (end - start).days
    offsets = rng.integers(0, days + 1, size=count)
    return [(start + timedelta(days=int(offset))).isoformat() for offset in offsets]


def generate_customers(count: int, rng: np.random.Generator) -> pd.DataFrame:
    """Create synthetic customer profiles."""
    customer_ids = [f"CUST{i:06d}" for i in range(1, count + 1)]
    customer_types = rng.choice(["individual", "business"], size=count, p=[0.82, 0.18])
    countries = rng.choice(
        ["GB", "US", "DE", "FR", "NL", "SG", "AE", "NG", "ZA", "BR", "MX", "TR"],
        size=count,
        p=[0.28, 0.18, 0.1, 0.08, 0.07, 0.07, 0.04, 0.05, 0.04, 0.04, 0.03, 0.02],
    )
    risk_bands = rng.choice(["low", "medium", "high"], size=count, p=[0.68, 0.24, 0.08])

    age_bands = rng.choice(["18-25", "26-35", "36-50", "51-65", "66+"], size=count)
    business_types = rng.choice(
        ["retail", "import_export", "professional_services", "cash_intensive", "fintech"],
        size=count,
    )
    age_or_business = [
        business_types[index] if customer_type == "business" else age_bands[index]
        for index, customer_type in enumerate(customer_types)
    ]

    return pd.DataFrame(
        {
            "customer_id": customer_ids,
            "customer_type": customer_types,
            "age_band_or_business_type": age_or_business,
            "country": countries,
            "risk_band": risk_bands,
            "onboarding_date": _random_dates(rng, count),
            "kyc_status": rng.choice(
                ["verified", "pending_review", "enhanced_due_diligence"],
                size=count,
                p=[0.82, 0.12, 0.06],
            ),
        }
    )
