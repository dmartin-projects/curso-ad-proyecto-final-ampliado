"""IUnidadDeTrabajo en memoria (módulo 89): la transacción y el savepoint DESHACEN de verdad."""

from contextlib import contextmanager

from estadisticas.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from tests.fakes.memoria import Memoria


class UnidadDeTrabajoFake(IUnidadDeTrabajo):
    def __init__(self, memoria: Memoria):
        self.memoria = memoria
        self.confirmadas = self.deshechas = 0

    def __enter__(self):
        self._foto = self.memoria.foto()
        return self

    def __exit__(self, tipo, *_):
        if tipo is None:
            self.confirmadas += 1
        else:
            self.memoria.restaurar(self._foto)
            self.deshechas += 1

    @contextmanager
    def savepoint(self):
        foto = self.memoria.foto()
        try:
            yield
        except BaseException:
            self.memoria.restaurar(foto)
            raise
