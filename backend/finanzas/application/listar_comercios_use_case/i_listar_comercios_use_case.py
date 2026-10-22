# finanzas/application/listar_comercios_use_case/i_listar_comercios_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from core.application.dtos.pagina_output_dto import PaginaOutputDTO
from finanzas.application.listar_comercios_use_case.dtos.comercio_listado_output_dto import ComercioListadoOutputDTO
from finanzas.application.listar_comercios_use_case.dtos.listar_comercios_input_dto import ListarComerciosInputDTO


class IListarComerciosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarComerciosInputDTO) -> PaginaOutputDTO[ComercioListadoOutputDTO]: ...
