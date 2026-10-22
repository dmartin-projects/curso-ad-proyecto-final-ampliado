# hogares/infrastructure/database/repositories/invitacion_query_service_orm.py — IInvitacionQueryService con el ORM (módulo 88)
from hogares.domain.read_models.invitacion_listada import InvitacionListada
from hogares.domain.repositories.i_invitacion_query_service import IInvitacionQueryService
from hogares.infrastructure.database.models.invitacion_model import Invitacion as InvitacionModel


class InvitacionQueryServiceORM(IInvitacionQueryService):
    def detalle(self, hogar_id, invitacion_id):
        campos = ("pk", "email", "rol", "caduca", "aceptada")
        fila = InvitacionModel.objects.filter(hogar_id=hogar_id, pk=invitacion_id).values_list(*campos).first()
        return None if fila is None else InvitacionListada(*fila)
