"""Modelo de factura."""
from dataclasses import dataclass, field
from datetime import date

from .fechas import vencimiento
from .importes import calcular_iva, redondear


@dataclass
class Linea:
    concepto: str
    cantidad: int
    precio_unitario: float

    @property
    def importe(self) -> float:
        return redondear(self.cantidad * self.precio_unitario)


@dataclass
class Factura:
    numero: str
    cliente: str
    emision: date
    lineas: list[Linea] = field(default_factory=list)
    tipo_iva: str = "general"

    def base(self) -> float:
        return redondear(sum(l.importe for l in self.lineas))

    def iva(self) -> float:
        return calcular_iva(self.base(), self.tipo_iva)

    def total(self) -> float:
        return redondear(self.base() + self.iva())

    def vence(self) -> date:
        return vencimiento(self.emision)
