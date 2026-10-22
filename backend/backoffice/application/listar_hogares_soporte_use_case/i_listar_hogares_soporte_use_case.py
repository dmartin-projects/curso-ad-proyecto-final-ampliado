# backoffice/application/listar_hogares_soporte_use_case/i_listar_hogares_soporte_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.listar_hogares_soporte_use_case.dtos.listar_hogares_soporte_input_dto import (
    ListarHogaresSoporteInputDTO,
)
from backoffice.application.shared.dtos.hogar_soporte_output_dto import HogarSoporteOutputDTO
from core.application.dtos.pagina_output_dto import PaginaOutputDTO


class IListarHogaresSoporteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarHogaresSoporteInputDTO) -> PaginaOutputDTO[HogarSoporteOutputDTO]: ...
