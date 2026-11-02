from datetime import date

from facturas.factura import Factura, Linea


def test_total_factura():
    f = Factura("F-1", "ACME", date(2026, 3, 2), [Linea("Horas", 10, 50.0), Linea("Licencia", 1, 120.0)])
    assert f.base() == 620.0
    assert f.iva() == 130.2
    assert f.total() == 750.2
