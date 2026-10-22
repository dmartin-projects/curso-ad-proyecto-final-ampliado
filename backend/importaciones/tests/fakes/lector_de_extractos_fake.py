# importaciones/tests/fakes/lector_de_extractos_fake.py — ILectorDeExtractos: devuelve (o lanza) la lectura que se le dé (módulo 88)
from core.tests.fakes.almacen_en_memoria import copia
from importaciones.application.ports.i_lector_de_extractos import ILectorDeExtractos
from importaciones.domain.vo.lectura import Lectura


class LectorDeExtractosFake(ILectorDeExtractos):
    def __init__(self, lectura: Lectura | Exception | None = None):
        self.lectura = lectura if lectura is not None else Lectura()

    def leer(self, contenido, formato):
        if isinstance(self.lectura, Exception):
            raise self.lectura
        return copia(self.lectura)
