from datetime import date

from invoices.invoice import Invoice, Line


def test_invoice_total():
    inv = Invoice("F-1", "ACME", date(2026, 3, 2), [Line("Hours", 10, 50.0), Line("Licence", 1, 120.0)])
    assert inv.subtotal() == 620.0
    assert inv.vat() == 130.2
    assert inv.total() == 750.2
