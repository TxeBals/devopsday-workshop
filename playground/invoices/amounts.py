"""Amount calculations. All amounts are expressed in euros with 2 decimals."""
from decimal import Decimal

VAT_RATES = {"standard": 21, "reduced": 10, "super_reduced": 4}


def round_amount(value: float) -> float:
    """Rounds to cents (half-up, as invoicing regulations require)."""
    return round(value, 2)


def calculate_vat(base: float, rate: str = "standard") -> float:
    """VAT amount for a taxable base."""
    if rate not in VAT_RATES:
        raise ValueError(f"unknown VAT rate: {rate}")
    return round_amount(base * VAT_RATES[rate] / 100)


def total_with_vat(base: float, rate: str = "standard") -> float:
    return round_amount(base + calculate_vat(base, rate))


def to_decimal(value: float) -> Decimal:
    return Decimal(str(value))
