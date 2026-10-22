# estadisticas/application/obtener_dias_semana_use_case/obtener_dias_semana_use_case.py — un use case de CONSULTA
# (módulo 89)
#
# PostgreSQL suma lo gastado cada día de la semana; la media (÷ cuántos lunes, martes… tiene el periodo) es del
# dominio, y el periodo, sin pasar de hoy: los días que aún no han llegado bajarían la media.
from estadisticas.application.obtener_dias_semana_use_case.dtos.dia_semana_output_dto import DiaSemanaOutputDTO
from estadisticas.application.obtener_dias_semana_use_case.dtos.dias_semana_output_dto import DiasSemanaOutputDTO
from estadisticas.application.obtener_dias_semana_use_case.dtos.obtener_dias_semana_input_dto import (
    ObtenerDiasSemanaInputDTO,
)
from estadisticas.application.obtener_dias_semana_use_case.i_obtener_dias_semana_use_case import (
    IObtenerDiasSemanaUseCase,
)
from estadisticas.application.ports.i_reloj import IReloj
from estadisticas.application.shared.mes_hasta import mes_hasta
from estadisticas.domain.repositories.i_movimiento_query_service import IMovimientoQueryService
from estadisticas.domain.repositories.i_progreso_query_service import IProgresoQueryService
from estadisticas.domain.repositories.queries.periodo_del_hogar_query import PeriodoDelHogarQuery
from estadisticas.domain.services.medias_por_dia import gasto_medio_por_dia
from estadisticas.domain.vo.periodo import Periodo


class ObtenerDiasSemanaUseCase(IObtenerDiasSemanaUseCase):
    def __init__(self, *, movimientos: IMovimientoQueryService, progreso: IProgresoQueryService, reloj: IReloj):
        self.movimientos = movimientos
        self.progreso = progreso
        self.reloj = reloj

    def ejecutar(self, entrada: ObtenerDiasSemanaInputDTO) -> DiasSemanaOutputDTO:
        hoy = self.reloj.hoy()
        periodo = Periodo.de_meses_hasta_hoy(mes_hasta(entrada.hasta, hoy), entrada.meses, hoy)
        totales = self.movimientos.gasto_por_dia_de_la_semana(PeriodoDelHogarQuery(entrada.hogar_id, periodo))
        dias = [DiaSemanaOutputDTO(dia=d, nombre=n, gasto_medio=m) for d, n, m in gasto_medio_por_dia(totales, periodo)]
        return DiasSemanaOutputDTO(
            hogar_id=entrada.hogar_id,
            ultimo_evento=self.progreso.ultimo_evento(),
            desde=periodo.desde,
            hasta=periodo.hasta,
            dias=dias,
        )
