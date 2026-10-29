# asistente/tests/fakes/festivos_fake.py — IFestivos con un calendario fijo (módulo 95, ejercicio 1)
from asistente.application.ports.i_festivos import IFestivos


class FestivosFake(IFestivos):
    def __init__(self, festivos=(), fallo: Exception | None = None):
        self.festivos, self.fallo = tuple(festivos), fallo
        self.pedidos: list[tuple[int, str]] = []

    def del_anio(self, anio, pais):
        self.pedidos.append((anio, pais))
        if self.fallo:
            raise self.fallo
        return tuple(f for f in self.festivos if f.fecha.year == anio)
