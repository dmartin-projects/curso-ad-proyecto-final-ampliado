# asistente/application/listar_recuerdos_use_case/i_listar_recuerdos_use_case.py (módulo 99)
from abc import ABC, abstractmethod

from asistente.application.listar_recuerdos_use_case.dtos.listar_recuerdos_input_dto import ListarRecuerdosInputDTO
from asistente.application.shared.dtos.recuerdo_output_dto import RecuerdoOutputDTO


class IListarRecuerdosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarRecuerdosInputDTO) -> list[RecuerdoOutputDTO]:
        """Lo que el asistente recuerda de quien pide, en este hogar."""
