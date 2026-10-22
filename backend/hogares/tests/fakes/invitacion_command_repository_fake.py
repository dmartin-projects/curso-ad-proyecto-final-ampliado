# hogares/tests/fakes/invitacion_command_repository_fake.py — IInvitacionCommandRepository en memoria (módulo 88)
from core.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia
from hogares.domain.repositories.i_invitacion_command_repository import IInvitacionCommandRepository


class InvitacionCommandRepositoryFake(AlmacenEnMemoria, IInvitacionCommandRepository):
    def pendiente(self, hogar_id, email):
        return next(
            (
                copia(i)
                for i in self._datos.values()
                if (i.hogar_id, i.email) == (hogar_id, email) and i.aceptada is None
            ),
            None,
        )

    def por_token(self, token):
        return next((copia(i) for i in self._datos.values() if i.token == token), None)

    def guardar(self, invitacion):
        self._asignar_id(invitacion)
        self._datos[invitacion.id] = copia(invitacion)
