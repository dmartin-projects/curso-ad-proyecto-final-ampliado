# estadisticas/application/obtener_sin_revisar_use_case/obtener_sin_revisar_use_case.py — un use case de CONSULTA
# (módulo 89; lo que se mide, del módulo 85, ejercicio 4)
from dataclasses import asdict

from estadisticas.application.obtener_sin_revisar_use_case.dtos.mes_sin_revisar_output_dto import (
    MesSinRevisarOutputDTO,
)
from estadisticas.application.obtener_sin_revisar_use_case.dtos.obtener_sin_revisar_input_dto import (
    ObtenerSinRevisarInputDTO,
)
from estadisticas.application.obtener_sin_revisar_use_case.dtos.sin_revisar_output_dto import SinRevisarOutputDTO
from estadisticas.application.obtener_sin_revisar_use_case.i_obtener_sin_revisar_use_case import (
    IObtenerSinRevisarUseCase,
)
from estadisticas.application.ports.i_reloj import IReloj
from estadisticas.application.shared.mes_hasta import mes_hasta
from estadisticas.domain.repositories.i_movimiento_query_service import IMovimientoQueryService
from estadisticas.domain.repositories.i_progreso_query_service import IProgresoQueryService
from estadisticas.domain.repositories.queries.periodo_del_hogar_query import PeriodoDelHogarQuery
from estadisticas.domain.vo.periodo import Periodo


class ObtenerSinRevisarUseCase(IObtenerSinRevisarUseCase):
    def __init__(self, *, movimientos: IMovimientoQueryService, progreso: IProgresoQueryService, reloj: IReloj):
        self.movimientos = movimientos
        self.progreso = progreso
        self.reloj = reloj

    def ejecutar(self, entrada: ObtenerSinRevisarInputDTO) -> SinRevisarOutputDTO:
        periodo = Periodo.de_meses(mes_hasta(entrada.hasta, self.reloj.hoy()), entrada.meses)
        meses = self.movimientos.sin_revisar(PeriodoDelHogarQuery(entrada.hogar_id, periodo))
        return SinRevisarOutputDTO(
            hogar_id=entrada.hogar_id,
            ultimo_evento=self.progreso.ultimo_evento(),
            meses=[MesSinRevisarOutputDTO(**asdict(m)) for m in meses],
        )
