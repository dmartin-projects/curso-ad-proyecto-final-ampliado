# eventos/tests/fakes/broker_fake.py — IBroker en memoria (módulos 85 y 88)
from eventos.application.ports.i_broker import IBroker
from eventos.domain.exceptions.publicacion_no_confirmada_exception import PublicacionNoConfirmadaException


class BrokerFake(IBroker):
    def __init__(self, falla=False):
        self.enviados, self.falla = [], falla

    def publicar(self, lote):
        if self.falla:
            raise PublicacionNoConfirmadaException("broker caído")
        self.enviados.extend(p.id for p in lote)
