from facturas.importes import calcular_iva, redondear, total_con_iva


def test_redondeo_half_up():
    # 0,125 -> 0,13 (half-up). round() de Python da 0,12 (banker's rounding + coma flotante).
    assert redondear(0.125) == 0.13
    assert redondear(2.675) == 2.68


def test_iva_general():
    assert calcular_iva(100) == 21.0


def test_total_con_iva_centimo():
    assert total_con_iva(10.05, "reducido") == 11.06
