# asistente/domain/services/prevision.py — cuánto se gastará este mes al ritmo de ahora (módulo 95)
"""Una previsión honesta tiene dos números, porque cada uno se equivoca de una forma:

- el ritmo lineal (lo gastado / los días que van × los días del mes): se pasa si los gastos fijos van al principio
  (el alquiler el día 1 "se repite" cada día) y se queda corto si van al final;
- a estas alturas del mes pasado: cuánto llevabais el mismo día, y cuánto acabasteis gastando.

El modelo recibe los dos y los explica; ninguno es una promesa.
"""

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from asistente.domain.read_models.gasto_del_dia import GastoDelDia

CENTIMO = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class Prevision:
    gastado: Decimal  # del día 1 a hoy
    dias_transcurridos: int
    dias_del_mes: int
    al_ritmo_actual: Decimal  # el total del mes si se sigue igual
    mes_anterior_a_estas_alturas: Decimal | None  # lo que llevabais el mismo día del mes anterior
    mes_anterior_total: Decimal | None


def acumulado_hasta(dias: tuple[GastoDelDia, ...], dia: int) -> Decimal:
    """El acumulado del último día con gastos que no pasa de `dia` (los días sin gastos no aparecen)."""
    hasta = [d.acumulado for d in dias if d.fecha.day <= dia]
    return hasta[-1] if hasta else Decimal("0")


def prever(hoy: date, este_mes: tuple[GastoDelDia, ...], mes_anterior: tuple[GastoDelDia, ...] | None) -> Prevision:
    dias_del_mes = calendar.monthrange(hoy.year, hoy.month)[1]
    gastado = acumulado_hasta(este_mes, hoy.day)
    ritmo = (gastado / hoy.day * dias_del_mes).quantize(CENTIMO, rounding=ROUND_HALF_UP)
    if not mes_anterior:
        return Prevision(gastado, hoy.day, dias_del_mes, ritmo, None, None)
    # El "mismo día" de un mes más corto: el 31 de octubre frente a septiembre es el 30
    dia_anterior = min(hoy.day, calendar.monthrange(mes_anterior[0].fecha.year, mes_anterior[0].fecha.month)[1])
    return Prevision(
        gastado=gastado,
        dias_transcurridos=hoy.day,
        dias_del_mes=dias_del_mes,
        al_ritmo_actual=ritmo,
        mes_anterior_a_estas_alturas=acumulado_hasta(mes_anterior, dia_anterior),
        mes_anterior_total=mes_anterior[-1].acumulado,
    )
