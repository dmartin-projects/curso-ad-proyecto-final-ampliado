# hogares/infrastructure/database/repositories/invitacion_command_repository_orm.py — IInvitacionCommandRepository con el ORM (módulo 88)
from core.infrastructure.database.guardado import guardar_fila
from hogares.domain.bo.invitacion import Invitacion
from hogares.domain.repositories.i_invitacion_command_repository import IInvitacionCommandRepository
from hogares.infrastructure.database.mappers.invitacion_mapper import invitacion_a_bo, invitacion_a_modelo
from hogares.infrastructure.database.models.invitacion_model import Invitacion as InvitacionModel

CAMPOS = ["rol", "invitado_por", "caduca", "aceptada"]


class InvitacionCommandRepositoryORM(IInvitacionCommandRepository):
    def pendiente(self, hogar_id, email):
        fila = InvitacionModel.objects.filter(hogar_id=hogar_id, email=email, aceptada__isnull=True).first()
        return invitacion_a_bo(fila) if fila else None

    def por_token(self, token):
        fila = InvitacionModel.objects.select_for_update().filter(token=token).first()
        return invitacion_a_bo(fila) if fila else None

    def guardar(self, invitacion: Invitacion) -> None:
        fila = invitacion_a_modelo(invitacion)
        guardar_fila(fila, CAMPOS, {})
        invitacion.id = fila.pk
