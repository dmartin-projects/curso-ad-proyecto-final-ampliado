# informes/application/listar_informes_use_case/i_listar_informes_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from informes.application.listar_informes_use_case.dtos.listar_informes_input_dto import ListarInformesInputDTO
from informes.application.shared.dtos.informe_listado_output_dto import InformeListadoOutputDTO


class IListarInformesUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarInformesInputDTO) -> list[InformeListadoOutputDTO]: ...
