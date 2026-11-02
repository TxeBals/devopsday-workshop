"""Fechas de vencimiento."""
from datetime import date, timedelta


def vencimiento(emision: date, dias: int = 30) -> date:
    """Fecha de vencimiento: emisión + `dias` naturales. Si cae en sábado o domingo,
    se traslada al lunes siguiente."""
    fecha = emision + timedelta(days=dias)
    if fecha.weekday() == 5:
        fecha += timedelta(days=2)
    return fecha
