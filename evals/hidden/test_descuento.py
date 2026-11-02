"""Test OCULTO: el agente no lo ve. Se copia al workdir solo para corregir la tarea."""
from datetime import date

import pytest

from facturas.factura import Factura, Linea


def test_descuento_antes_de_iva():
    f = Factura("F-2", "ACME", date(2026, 3, 2), [Linea("Horas", 10, 50.0)])
    assert f.total(descuento=10) == 544.5  # base 500 -> 450 con 10 % -> +21 % IVA = 544,50


def test_sin_descuento_igual_que_antes():
    f = Factura("F-3", "ACME", date(2026, 3, 2), [Linea("Horas", 10, 50.0)])
    assert f.total() == 605.0


def test_descuento_fuera_de_rango():
    f = Factura("F-4", "ACME", date(2026, 3, 2), [Linea("Horas", 1, 10.0)])
    with pytest.raises(ValueError):
        f.total(descuento=150)
