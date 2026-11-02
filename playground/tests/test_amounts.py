from invoices.amounts import calculate_vat, round_amount, total_with_vat


def test_round_half_up():
    # 0.125 -> 0.13 (half-up). Python's round() gives 0.12 (banker's rounding + floating point).
    assert round_amount(0.125) == 0.13
    assert round_amount(2.675) == 2.68


def test_standard_vat():
    assert calculate_vat(100) == 21.0


def test_total_with_vat_cent():
    assert total_with_vat(10.05, "reduced") == 11.06
