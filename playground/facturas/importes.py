"""Cálculo de importes. Todos los importes se expresan en euros con 2 decimales."""
from decimal import Decimal

TIPOS_IVA = {"general": 21, "reducido": 10, "superreducido": 4}


def redondear(valor: float) -> float:
    """Redondea a céntimos (half-up, como exige la normativa de facturación)."""
    return round(valor, 2)


def calcular_iva(base: float, tipo: str = "general") -> float:
    """Cuota de IVA de una base imponible."""
    if tipo not in TIPOS_IVA:
        raise ValueError(f"tipo de IVA desconocido: {tipo}")
    return redondear(base * TIPOS_IVA[tipo] / 100)


def total_con_iva(base: float, tipo: str = "general") -> float:
    return redondear(base + calcular_iva(base, tipo))


def a_decimal(valor: float) -> Decimal:
    return Decimal(str(valor))
