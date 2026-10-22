# hogares/application/aceptar_invitacion_use_case/i_aceptar_invitacion_use_case.py (módulos 71 y 88)
from abc import ABC, abstractmethod

from hogares.application.aceptar_invitacion_use_case.dtos.aceptar_invitacion_input_dto import AceptarInvitacionInputDTO
from hogares.application.shared.dtos.membresia_output_dto import MembresiaOutputDTO


class IAceptarInvitacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: AceptarInvitacionInputDTO) -> MembresiaOutputDTO: ...
