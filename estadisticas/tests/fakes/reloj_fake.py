"""IReloj con una fecha fija (módulo 89)."""

from datetime import date

from estadisticas.application.ports.i_reloj import IReloj


class RelojFake(IReloj):
    def __init__(self, hoy: date):
        self._hoy = hoy

    def hoy(self) -> date:
        return self._hoy
