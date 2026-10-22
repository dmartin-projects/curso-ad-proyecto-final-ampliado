# estadisticas/domain/services/medias_por_dia.py — el gasto medio de cada día de la semana (módulos 85 y 89)
from decimal import Decimal

from estadisticas.domain.vo.periodo import Periodo

DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")  # isoweekday() - 1


def gasto_medio_por_dia(totales: dict[int, Decimal], periodo: Periodo) -> list[tuple[int, str, Decimal]]:
    """[(1, "lunes", media), …]: el gasto de cada día de la semana ÷ cuántos de ese día tiene el periodo."""
    cuantos = periodo.dias_de_la_semana()
    return [(d, DIAS[d - 1], (Decimal(totales.get(d, 0)) / cuantos[d]).quantize(Decimal("0.01"))) for d in range(1, 8)]
