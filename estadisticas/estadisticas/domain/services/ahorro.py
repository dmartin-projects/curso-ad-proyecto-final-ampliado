# estadisticas/domain/services/ahorro.py — la tasa de ahorro (módulo 89, ejercicio 2): qué parte de lo que entra se
# queda
from decimal import Decimal


def tasa_de_ahorro(ingresos: Decimal, ahorro: Decimal) -> Decimal | None:
    """% de los ingresos que se ahorra (negativo si se gasta más de lo que entra), con un decimal.
    None si no hubo ingresos: "cuánto ahorras de nada" no tiene respuesta (y no es 0 % ni -∞ %)."""
    if ingresos <= 0:
        return None
    return (ahorro * 100 / ingresos).quantize(Decimal("0.1"))
