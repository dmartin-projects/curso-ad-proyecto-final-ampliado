# hogares/application/listar_hogares_use_case/i_listar_hogares_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from core.application.dtos.pagina_output_dto import PaginaOutputDTO
from hogares.application.listar_hogares_use_case.dtos.listar_hogares_input_dto import ListarHogaresInputDTO
from hogares.application.shared.dtos.hogar_listado_output_dto import HogarListadoOutputDTO


class IListarHogaresUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarHogaresInputDTO) -> PaginaOutputDTO[HogarListadoOutputDTO]: ...
