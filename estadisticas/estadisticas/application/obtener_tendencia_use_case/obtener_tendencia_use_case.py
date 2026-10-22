# estadisticas/application/obtener_tendencia_use_case/obtener_tendencia_use_case.py — un use case de CONSULTA
# (módulo 89)
#
# Lado de lectura de CQRS: usa query services (nunca un command repository) y no abre transacción. Su trabajo es
# decidir el periodo (el dominio sabe de meses) y traducir los read models a su OutputDTO.
from dataclasses import asdict

from estadisticas.application.obtener_tendencia_use_case.dtos.mes_de_tendencia_output_dto import (
    MesDeTendenciaOutputDTO,
)
from estadisticas.application.obtener_tendencia_use_case.dtos.obtener_tendencia_input_dto import (
    ObtenerTendenciaInputDTO,
)
from estadisticas.application.obtener_tendencia_use_case.dtos.tendencia_output_dto import TendenciaOutputDTO
from estadisticas.application.obtener_tendencia_use_case.i_obtener_tendencia_use_case import IObtenerTendenciaUseCase
from estadisticas.application.ports.i_reloj import IReloj
from estadisticas.application.shared.mes_hasta import mes_hasta
from estadisticas.domain.repositories.i_movimiento_query_service import IMovimientoQueryService
from estadisticas.domain.repositories.i_progreso_query_service import IProgresoQueryService
from estadisticas.domain.repositories.queries.periodo_del_hogar_query import PeriodoDelHogarQuery
from estadisticas.domain.vo.periodo import Periodo


class ObtenerTendenciaUseCase(IObtenerTendenciaUseCase):
    def __init__(self, *, movimientos: IMovimientoQueryService, progreso: IProgresoQueryService, reloj: IReloj):
        self.movimientos = movimientos
        self.progreso = progreso
        self.reloj = reloj

    def ejecutar(self, entrada: ObtenerTendenciaInputDTO) -> TendenciaOutputDTO:
        periodo = Periodo.de_meses(mes_hasta(entrada.hasta, self.reloj.hoy()), entrada.meses)
        meses = self.movimientos.tendencia(PeriodoDelHogarQuery(entrada.hogar_id, periodo))
        return TendenciaOutputDTO(
            hogar_id=entrada.hogar_id,
            ultimo_evento=self.progreso.ultimo_evento(),
            meses=[MesDeTendenciaOutputDTO(**asdict(m)) for m in meses],
        )
