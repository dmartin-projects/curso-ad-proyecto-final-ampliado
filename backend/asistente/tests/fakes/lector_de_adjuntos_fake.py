# asistente/tests/fakes/lector_de_adjuntos_fake.py — ILectorDeAdjuntos con un texto fijo (módulo 97)
from asistente.application.ports.i_lector_de_adjuntos import ILectorDeAdjuntos


class LectorDeAdjuntosFake(ILectorDeAdjuntos):
    def __init__(self, texto: str = "MERCADONA\nLECHE 1,15\nTOTAL 4,85"):
        self.texto = texto
        self.leidos: list[tuple[int, str]] = []

    def leer(self, contenido, tipo):
        self.leidos.append((len(contenido), tipo))
        return self.texto
