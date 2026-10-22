# estadisticas/application/shared/mes_hasta.py — el último mes que se pide (módulo 89)
from datetime import date

from estadisticas.domain.vo.mes import Mes


def mes_hasta(hasta: str | None, hoy: date) -> Mes:
    """El parámetro `hasta` ("2026-10") como Mes del dominio; sin él, el mes de hoy.
    MesMalFormadoException si no tiene la forma AAAA-MM."""
    if hasta is None:
        return Mes.de(hoy)
    return Mes.desde_texto(hasta)
