# hogares/infrastructure/database/mappers/invitacion_mapper.py — BO ↔ fila (módulo 88)
from hogares.domain.bo.invitacion import Invitacion
from hogares.infrastructure.database.models.invitacion_model import Invitacion as InvitacionModel


def invitacion_a_bo(fila: InvitacionModel) -> Invitacion:
    return Invitacion(
        id=fila.pk,
        hogar_id=fila.hogar_id,
        email=fila.email,
        rol=fila.rol,
        token=fila.token,
        invitado_por_id=fila.invitado_por_id,
        caduca=fila.caduca,
        aceptada=fila.aceptada,
    )


def invitacion_a_modelo(i: Invitacion) -> InvitacionModel:
    return InvitacionModel(
        pk=i.id,
        hogar_id=i.hogar_id,
        email=i.email,
        rol=i.rol,
        token=i.token,
        invitado_por_id=i.invitado_por_id,
        caduca=i.caduca,
        aceptada=i.aceptada,
    )
