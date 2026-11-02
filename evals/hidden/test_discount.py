"""HIDDEN test: the agent doesn't see it. It is copied into the workdir only to grade the task."""
from datetime import date

import pytest

from invoices.invoice import Invoice, Line


def test_discount_before_vat():
    inv = Invoice("F-2", "ACME", date(2026, 3, 2), [Line("Hours", 10, 50.0)])
    assert inv.total(discount=10) == 544.5  # subtotal 500 -> 450 with 10 % -> +21 % VAT = 544.50


def test_no_discount_same_as_before():
    inv = Invoice("F-3", "ACME", date(2026, 3, 2), [Line("Hours", 10, 50.0)])
    assert inv.total() == 605.0


def test_discount_out_of_range():
    inv = Invoice("F-4", "ACME", date(2026, 3, 2), [Line("Hours", 1, 10.0)])
    with pytest.raises(ValueError):
        inv.total(discount=150)
