# core/tests/fakes/publicador_eventos_fake.py — IPublicadorEventos en memoria (módulos 87 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos


class PublicadorEventosFake(IPublicadorEventos):
    def __init__(self):
        self.publicados: list = []

    def publicar(self, *eventos):
        self.publicados.extend(eventos)

    def de_tipo(self, tipo) -> list:
        return [e for e in self.publicados if isinstance(e, tipo)]
