from datetime import date

from facturas.fechas import vencimiento


def test_vencimiento_laborable():
    assert vencimiento(date(2026, 3, 2), 30) == date(2026, 4, 1)  # miércoles


def test_vencimiento_sabado_pasa_a_lunes():
    assert vencimiento(date(2026, 3, 5), 30) == date(2026, 4, 6)  # 4 abr sábado -> lunes 6


def test_vencimiento_domingo_pasa_a_lunes():
    assert vencimiento(date(2026, 3, 6), 30) == date(2026, 4, 6)  # 5 abr domingo -> lunes 6
