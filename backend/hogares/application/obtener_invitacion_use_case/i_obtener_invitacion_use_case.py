# hogares/application/obtener_invitacion_use_case/i_obtener_invitacion_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from hogares.application.obtener_invitacion_use_case.dtos.invitacion_listada_output_dto import (
    InvitacionListadaOutputDTO,
)
from hogares.application.obtener_invitacion_use_case.dtos.obtener_invitacion_input_dto import ObtenerInvitacionInputDTO


class IObtenerInvitacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerInvitacionInputDTO) -> InvitacionListadaOutputDTO | None: ...
