# estadisticas/domain/vo/periodo.py — value object (módulo 89)
#
# La aritmética de fechas de las estadísticas, en Python puro: qué meses entran en "los últimos 12", hasta qué día
# cuenta el mes en curso, cuántos martes tiene un periodo. Se prueba sin base de datos.
from dataclasses import dataclass
from datetime import date, timedelta

from estadisticas.domain.vo.mes import Mes


@dataclass(frozen=True, slots=True)
class Periodo:
    """Los días [desde, antes_de): lo que entra en una consulta (el último día NO entra, como en SQL)."""

    desde: date
    antes_de: date

    @classmethod
    def de_meses(cls, ultimo: Mes, meses: int) -> "Periodo":
        """Los `meses` meses que terminan en `ultimo`, incluido."""
        return cls(ultimo.mas(1 - meses).primer_dia, ultimo.mas(1).primer_dia)

    @classmethod
    def de_meses_hasta_hoy(cls, ultimo: Mes, meses: int, hoy: date) -> "Periodo":
        """Como `de_meses`, pero sin pasar de hoy: un mes futuro cuenta como el actual (si no, el periodo empezaría
        después de terminar), y del mes en curso solo los días que ya han llegado."""
        completo = cls.de_meses(min(ultimo, Mes.de(hoy)), meses)
        return cls(completo.desde, min(completo.antes_de, hoy + timedelta(days=1)))

    @property
    def hasta(self) -> date:
        """El último día que entra."""
        return self.antes_de - timedelta(days=1)

    def meses(self) -> list[Mes]:
        """Todos los meses del periodo, en orden: también los que no tengan movimientos (para el gráfico)."""
        resultado, mes = [], Mes.de(self.desde)
        while mes.primer_dia < self.antes_de:
            resultado.append(mes)
            mes = mes.mas(1)
        return resultado

    def dias_de_la_semana(self) -> dict[int, int]:
        """{1: cuántos lunes tiene el periodo, …, 7: cuántos domingos}."""
        dias = (self.antes_de - self.desde).days
        primero = self.desde.isoweekday()
        return {d: dias // 7 + (1 if (d - primero) % 7 < dias % 7 else 0) for d in range(1, 8)}
