"""ITrazas en memoria (módulo 89): anota qué ha pasado con cada mensaje (por su offset), lo que en producción va
al span."""

from contextlib import contextmanager

from estadisticas.application.ports.i_trazas import ITrazas
from estadisticas.application.shared.dtos.mensaje_input_dto import MensajeInputDTO
from estadisticas.domain.enums.resultado import Resultado
from tests.fakes.traza_fake import TrazaFake


class TrazasFake(ITrazas):
    def __init__(self):
        self.resultados: dict[int, Resultado] = {}

    @contextmanager
    def procesando(self, mensaje: MensajeInputDTO):
        traza = TrazaFake()
        yield traza
        self.resultados[mensaje.offset] = traza.valor
