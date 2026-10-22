# estadisticas/domain/repositories/queries/periodo_del_hogar_query.py — qué se pide: un hogar y unos días (módulo 89)
from dataclasses import dataclass

from estadisticas.domain.vo.periodo import Periodo


@dataclass(frozen=True, slots=True)
class PeriodoDelHogarQuery:
    hogar_id: int
    periodo: Periodo
