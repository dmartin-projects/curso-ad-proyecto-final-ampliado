# hogares/application/invitar_use_case/i_invitar_use_case.py (módulos 71 y 88)
from abc import ABC, abstractmethod

from hogares.application.invitar_use_case.dtos.invitacion_output_dto import InvitacionOutputDTO
from hogares.application.invitar_use_case.dtos.invitar_input_dto import InvitarInputDTO


class IInvitarUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: InvitarInputDTO) -> InvitacionOutputDTO: ...
