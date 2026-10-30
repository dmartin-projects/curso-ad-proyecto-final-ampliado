# asistente/application/informe_de_costes_use_case/i_informe_de_costes_use_case.py (módulo 98)
from abc import ABC, abstractmethod

from asistente.application.informe_de_costes_use_case.dtos.informe_de_costes_input_dto import InformeDeCostesInputDTO
from asistente.domain.read_models.coste_por_hogar import CostePorHogar


class IInformeDeCostesUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: InformeDeCostesInputDTO) -> tuple[CostePorHogar, ...]:
        """Lo que ha costado el asistente, por hogar y modelo (para el personal: no lleva Actor de un hogar)."""
