# eventos/tests/fakes/evento_pendiente_command_repository_fake.py — la bandeja del relay en memoria (módulos 85 y 88)
from datetime import UTC, datetime

from eventos.domain.bo.evento_pendiente import EventoPendiente
from eventos.domain.repositories.i_evento_pendiente_command_repository import IEventoPendienteCommandRepository


class EventoPendienteCommandRepositoryFake(IEventoPendienteCommandRepository):
    def __init__(self, *mensajes, creado: datetime = datetime(2026, 10, 15, tzinfo=UTC)):
        self.filas = {i: {"mensaje": m, "publicado": None} for i, m in enumerate(mensajes, start=1)}
        self.creado = creado

    def pendientes(self, tamano):
        sin = [(i, f) for i, f in sorted(self.filas.items()) if f["publicado"] is None][:tamano]
        return [EventoPendiente(i, f["mensaje"], "", self.creado) for i, f in sin]

    def marcar_publicados(self, ids, cuando):
        for i in ids:
            self.filas[i]["publicado"] = cuando
