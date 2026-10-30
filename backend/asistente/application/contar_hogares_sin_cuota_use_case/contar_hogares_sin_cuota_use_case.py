# asistente/application/contar_hogares_sin_cuota_use_case/contar_hogares_sin_cuota_use_case.py (98, ejercicio 2)
from datetime import datetime

from asistente.application.contar_hogares_sin_cuota_use_case.dtos.contar_hogares_sin_cuota_input_dto import (
    ContarHogaresSinCuotaInputDTO,
)
from asistente.application.contar_hogares_sin_cuota_use_case.i_contar_hogares_sin_cuota_use_case import (
    IContarHogaresSinCuotaUseCase,
)
from asistente.application.ports.i_tarifas import ITarifas
from asistente.domain.enums.plan import Plan
from asistente.domain.repositories.i_consumo_query_service import IConsumoQueryService
from asistente.domain.repositories.i_plan_del_hogar_repository import IPlanDelHogarRepository
from core.application.ports.i_reloj import IReloj


class ContarHogaresSinCuotaUseCase(IContarHogaresSinCuotaUseCase):
    """Un número para Prometheus que resume miles de hogares: el detalle (cuáles) está en la base de datos. Es la
    forma de llevar a las métricas algo que es POR HOGAR sin poner el hogar en una etiqueta.

    El mes es el de UTC (uno para todos): para un aviso basta; la cuota de cada hogar usa el suyo."""

    def __init__(
        self, *, consumos: IConsumoQueryService, planes: IPlanDelHogarRepository, tarifas: ITarifas, reloj: IReloj
    ):
        self.consumos, self.planes, self.tarifas, self.reloj = consumos, planes, tarifas, reloj

    def ejecutar(self, entrada: ContarHogaresSinCuotaInputDTO) -> int:
        ahora = self.reloj.ahora()
        inicio = datetime(ahora.year, ahora.month, 1, tzinfo=ahora.tzinfo)
        minimo = min(self.tarifas.cuota(p).coste_mes_hogar for p in Plan)
        # solo se mira el plan de los que han gastado al menos la cuota más pequeña: los demás no pueden haberla agotado
        return sum(
            1
            for hogar_id, coste in self.consumos.coste_por_hogar(inicio).items()
            if coste >= minimo and coste >= self.tarifas.cuota(self.planes.plan_de(hogar_id)).coste_mes_hogar
        )
