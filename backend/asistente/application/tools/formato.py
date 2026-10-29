# asistente/application/tools/formato.py — cómo escriben las tools los números que lee el modelo (módulo 94)
from decimal import Decimal


def euros(valor: Decimal | int | None) -> str | None:
    """Importes como texto con dos decimales ("812.40"): ni floats (0.1 + 0.2) ni Decimals con 6 decimales."""
    return None if valor is None else f"{Decimal(valor):.2f}"


def pct(valor: Decimal | None) -> float | None:
    """Porcentajes con un decimal (63.6): un número, que el modelo compara y redondea mejor que un texto."""
    return None if valor is None else round(float(valor), 1)
