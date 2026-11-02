"""Invoice model."""
from dataclasses import dataclass, field
from datetime import date

from . import dates
from .amounts import calculate_vat, round_amount


@dataclass
class Line:
    description: str
    quantity: int
    unit_price: float

    @property
    def amount(self) -> float:
        return round_amount(self.quantity * self.unit_price)


@dataclass
class Invoice:
    number: str
    customer: str
    issue_date: date
    lines: list[Line] = field(default_factory=list)
    vat_rate: str = "standard"

    def subtotal(self) -> float:
        return round_amount(sum(l.amount for l in self.lines))

    def vat(self) -> float:
        return calculate_vat(self.subtotal(), self.vat_rate)

    def total(self) -> float:
        return round_amount(self.subtotal() + self.vat())

    def due_date(self) -> date:
        return dates.due_date(self.issue_date)
