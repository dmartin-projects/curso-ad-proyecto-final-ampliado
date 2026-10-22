# notificaciones/application/contar_no_leidas_use_case/i_contar_no_leidas_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from notificaciones.application.contar_no_leidas_use_case.dtos.contar_no_leidas_input_dto import ContarNoLeidasInputDTO


class IContarNoLeidasUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ContarNoLeidasInputDTO) -> int: ...
