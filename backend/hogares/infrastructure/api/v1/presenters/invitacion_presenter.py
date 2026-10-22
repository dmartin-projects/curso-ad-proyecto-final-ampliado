# hogares/infrastructure/api/v1/presenters/invitacion_presenter.py — del OutputDTO a lo que lee el serializer (módulo 88)
from types import SimpleNamespace

from hogares.application.obtener_invitacion_use_case.dtos.invitacion_listada_output_dto import (
    InvitacionListadaOutputDTO,
)


def presentar(i: InvitacionListadaOutputDTO) -> SimpleNamespace:
    return SimpleNamespace(pk=i.id, id=i.id, email=i.email, rol=i.rol, caduca=i.caduca, aceptada=i.aceptada)
