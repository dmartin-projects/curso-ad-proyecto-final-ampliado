# finanzas/tests/fakes/publicador_eventos_fake.py — IPublicadorEventos en memoria (módulo 87)
from core.application.ports.i_publicador_eventos import IPublicadorEventos


class PublicadorEventosFake(IPublicadorEventos):
    def __init__(self):
        self.publicados: list = []

    def publicar(self, *eventos):
        self.publicados.extend(eventos)
