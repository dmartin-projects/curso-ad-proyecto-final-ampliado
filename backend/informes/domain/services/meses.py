# informes/domain/services/meses.py — de qué meses se puede generar un informe (módulos 78 y 88)
from datetime import date

from core.domain.vo.mes import Mes
from informes.domain.exceptions.mes_futuro_exception import MesFuturoException


def comprobar_mes(mes: Mes, hoy: date) -> Mes:
    """No se genera el informe de un mes que aún no ha empezado (el mes en curso sí: "lo que llevamos")."""
    if mes.inicio > hoy:
        raise MesFuturoException()
    return mes
