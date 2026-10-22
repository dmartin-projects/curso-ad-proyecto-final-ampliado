"""Las "tablas" de los fakes (módulo 89): lo que la unidad de trabajo copia al empezar y restaura si algo falla."""

import copy
from datetime import datetime

from estadisticas.domain.bo.membresia import Membresia
from estadisticas.domain.bo.movimiento import Movimiento


class Memoria:
    def __init__(self):
        self.movimientos: dict[int, Movimiento] = {}
        self.membresias: dict[tuple[int, int], Membresia] = {}
        self.progreso: dict[tuple[str, int], tuple[int, datetime]] = {}

    def foto(self) -> dict:
        return copy.deepcopy(vars(self))

    def restaurar(self, foto: dict) -> None:
        vars(self).update(foto)
