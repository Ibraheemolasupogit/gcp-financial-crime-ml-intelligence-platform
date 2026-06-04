"""Explicit schemas for synthetic financial crime datasets."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ColumnSchema:
    """Column-level validation rules."""

    dtype: str
    required: bool = True
    allowed_values: set[object] | None = None
    min_value: float | None = None


@dataclass(frozen=True)
class DatasetSchema:
    """Dataset-level validation rules."""

    columns: dict[str, ColumnSchema]
    primary_key: str
    unique_columns: list[str] = field(default_factory=list)


RISK_BANDS = {"low", "medium", "high"}
COUNTRIES = {"GB", "US", "DE", "FR", "NL", "SG", "AE", "NG", "ZA", "BR", "MX", "TR", "PA"}
CURRENCIES = {"GBP", "USD", "EUR", "SGD", "AED"}

SCHEMAS = {
    "customers": DatasetSchema(
        primary_key="customer_id",
        unique_columns=["customer_id"],
        columns={
            "customer_id": ColumnSchema("string"),
            "customer_type": ColumnSchema("string", allowed_values={"individual", "business"}),
            "age_band_or_business_type": ColumnSchema("string"),
            "country": ColumnSchema("string", allowed_values=COUNTRIES),
            "risk_band": ColumnSchema("string", allowed_values=RISK_BANDS),
            "onboarding_date": ColumnSchema("datetime"),
            "kyc_status": ColumnSchema(
                "string",
                allowed_values={"verified", "pending_review", "enhanced_due_diligence"},
            ),
        },
    ),
    "accounts": DatasetSchema(
        primary_key="account_id",
        unique_columns=["account_id"],
        columns={
            "account_id": ColumnSchema("string"),
            "customer_id": ColumnSchema("string"),
            "account_type": ColumnSchema(
                "string",
                allowed_values={"current", "savings", "business_current", "wallet"},
            ),
            "open_date": ColumnSchema("datetime"),
            "account_status": ColumnSchema(
                "string",
                allowed_values={"active", "dormant", "restricted", "closed"},
            ),
            "base_currency": ColumnSchema("string", allowed_values=CURRENCIES),
            "branch_region": ColumnSchema(
                "string",
                allowed_values={
                    "London",
                    "South East",
                    "Midlands",
                    "North West",
                    "Scotland",
                    "Digital",
                },
            ),
        },
    ),
    "transactions": DatasetSchema(
        primary_key="transaction_id",
        unique_columns=["transaction_id"],
        columns={
            "transaction_id": ColumnSchema("string"),
            "account_id": ColumnSchema("string"),
            "beneficiary_id": ColumnSchema("string"),
            "device_id": ColumnSchema("string"),
            "transaction_timestamp": ColumnSchema("datetime"),
            "amount": ColumnSchema("numeric", min_value=0),
            "currency": ColumnSchema("string", allowed_values=CURRENCIES),
            "transaction_type": ColumnSchema(
                "string",
                allowed_values={
                    "card_payment",
                    "bank_transfer",
                    "cash_withdrawal",
                    "international_transfer",
                },
            ),
            "merchant_category": ColumnSchema(
                "string",
                allowed_values={
                    "grocery",
                    "travel",
                    "electronics",
                    "crypto_exchange",
                    "gambling",
                    "cash_services",
                },
            ),
            "origin_country": ColumnSchema("string", allowed_values=COUNTRIES),
            "destination_country": ColumnSchema("string", allowed_values=COUNTRIES),
            "channel": ColumnSchema("string", allowed_values={"mobile", "web", "branch", "api"}),
            "is_suspicious": ColumnSchema("boolean"),
            "suspicious_pattern": ColumnSchema(
                "string",
                allowed_values={
                    "normal_activity",
                    "high_transaction_velocity",
                    "round_number_payments",
                    "unusual_amount_spike",
                    "new_beneficiary_risk",
                    "high_risk_jurisdiction_exposure",
                    "rapid_movement_of_funds",
                    "shared_device_behaviour",
                    "mule_account_style_behaviour",
                    "account_takeover_style_behaviour",
                },
            ),
        },
    ),
    "beneficiaries": DatasetSchema(
        primary_key="beneficiary_id",
        unique_columns=["beneficiary_id"],
        columns={
            "beneficiary_id": ColumnSchema("string"),
            "beneficiary_country": ColumnSchema("string", allowed_values=COUNTRIES),
            "beneficiary_type": ColumnSchema(
                "string",
                allowed_values={"individual", "business", "exchange", "payment_processor"},
            ),
            "first_seen_date": ColumnSchema("datetime"),
            "risk_band": ColumnSchema("string", allowed_values=RISK_BANDS),
        },
    ),
    "devices": DatasetSchema(
        primary_key="device_id",
        unique_columns=["device_id"],
        columns={
            "device_id": ColumnSchema("string"),
            "device_type": ColumnSchema(
                "string",
                allowed_values={"mobile_ios", "mobile_android", "desktop", "tablet", "api_client"},
            ),
            "ip_country": ColumnSchema("string", allowed_values=COUNTRIES),
            "first_seen_date": ColumnSchema("datetime"),
            "device_risk_band": ColumnSchema("string", allowed_values=RISK_BANDS),
        },
    ),
    "alerts": DatasetSchema(
        primary_key="alert_id",
        unique_columns=["alert_id"],
        columns={
            "alert_id": ColumnSchema("string"),
            "transaction_id": ColumnSchema("string"),
            "account_id": ColumnSchema("string"),
            "alert_type": ColumnSchema(
                "string",
                allowed_values={
                    "velocity_rule",
                    "structuring_indicator",
                    "amount_spike",
                    "new_beneficiary",
                    "jurisdiction_risk",
                    "rapid_movement",
                    "shared_device",
                    "mule_activity",
                    "account_takeover",
                },
            ),
            "alert_severity": ColumnSchema("string", allowed_values={"medium", "high"}),
            "alert_status": ColumnSchema(
                "string",
                allowed_values={"open", "in_review", "closed_false_positive", "escalated"},
            ),
            "alert_timestamp": ColumnSchema("datetime"),
            "alert_reason": ColumnSchema("string"),
        },
    ),
    "case_notes": DatasetSchema(
        primary_key="case_note_id",
        unique_columns=["case_note_id"],
        columns={
            "case_note_id": ColumnSchema("string"),
            "alert_id": ColumnSchema("string"),
            "note_timestamp": ColumnSchema("datetime"),
            "note_text": ColumnSchema("string"),
            "typology_label": ColumnSchema(
                "string",
                allowed_values={
                    "high_transaction_velocity",
                    "round_number_payments",
                    "unusual_amount_spike",
                    "new_beneficiary_risk",
                    "high_risk_jurisdiction_exposure",
                    "rapid_movement_of_funds",
                    "shared_device_behaviour",
                    "mule_account_style_behaviour",
                    "account_takeover_style_behaviour",
                },
            ),
        },
    ),
}
