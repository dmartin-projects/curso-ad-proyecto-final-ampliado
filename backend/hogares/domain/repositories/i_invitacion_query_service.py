# hogares/domain/repositories/i_invitacion_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from hogares.domain.read_models.invitacion_listada import InvitacionListada


class IInvitacionQueryService(ABC):
    @abstractmethod
    def detalle(self, hogar_id: int, invitacion_id: int) -> InvitacionListada | None: ...
