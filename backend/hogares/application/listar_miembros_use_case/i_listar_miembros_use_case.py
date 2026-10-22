# hogares/application/listar_miembros_use_case/i_listar_miembros_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from hogares.application.listar_miembros_use_case.dtos.listar_miembros_input_dto import ListarMiembrosInputDTO
from hogares.application.shared.dtos.miembro_listado_output_dto import MiembroListadoOutputDTO


class IListarMiembrosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarMiembrosInputDTO) -> list[MiembroListadoOutputDTO]: ...
