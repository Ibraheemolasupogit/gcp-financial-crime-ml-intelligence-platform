"""Customer risk feature helpers."""

RISK_BAND_ENCODING = {"low": 1, "medium": 2, "high": 3}


def encode_risk_band(risk_band: str) -> int:
    """Encode a low/medium/high synthetic risk band."""
    return RISK_BAND_ENCODING.get(risk_band, 0)
