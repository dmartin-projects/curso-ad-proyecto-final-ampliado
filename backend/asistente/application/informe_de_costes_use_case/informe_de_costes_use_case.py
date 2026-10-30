# asistente/application/informe_de_costes_use_case/informe_de_costes_use_case.py (módulo 98)
from datetime import UTC, datetime, time

from asistente.application.informe_de_costes_use_case.dtos.informe_de_costes_input_dto import InformeDeCostesInputDTO
from asistente.application.informe_de_costes_use_case.i_informe_de_costes_use_case import IInformeDeCostesUseCase
from asistente.domain.read_models.coste_por_hogar import CostePorHogar
from asistente.domain.repositories.i_consumo_query_service import IConsumoQueryService


class InformeDeCostesUseCase(IInformeDeCostesUseCase):
    """Por hogar, en la base de datos; en Prometheus, solo por modelo. Un hogar como etiqueta de una métrica sería una
    serie temporal por hogar (miles, y creciendo): la "cardinalidad" que tumba un Prometheus. Lo que se cuenta por
    algo con muchos valores va a la base de datos (o a las trazas), no a las métricas."""

    def __init__(self, *, consumos: IConsumoQueryService):
        self.consumos = consumos

    def ejecutar(self, entrada: InformeDeCostesInputDTO) -> tuple[CostePorHogar, ...]:
        if entrada.hasta <= entrada.desde:
            raise ValueError("`hasta` tiene que ser posterior a `desde`.")
        desde = datetime.combine(entrada.desde, time(), UTC)  # el mes de facturación del proveedor: en UTC
        hasta = datetime.combine(entrada.hasta, time(), UTC)
        return self.consumos.por_hogar(desde, hasta, por_canal=entrada.por_canal)
