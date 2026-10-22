# hogares/application/cambiar_rol_use_case/i_cambiar_rol_use_case.py (módulos 71 y 88)
from abc import ABC, abstractmethod

from hogares.application.cambiar_rol_use_case.dtos.cambiar_rol_input_dto import CambiarRolInputDTO
from hogares.application.shared.dtos.membresia_output_dto import MembresiaOutputDTO


class ICambiarRolUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: CambiarRolInputDTO) -> MembresiaOutputDTO: ...
