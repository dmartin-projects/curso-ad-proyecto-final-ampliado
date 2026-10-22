# notificaciones/tests/fakes/notificacion_command_repository_fake.py — INotificacionCommandRepository en memoria (módulo 88)
from core.tests.fakes.almacen_en_memoria import AlmacenEnMemoria, copia
from notificaciones.domain.repositories.i_notificacion_command_repository import INotificacionCommandRepository


class NotificacionCommandRepositoryFake(AlmacenEnMemoria, INotificacionCommandRepository):
    def crear_varias(self, notificaciones):
        for n in notificaciones:
            self._asignar_id(n)
            self._datos[n.id] = copia(n)
